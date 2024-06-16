import pickle
from pathlib import Path
from typing import Any, Callable

from loguru import logger


# TODO: check print to logging info
# TODO: remove extra calls to Path. Checkpoint file is already of type checkpoint path
class CheckpointService:
    _processed_objects: dict[str, Any]
    # checkpoint_file: Path = Path()

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
        logger.info(f"Checkpoint file: {cls._checkpoint_file}")

        cls._processed_objects = cls.load_checkpoint() or {}

    @classmethod
    def delete_checkpoint(cls):
        print("Deleting checkpoint file")
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
        print("Saving checkpoint file")
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

    # TODO: clean this up so that the name of the id attribute can be pass through
    # decorator definition. Right now, its hardcoded to id.
    @classmethod
    def checkpoint(cls, func: Callable[..., Any]) -> Any:
        # if hasattr(CheckpointService, "checkpoint_file"):
        #     print("I am initialized")
        #     cls.processed_objects = cls.load_checkpoint() or {}
        # else:
        #     print("I am not initialized yet")

        def wrapper(instance: Any, *args, **kwargs):  # type: ignore
            """
            This method that needs to be checkpointed should have this signature.
            This can only checkpoint methods that are part of a class.
            IMPORTANT: The method to be checkpointed must have 2 keyword str arguments
            for checkpoint to work. One argument "id" that is a unique identifier
            and another argument called "scenario" to checkpoint for.

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

            id = kwargs.get("id")
            scenario = kwargs.get("scenario")

            if not id or not scenario:
                raise RuntimeError(
                    "Checkpointed service must have 2 keyword string arguments id and scenario."
                )

            if cls._search(id, scenario):
                print(f"Data already processed: {id}")
                result = cls._processed_objects[id][scenario]
            else:
                result = func(instance, *args, **kwargs)
                cls._update(id, scenario, result)
                cls.save_checkpoint(cls._processed_objects)

            print(f"Result inside wrapper: {result}")
            print(cls._processed_objects.keys())
            return result

        return wrapper
