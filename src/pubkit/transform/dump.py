from __future__ import annotations

from pubkit import Paragraph, Section, Publication
from .record import (
    PublicationRecord,
    SectionRecord,
    ParagraphRecord,
    TableRecord,
    FigureRecord
)

from dataclasses import dataclass

@dataclass(slots=True)
class _Node:
    section: Section
    child_idx: int
    start_pos: int
    

def dump_section(
        root_section: Section,
        position: int = 1,
        start_depth: int = 0,
        parent_section_id: str | None = None,
) -> tuple[list[ParagraphRecord], list[SectionRecord]]:
    paragraph_records: list[ParagraphRecord] = []
    section_records: list[SectionRecord] = []

    # Set the initial Node
    stack: list[_Node] = [_Node(root_section, 0, position)]
    position += 1

    while stack:
        node = stack[-1]
        
        if node.child_idx < len(node.section.content):
            item = node.section.content[node.child_idx]

            # since this child (item) visited, increase the child_idx for current node
            stack[-1].child_idx += 1

            if isinstance(item, Paragraph):
                paragraph_records.append(
                    ParagraphRecord(
                        id=item.id,
                        position=position,
                        content=item.content,
                    )
                )
                position += 1

            elif isinstance(item, Section):
                # add next depth section to stack
                stack.append(_Node(item, 0, position))
                position += 1

        else:
            # if it traverses all children, then we can pop this Section
            # and also determine the end_position and depth
            start = node.start_pos
            end = position - 1

            parent_id = (
                stack[-2].section.id
                if len(stack) > 1
                else parent_section_id
            )
            depth = len(stack) - 1 + start_depth

            section_records.append(
                SectionRecord(
                    id=node.section.id,
                    depth=depth,
                    parent_section_id=parent_id,
                    start_position=start,
                    end_position=end,
                    label=node.section.label,
                    title=node.section.title,
                )
            )

            stack.pop()

    paragraph_records.sort(key=lambda x: x.position)
    section_records.sort(key=lambda x: x.start_position)

    return paragraph_records, section_records

def dump_publication(publication: Publication) -> PublicationRecord:
    paragraphs, sections = dump_section(publication.sections[0])
    figures: list[FigureRecord] = []
    tables: list[TableRecord] = []

    return PublicationRecord(
        id = str(publication.id) if publication.id else None,
        title = publication.title,
        doi = publication.doi, # opsiyonel bu?
        authors = publication.authors,
        keywords = publication.keywords,
        publication_date = publication.publication_date,
        publication_type = publication.publication_type,
        publication_rank = None,
        source_title = publication.source_title,
        sections = sections,
        paragraphs = paragraphs,
        figures = figures,
        tables = tables,
    )