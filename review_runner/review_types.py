import dataclasses

@dataclasses.dataclass
class ReviewRequest:
  diff: str
  title: str
  description: str

@dataclasses.dataclass
class LineComment:
  comment: str
  file: str
  line: int

@dataclasses.dataclass
class ReviewResponse:
  summary_comments: list[str]
  line_comments: list[LineComment]