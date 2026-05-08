from .record import (
    PublicationRecord,
    SectionRecord,
    ParagraphRecord,
    TableRecord,
    FigureRecord
)

from pubkit.models import (
    Publication,
    Section,
    Paragraph,
    Figure,
    Table,
    Reference
)

from dataclasses import dataclass
import bisect

@dataclass(frozen=True, kw_only=True, slots=True)
class _Node:
    start: int
    end: int
    item: Section | Paragraph

def rebuild_figure(figure_record: FigureRecord) -> Figure:
    return Figure.model_validate(figure_record.content)

def rebuild_table(table_record: TableRecord) -> Table:
    return Table.model_validate(table_record.content)

def rebuild_paragraph(paragraph_record: ParagraphRecord) -> Paragraph:
    references: list[Reference] = []

    for reference_record in paragraph_record.reference_records:
        references.append(
            Reference(refid=reference_record.refid, ref_type=reference_record.type) # !!! Check this ref_type !!!
        )

    return Paragraph(
        id=paragraph_record.id,
        content=paragraph_record.content,
        references=references
    )

def _rebuild_section_depr1(
        target_section_id: str,
        paragraph_records: list[ParagraphRecord],
        section_records: list[SectionRecord],
) -> Section:
    paragraph_records.sort(key=lambda x: x.position)
    section_records.sort(key=lambda x: x.start_position)

    target_sec_rec: SectionRecord | None = None
    for sec_rec in section_records:
        if sec_rec.id == target_section_id:
            target_sec_rec = sec_rec
            break

    if target_sec_rec is None:
        raise ValueError(f"Target Section id:({target_section_id}) not found in Section Records")
    
    start = target_sec_rec.start_position
    end = target_sec_rec.end_position

    sub_sec_recs: list[SectionRecord] = []
    first_sub_sec_start = end
    for sec_rec in section_records:
        if start < sec_rec.start_position <= end:
            sub_sec_recs.append(sec_rec)
            first_sub_sec_start = min(first_sub_sec_start, sec_rec.start_position)
    
    sub_sec_para_recs: list[ParagraphRecord] = []
    current_para_recs: list[ParagraphRecord] = []
    for para_rec in paragraph_records:
        if not (start < para_rec.position <= end):
            continue
        
        # belongs only target section, not its sub sections 
        if para_rec.position <= first_sub_sec_start:
            current_para_recs.append(para_rec)
        # both target section and its sub sections
        else:
            sub_sec_para_recs.append(para_rec)
    
    content: list[Paragraph | Section] = []
    content.extend([rebuild_paragraph(para_rec) for para_rec in current_para_recs])

    content.extend(
        [
            rebuild_section(sec_rec.id, sub_sec_para_recs, sub_sec_recs) 
            for sec_rec in sub_sec_recs if sec_rec.depth == target_sec_rec.depth + 1
            # only 1 level deep sections
        ]
    )
    
    return Section(
        id=target_sec_rec.id,
        label=target_sec_rec.label,
        title=target_sec_rec.title,
        content=content,
    )

def rebuild_section(
        target_section_id: str,
        paragraph_records: list[ParagraphRecord],
        section_records: list[SectionRecord],
) -> Section:
    nodes: list[_Node] = []
    for record in (paragraph_records + section_records):
        if isinstance(record, ParagraphRecord):
            nodes.append(
                _Node(
                    start=record.position,
                    end=record.position,
                    item=rebuild_paragraph(record)
                )
            )
        elif isinstance(record, SectionRecord):
            nodes.append(
                _Node(
                    start=record.start_position,
                    end=record.end_position,
                    item=Section(
                        id=record.id,
                        label=record.label,
                        title=record.title,
                        content=[],
                    )
                )
            )
        else:
            raise TypeError("Only ParagraphRecord or SectionRecord allowed")
    nodes.sort(key=lambda x: x.start)

    root_node: _Node | None = None
    for node in nodes:
        if not isinstance(node.item, Section):
            continue
        if node.item.id == target_section_id:
            root_node = node
            break

    if root_node is None:
        raise ValueError(f"Target Section id:({target_section_id}) not found in Sections")

    start = root_node.start
    end = root_node.end

    start_idx = bisect.bisect_left(nodes, start, key=lambda x: x.start)
    end_idx = bisect.bisect_right(nodes, end, key=lambda x: x.start)
    included_nodes = nodes[start_idx:end_idx]

    if root_node != included_nodes[0]:
        raise ValueError("Root node is not the first included node!")
    

    stack: list[_Node] = [root_node]
    for node in included_nodes[1:]:
        while not (stack[-1].start < node.start <= stack[-1].end):
            stack.pop()

        parent = stack[-1]
        if not isinstance(parent.item, Section):
            raise TypeError("Stack can only contains Section objects")
        
        parent.item.content.append(node.item)

        if isinstance(node.item, Section):
            stack.append(node)

    return root_node.item


def rebuild_publication(
        publication_record: PublicationRecord
) -> Publication:
    sections: list[Section] = []

    figure_records = publication_record.figures
    table_records = publication_record.tables
    paragraph_records = publication_record.paragraphs
    section_records = publication_record.sections

    depths = [sec_rec.depth for sec_rec in section_records]
    min_depth = min(depths) if depths else -1

    root_sec_recs: list[SectionRecord] = []
    for sec_rec in section_records:
        if sec_rec.id is None:
            raise ValueError("Section ID cannot be None!")
        
        if sec_rec.parent_section_id is None and sec_rec.depth == min_depth:
            root_sec_recs.append(sec_rec)

    root_sec_recs.sort(key=lambda x: x.start_position)

    for sec_rec in root_sec_recs:
        section = rebuild_section(
            target_section_id=sec_rec.id,
            paragraph_records=paragraph_records,
            section_records=section_records,
        )
        sections.append(section)
    
    
    figures: dict[str, Figure] = {}
    for fig_rec in figure_records:
        figure = rebuild_figure(fig_rec)
        figures[figure.id] = figure

    tables: dict[str, Table] = {}
    for tbl_rec in table_records:
        table = rebuild_table(tbl_rec)
        tables[table.id] = table


    return Publication(
        id = publication_record.id,
        title = publication_record.title,
        doi = publication_record.doi,
        authors = publication_record.authors,
        keywords = publication_record.keywords,
        publication_date = publication_record.publication_date,
        publication_type = publication_record.publication_type,
        publication_rank = publication_record.publication_rank,
        source_title = publication_record.source_title,
        sections=sections,
        figures=figures,
        tables=tables
    )