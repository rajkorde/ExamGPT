import pickle
from pathlib import Path
from typing import Any, Callable

from examgpt.core.config import settings

logger = settings.get_logger()


class CheckpointService:
    _processed_objects: dict[str, Any]

    @classmethod
    def init(cls, folder: str):
        if not Path(folder).exists():
            logger.warning(
                f"Folder to store checkpoints does not exist and will be created: {folder}"
            )
        full_path = Path(folder) / "checkpoints"
        if not full_path.exists():
            full_path.mkdir()

        cls._checkpoint_file = Path(full_path) / "checkpoint.pkl"
        cls._processed_objects = cls.load_checkpoint() or {}

    @classmethod
    def delete_checkpoint(cls):
        if Path(cls._checkpoint_file).exists():
            Path(cls._checkpoint_file).unlink()
        cls._processed_objects = {}

    @classmethod
    def load_checkpoint(cls):
        if Path(cls._checkpoint_file).exists():
            with Path(cls._checkpoint_file).open("rb") as f:
                return pickle.load(f)
        return None

    @classmethod
    def save_checkpoint(cls, data: object):
        if not cls._checkpoint_file:
            raise RuntimeError(
                "Trying to save checkpoint before initializing checkpoint service."
            )

        with Path(cls._checkpoint_file).open(
            "wb",
        ) as f:
            pickle.dump(data, f)

    @classmethod
    def _search(cls, id: str, scenario: str) -> bool:
        return (
            True
            if id in cls._processed_objects and scenario in cls._processed_objects[id]
            else False
        )

    @classmethod
    def _update(cls, id: str, scenario: str, result: Any) -> None:
        if id not in cls._processed_objects:
            cls._processed_objects[id] = {}
        cls._processed_objects[id][scenario] = result

    @classmethod
    def checkpoint(cls, func: Callable[..., Any]) -> Any:
        def wrapper(instance: Any, *args, **kwargs):  # type: ignore
            """
            IMPORTANT: For checkpointing service to work:
            * The method to be checkpointed must have 2 keyword str arguments.
              One argument "id" that is a unique identifier and another argument
              called "scenario" to checkpoint for.
            * Checkpointing service currently only works for class methods.

            Args:
                instance: Placeholder for self. This assumes that the method to be checkpointed
                is part of a class.

            Returns:
                The result of the operation.
            """

            if not hasattr(CheckpointService, "_processed_objects"):
                raise RuntimeError(
                    "Checkpoint file undefined. Did you forget to run init() method?"
                )

            try:
                id = kwargs.get("id")
                scenario = kwargs.get("scenario")
            except KeyError as e:
                raise RuntimeError(
                    f"Checkpointed service must have 2 keyword string arguments id and scenario: {str(e)}"
                )

            if not id or not scenario:
                raise RuntimeError(
                    "Checkpointed service must have 2 keyword string arguments id and scenario."
                )

            if cls._search(id, scenario):
                logger.info(f"Data already processed. Recovering from checkpoint: {id}")
                result = cls._processed_objects[id][scenario]
            else:
                result = func(instance, *args, **kwargs)
                cls._update(id, scenario, result)
                cls.save_checkpoint(cls._processed_objects)

            return result

        return wrapper
