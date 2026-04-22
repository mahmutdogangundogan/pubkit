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

def build_figure(figure_record: FigureRecord) -> Figure:
    return Figure.model_validate(figure_record.content)

def build_table(table_record: TableRecord) -> Table:
    return Table.model_validate(table_record.content)

def build_paragraph(paragraph_record: ParagraphRecord) -> Paragraph:
    references: list[Reference] = []

    for _id in paragraph_record.referenced_figure_ids:
        references.append(
            Reference(refid=_id, ref_type="figure") # !!! Check this ref_type !!!
        )
    for _id in paragraph_record.referenced_table_ids:
        references.append(
            Reference(refid=_id, ref_type="table") # !!! Check this ref_type !!!
        )
    for _id in paragraph_record.referenced_other_ids:
        references.append(
            Reference(refid=_id, ref_type="other") # !!! Check this ref_type !!!
        )

    return Paragraph(
        id=paragraph_record.id,
        content=paragraph_record.content,
        references=references
    )

def build_section(
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
    content.extend([build_paragraph(para_rec) for para_rec in current_para_recs])

    content.extend(
        [
            build_section(sec_rec.id, sub_sec_para_recs, sub_sec_recs) 
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



def build_publication(
        figure_records: list[FigureRecord],
        table_records: list[TableRecord],
        paragraph_records: list[ParagraphRecord],
        section_records: list[SectionRecord],
        publication_record: PublicationRecord
) -> Publication:
    sections: list[Section] = []

    if not section_records:
        raise ValueError("Section records cannot be empty")

    depths = [sec_rec.depth for sec_rec in section_records]
    min_depth = min(depths)

    root_sec_recs: list[SectionRecord] = []
    for sec_rec in section_records:
        if sec_rec.id is None:
            raise ValueError("Section ID cannot be None!")
        
        if sec_rec.parent_section_id is None and sec_rec.depth == min_depth:
            root_sec_recs.append(sec_rec)

    root_sec_recs.sort(key=lambda x: x.start_position)

    for sec_rec in root_sec_recs:
        section = build_section(
            target_section_id=sec_rec.id,
            paragraph_records=paragraph_records,
            section_records=section_records,
        )
        sections.append(section)
    
    
    figures: dict[str, Figure] = {}
    for fig_rec in figure_records:
        figure = build_figure(fig_rec)
        figures[figure.id] = figure

    tables: dict[str, Table] = {}
    for tbl_rec in table_records:
        table = build_table(tbl_rec)
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