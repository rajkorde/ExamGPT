import shutil
from pathlib import Path
from typing import Any, Optional

import typer
from rich import print
from tenacity import retry, stop_after_attempt
from typing_extensions import Annotated

from examgpt.ai.aimodel import AIModel
from examgpt.ai.model_providers.openai import OpenAIProvider
from examgpt.core.config import settings
from examgpt.core.exam import Exam
from examgpt.core.question import QACollection
from examgpt.sources.chunkers.pdf_chunker import SimplePDFChunker
from examgpt.sources.filetypes.base import Source, SourceState
from examgpt.sources.filetypes.pdf import PDFFile
from examgpt.storage.files import FileStorage
from examgpt.utils.checkpoint import CheckpointService

__version__ = "0.1.0"

app = typer.Typer(no_args_is_help=True, add_completion=False)
state = {"verbose": False, "debug": False}


def version_callback(value: bool):
    if value:
        print(f"ExamGPT CLI Version: {__version__}")
        raise typer.Exit()


def debug_log(text: Any):
    if state["debug"]:
        print(str(text))


def log(text: Any):
    print(str(text))


@app.command()
def cleanup(
    exam_code: Annotated[
        str, typer.Option(help="Exam code of the exam", show_default=False)
    ],
):
    """
    Clean up all the resources for an exam
    """
    destination_folder = Path(settings.temp_folder) / exam_code
    if destination_folder.exists():
        shutil.rmtree(
            str(destination_folder),
        )
    log("Cleanup complete.")


@retry(stop=stop_after_attempt(10))
def get_qa_collection(
    source: Source, exam_id: str, exam_name: str, model: AIModel
) -> QACollection | None:
    qa_collection = source.get_qa_collection(exam_id, exam_name, model)
    return qa_collection


@app.command()
def generate(
    name: Annotated[str, typer.Option(help="Name of the exam", show_default=False)],
    location: Annotated[
        str,
        typer.Option(
            help="Location of the file with study material", show_default=False
        ),
    ],
    final_state: SourceState = typer.Option(
        default=SourceState.INIT.value,  # This needs to be string due to bug in typer package
        help="Final state of the execution",
        case_sensitive=False,
    ),
    debug: Annotated[
        bool, typer.Option(help="Run app without saving any information to the backend")
    ] = True,
    verbose: Annotated[bool, typer.Option(help="Enable verbose output")] = True,
    version: Annotated[
        Optional[bool],
        typer.Option("--version", help="Show CLI version", callback=version_callback),
    ] = None,
    code: Annotated[
        Optional[str],
        typer.Option(help="Specify exam code if you want to reuse a code"),
    ] = None,
):
    """
    Create an exam by specifying the exam name and location of the study material.
    Once the processing of study material is complete, you will be provided with an exam code that you can use in telegram.
    """

    # logger.info(f"{name=}")
    # logger.info(f"{location=}")
    # logger.info(f"{final_state=}")
    # logger.info(f"{debug=}")
    # logger.info(f"{verbose=}")
    # logger.info(f"{version=}")
    # logger.info(f"{code=}")

    # verify location
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
    state["debug"] = debug

    # Init
    log("Initializing Exam...")
    chunker = SimplePDFChunker(chunk_size=2500)
    pdf = PDFFile(location=location, chunker=chunker)
    debug_log(pdf.to_dict())
    exam = Exam(name=name, sources=[pdf])
    debug_log(exam)

    print(
        f"Your exam code is [bold green]{exam.exam_id}[/bold green]. Please use this code to start practicing in Telegram app."
    )

    # Copy
    log("Copying content...")
    destination_folder = str(Path(settings.temp_folder) / exam.exam_id)
    storage = FileStorage(folder=destination_folder)
    storage.copy(sources=exam.sources)
    debug_log(f"New content location: {pdf.location}")

    # Chunk
    log("Chunking content...")
    pdf.chunk()
    storage.save_to_json(data=exam.to_dict(), filename="chunks.json")
    log("Chunking complete")

    # Generate QA
    log(
        "Generating flash cards and multiple choice questions. This can take few minutes..."
    )
    pdf.limit_chunks()  # for testing only
    model = AIModel(model_provider=OpenAIProvider())
    CheckpointService.init(destination_folder)
    qa_collection = get_qa_collection(pdf, exam.exam_id, name, model)
    CheckpointService.delete_checkpoint()
    storage.save_to_json(data=qa_collection.to_dict(), filename="answers.json")
    log("Generation complete.")


if __name__ == "__main__":
    app()
    typer.Typer()
