import shutil
from pathlib import Path
from typing import Optional

import typer
from rich import print
from typing_extensions import Annotated

from examgpt.ai.aimodel import AIModel

# from examgpt.ai.base import ModelConfig
# from examgpt.ai.constants import ModelFamily, ModelName
from examgpt.ai.model_providers.openai import OpenAIProvider
from examgpt.core.config import settings
from examgpt.frontend.cli_helper import CLIHelper
from examgpt.sources.chunkers.pdf_chunker import SimplePDFChunker
from examgpt.storage.files import FileStorage

__version__ = "0.1.5"

app = typer.Typer(no_args_is_help=True, add_completion=False)
state = {"verbose": False, "debug": False}


def version_callback(value: bool):
    if value:
        print(f"ExamGPT CLI Version: {__version__}")
        raise typer.Exit()


@app.callback()
def version(
    version: Annotated[
        Optional[bool],
        typer.Option("--version", help="Show CLI version", callback=version_callback),
    ] = None,
):
    return


@app.command()
def cleanup(
    code: Annotated[
        str, typer.Option(help="Exam code of the exam", show_default=False)
    ],
):
    """
    Clean up all the resources for an exam
    """
    destination_folder = Path(settings.temp_folder) / code
    if destination_folder.exists():
        shutil.rmtree(
            str(destination_folder),
        )
        print(f"Cleanup complete for {code}.")
    else:
        print(f"[bold red]Error:[/bold red] No content found for {code}.")


def validate_limit(limit: int) -> int:
    if limit < 0:
        raise typer.BadParameter("Limit must be greater than zero.")
    return limit


@app.command()
def generate(
    name: Annotated[str, typer.Option(help="Name of the exam", show_default=False)],
    location: Annotated[
        str,
        typer.Option(
            help="Location of the file with study material", show_default=False
        ),
    ],
    limit: Annotated[
        Optional[int],
        typer.Option(
            help="Limit the number of chunks to use for generation",
            callback=validate_limit,
        ),
    ] = 0,
    debug: Annotated[
        bool, typer.Option(help="Run app without saving any information to the backend")
    ] = False,
    verbose: Annotated[
        bool, typer.Option(help="Enable verbose debugging output")
    ] = False,
    code: Annotated[
        Optional[str],
        typer.Option(help="Specify exam code if you want to reuse a code"),
    ] = None,
):
    """
    Create an exam by specifying the exam name and location of the study material.
    Once the processing of study material is complete, you will be provided with an exam code that you can use in telegram.
    """

    # Verify location
    if not Path(location).exists():
        print(f"[bold red]Error:[/bold red] File not found: {location}")
        typer.Exit(-1)
        return

    if str(Path(location).suffix).lower() != ".pdf":
        print(
            f"[bold red]Error:[/bold red] Only pdf files supported currently: {location}"
        )
        typer.Exit(-1)
        return
    state["verbose"] = verbose

    log_level = "debug" if verbose else "error"
    settings.configure_logging(log_level)

    cli_helper = CLIHelper(name, location, code) if code else CLIHelper(name, location)

    # Init
    print("Initializing Exam...")
    code = cli_helper.initialize()
    print(
        f"Your exam code is [bold green]{code}[/bold green]. Please use this code to start practicing in Telegram app."
    )

    # Copy
    print("Copying content...")
    destination_folder = str(Path(settings.temp_folder) / code)
    cli_helper.set_storage(FileStorage(folder=destination_folder))
    cli_helper.copy()

    # Chunk
    print("Chunking content...")
    cli_helper.chunk(SimplePDFChunker(chunk_size=2500))
    print("Chunking complete.")

    # Generate QA
    print(
        "Generating flash cards and multiple choice questions. This can take few minutes..."
    )

    model = AIModel(OpenAIProvider())
    # model = AIModel(
    #     model_provider=OpenAIProvider(
    #         ModelConfig(ModelFamily.OPENAI, ModelName.GPT4O, cost_ppm_token=500)
    #     )
    # )
    cli_helper.generate_qa(model, limit)
    print("Generation complete.")


if __name__ == "__main__":
    app()
