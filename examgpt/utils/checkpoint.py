import pickle
from pathlib import Path
from typing import Optional

from examgpt.core.exceptions import UndefinedCheckpointPath


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
