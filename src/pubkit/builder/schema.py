from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class SectionSchema:
    id: str
    depth: int
    render_order: int
    render_order_start: int
    render_order_end: int
    parent_section_id: str | None = None
    label: list[dict[str, Any]] | None = None
    title: list[dict[str, Any]] | None = None


@dataclass(frozen=True)
class ParagraphSchema:
    id: str
    render_order: int
    content: list[dict[str, Any]]
    referenced_figure_ids: list[str] | None = None
    referenced_table_ids: list[str] | None = None
    referenced_other_ids: list[str] | None = None


@dataclass(frozen=True)
class FigureSchema:
    figure_id: str
    content: dict[str, Any]


@dataclass(frozen=True)
class TableSchema:
    table_id: str
    content: dict[str, Any]


@dataclass(frozen=True)
class PublicationSchema:
    id: str
    title: str
    doi: str | None
    authors: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    publication_date: Any = None
    publication_type: str | None = None
    source_title: str | None = None
    sections: list[SectionSchema] = field(default_factory=list)
    paragraphs: list[ParagraphSchema] = field(default_factory=list)
    figures: list[FigureSchema] = field(default_factory=list)
    tables: list[TableSchema] = field(default_factory=list)