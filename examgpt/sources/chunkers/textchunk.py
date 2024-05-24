from dataclasses import asdict, dataclass


@dataclass
class TextChunk:
    id: str
    text: str
    page_number: int | None

    def to_dict(self):
        return asdict(self)
