from dataclasses import dataclass, field
from typing import Any
from datetime import date

@dataclass(frozen=True, kw_only=True, slots=True)
class SectionRecord:
    id: str
    depth: int
    parent_section_id: str | None = field(default=None)
    start_position: int
    end_position: int
    label: list[dict[str, Any]] = field(default_factory=list)
    title: list[dict[str, Any]] = field(default_factory=list)

@dataclass(frozen=True, kw_only=True, slots=True)
class ReferenceRecord:
    refid: str
    type: str


@dataclass(frozen=True, kw_only=True, slots=True)
class ParagraphRecord:
    id: str | None = None
    position: int
    content: list[dict[str, Any]]
    reference_records: list[ReferenceRecord] = field(default_factory=list)


@dataclass(frozen=True, kw_only=True, slots=True)
class FigureRecord:
    id: str
    content: dict[str, Any]


@dataclass(frozen=True, kw_only=True, slots=True)
class TableRecord:
    id: str
    content: dict[str, Any]


@dataclass(frozen=True, kw_only=True, slots=True)
class PublicationRecord:
    id: str | None = field(default=None)
    title: str
    doi: str | None = field(default=None)
    authors: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    publication_date: date | None = field(default=None)
    publication_type: str
    publication_rank: str | None = field(default=None)
    subject_areas: list
    source_title: str | None = field(default=None)
    sections: list[SectionRecord] = field(default_factory=list)
    paragraphs: list[ParagraphRecord] = field(default_factory=list)
    figures: list[FigureRecord] = field(default_factory=list)
    tables: list[TableRecord] = field(default_factory=list)
    extra: dict = field(default_factory=dict)