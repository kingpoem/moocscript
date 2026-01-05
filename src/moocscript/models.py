"""Data models for MOOC API responses."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class Status:
    """API response status."""
    code: int
    message: str


@dataclass
class Result:
    """Generic API response wrapper.
    
    Attributes:
        status: Response status with code and message
        results: Response data (can be any type)
    """
    status: Status
    results: Any
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Result":
        """Create Result from dictionary response."""
        status_data = data.get("status", {})
        status = Status(
            code=status_data.get("code", -1),
            message=status_data.get("message", "")
        )
        return cls(status=status, results=data.get("results"))


@dataclass
class Pagination:
    """Pagination information."""
    totlePageCount: int  # Note: keeping original typo from API


@dataclass
class SchoolPanel:
    """School information."""
    name: str


@dataclass
class TermPanel:
    """Term information."""
    id: int


@dataclass
class Course:
    """Course information."""
    id: int
    currentTermId: int
    name: str
    imgUrl: str
    fromCourseId: int
    schoolPanel: SchoolPanel
    termPanel: TermPanel


@dataclass
class Homework:
    """Homework information."""
    contentId: int
    name: str
    contentType: Optional[int] = None


@dataclass
class Quiz:
    """Quiz information."""
    contentId: int
    name: str
    contentType: Optional[int] = None


@dataclass
class Exam:
    """Exam information."""
    objectTestVo: Optional[Dict[str, Any]] = None
    subjectTestVo: Optional[Dict[str, Any]] = None


@dataclass
class Chapter:
    """Chapter information."""
    id: int
    name: str
    homeworks: List[Homework]
    quizs: List[Quiz]
    exam: Optional[Exam] = None


@dataclass
class OptionDto:
    """Multiple choice option."""
    id: str
    answer: bool
    content: str


@dataclass
class ObjectiveQ:
    """Objective question (multiple choice, etc.)."""
    id: int
    type: int
    title: str
    optionDtos: List[OptionDto]
    stdAnswer: str


@dataclass
class JudgeDto:
    """Subjective question judge criteria."""
    id: int
    msg: str


@dataclass
class SubjectiveQ:
    """Subjective question."""
    id: int
    type: int
    title: str
    judgeDtos: List[JudgeDto]


@dataclass
class MocPaperDto:
    """Paper/Test data structure."""
    objectiveQList: List[ObjectiveQ]
    subjectiveQList: List[SubjectiveQ]
