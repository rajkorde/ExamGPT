import pickle
from pathlib import Path
from typing import Any, Optional

from loguru import logger

from examgpt.core.exceptions import UndefinedCheckpointPath

# class CheckpointService:
#     def __init__(self, checkpoint_file: str = "checkpoint.pkl"):
#         self.checkpoint_file = Path(checkpoint_file)

#     def save_checkpoint(self, data):
#         with self.checkpoint_file.open("wb") as f:
#             pickle.dump(data, f)

#     def load_checkpoint(self):
#         if self.checkpoint_file.exists():
#             with self.checkpoint_file.open("rb") as f:
#                 return pickle.load(f)
#         return None

#     def checkpoint(self, func):
#         def wrapper(*args, **kwargs):
#             checkpoint_data = self.load_checkpoint()
#             if checkpoint_data:
#                 logger.info("Resuming from last checkpoint...")
#                 return checkpoint_data
#             result = func(*args, **args)
#             self.save_checkpoint(result)
#             return result

#         return wrapper


class CheckpointService:
    checkpoint_file: Optional[Path] = None

    def __init__(self, folder: str):
        full_path = Path(folder) / "checkpoints"

        if not full_path.exists():
            full_path.mkdir()

        CheckpointService.checkpoint_file = Path(full_path) / "checkpoint.pkl"

    @classmethod
    def save_checkpoint(cls, data: object):
        if CheckpointService.checkpoint_file is None:
            raise UndefinedCheckpointPath()
        with CheckpointService.checkpoint_file.open(
            "wb",
        ) as f:
            pickle.dump(data, f)

    @classmethod
    def load_checkpoint(cls):
        if CheckpointService.checkpoint_file.exists():
            with CheckpointService.checkpoint_file.open("rb") as f:
                return pickle.load(f)
        return None
