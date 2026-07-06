import dataclasses
import enum


@dataclasses.dataclass
class ReviewRequest:
    diff: str
    title: str
    description: str


class CommentSide(enum.Enum):
    Left = 1
    Right = 2


@dataclasses.dataclass
class LineComment:
    comment: str
    file: str
    line: int
    side: CommentSide


@dataclasses.dataclass
class ReviewResponse:
    summary_comments: list[str]
    line_comments: list[LineComment]
