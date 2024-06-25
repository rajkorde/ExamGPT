from typing import Optional

import typer
from loguru import logger
from typing_extensions import Annotated

from examgpt.sources.filetypes.base import SourceState

__version__ = "0.1.0"

app = typer.Typer(no_args_is_help=True)


def version_callback(value: bool):
    if value:
        print(f"ExamGPT CLI Version: {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
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
    verbose: Annotated[bool, typer.Option(help="Enable verbose output")] = False,
    version: Annotated[
        Optional[bool], typer.Option("--version", callback=version_callback)
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

    logger.info(f"{name=}")
    logger.info(f"{location=}")
    logger.info(f"{final_state=}")
    logger.info(f"{debug=}")
    logger.info(f"{verbose=}")
    logger.info(f"{version=}")
    logger.info(f"{code=}")


if __name__ == "__main__":
    app()
    typer.Typer()
