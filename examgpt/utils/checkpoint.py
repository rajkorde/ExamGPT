import pickle
from pathlib import Path
from typing import Any, Callable

from loguru import logger


# TODO: check print to logging info
# TODO: remove extra calls to Path. Checkpoint file is already of type checkpoint path
class CheckpointService:
    processed_objects: dict[str, Any]
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

        cls.checkpoint_file = Path(full_path) / "checkpoint.pkl"
        logger.info(f"Checkpoint file: {cls.checkpoint_file}")

        cls.processed_objects = cls.load_checkpoint() or {}

    @classmethod
    def delete_checkpoint(cls):
        print("Deleting checkpoint file")
        if Path(cls.checkpoint_file).exists():
            Path(cls.checkpoint_file).unlink()
        cls.processed_objects = {}

    @classmethod
    def load_checkpoint(cls):
        # if cls.checkpoint_file == Path():
        #     raise RuntimeError(
        #         "Checkpoint file undefined. Did you forget to run init() method?"
        #     )
        if Path(cls.checkpoint_file).exists():
            with Path(cls.checkpoint_file).open("rb") as f:
                return pickle.load(f)
        return None

    @classmethod
    def save_checkpoint(cls, data: object):
        print("Saving checkpoint file")
        if not cls.checkpoint_file:
            raise RuntimeError(
                "Trying to save checkpoint before initializing checkpoint service."
            )

        with Path(cls.checkpoint_file).open(
            "wb",
        ) as f:
            pickle.dump(data, f)

    # TODO: clean this up so that the name of the id attribute can be pass through
    # decorator definition. Right now, its hardcoded to id.
    @classmethod
    def checkpoint(cls, func: Callable[..., Any]) -> Any:
        # if hasattr(CheckpointService, "checkpoint_file"):
        #     print("I am initialized")
        #     cls.processed_objects = cls.load_checkpoint() or {}
        # else:
        #     print("I am not initialized yet")

        def wrapper(instance: Any, id: str, *args, **kwargs):  # type: ignore
            """
            This method that needs to be checkpointed should have this signature.
            This can only checkpoint methods that are part of a class.
            IMPORTANT: The first parameter of any method that needs to be checkpointed
            must have a unqiue id it gets after the first parameter (after self)

            Args:
                instance: This assumes that the method to be checkpointed is part of a class.
                id: unique identifier for this object. Used for indexing in the checkpoint file

            Returns:
                The result of the operation.
            """

            if id in cls.processed_objects:
                print(f"Data already processed: {id}")
                result = cls.processed_objects[id]
            else:
                result = func(instance, id, *args, **kwargs)
                cls.processed_objects[id] = result
                cls.save_checkpoint(cls.processed_objects)

            print(f"Result inside wrapper: {result}")
            print(cls.processed_objects.keys())
            return result

        return wrapper
