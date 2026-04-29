from __future__ import annotations
from typing import TYPE_CHECKING
from .converter import node_content_to_html
from html import escape
if TYPE_CHECKING:
    from pubkit.models import (
        Publication, Section, Paragraph, Figure, Table
    )

MAX_HEADING_LEVEL = 6

class HTMLRenderer:
    def __init__(
            self,
            figures: dict[str, Figure] | None = None,
            tables: dict[str, Table] | None = None,
    ):
        self.figures = figures or {}
        self.tables = tables or {}

    def render_reference(
            self,
            refid: str
    ):
        if refid in self.figures:
            return node_content_to_html([self.figures[refid]])
        
        if refid in self.tables:
            return node_content_to_html([self.tables[refid]])
        
        return ""

    def render_paragraph(
            self,
            paragraph: Paragraph,
            rendered_refs: set[str] | None = None
    ):
        if rendered_refs is None:
            rendered_refs = set()
        
        parts = []
        
        content_html = node_content_to_html(paragraph.content)
        parts.append(content_html)
        
        for ref in paragraph.references:
            refid = ref.refid
            if refid not in rendered_refs:
                ref_html = self.render_reference(refid)
                if ref_html:
                    parts.append(ref_html)
                    rendered_refs.add(refid)
        
        inner_html = "\n".join(parts)

        id_attr = f' id="{escape(paragraph.id)}"' if paragraph.id else ""
        return f'<div{id_attr}>\n{inner_html}\n</div>'
    
    def render_section(
            self,
            section: Section,
            heading_level: int = 2,
            rendered_refs: set[str] | None = None
    ):
        if rendered_refs is None:
            rendered_refs = set()
        
        parts = []
        
        # Heading
        heading_parts = []
        
        if section.label:
            label_html = node_content_to_html(section.label)
            heading_parts.append(f'<span class="section-label">{label_html}</span>')
        
        if section.title:
            title_html = node_content_to_html(section.title)
            heading_parts.append(f'<span class="section-title">{title_html}</span>')
        
        if heading_parts:
            level = min(heading_level, MAX_HEADING_LEVEL)
            heading_html = " ".join(heading_parts)
            parts.append(f'<h{level}>{heading_html}</h{level}>')
        
        # Content (Paragraph veya nested Section)
        for item in section.content:
            if item.type == "Paragraph":
                parts.append(self.render_paragraph(item, rendered_refs))
            elif item.type == "Section":
                parts.append(self.render_section(item, heading_level + 1, rendered_refs))

        inner_html = "\n".join(parts)
        id_attr = f' id="{escape(section.id)}"' if section.id else ""

        return f'<section{id_attr}>\n{inner_html}\n</section>'

    def render_section_heading(
            self,
            section: Section,
            include_label: bool = True
    ):
        text = ""
        if include_label and section.label:
            text += node_content_to_html(section.label) + " "
            
        if section.title:
            text += node_content_to_html(section.title)

        return text

    def render_publication(
            self,
            publication: Publication,
            include_metadata: bool = True
    ):
        parts = []
        rendered_refs: set[str] = set()
        
        section_heading_level = 1
        if include_metadata:
            section_heading_level = 2
            header_parts = []

            # Title (H1)
            header_parts.append(f'<h1 class="publication-title">{escape(publication.title)}</h1>')

            # Publication info (source_title ve publication_date)
            pub_info_parts = []
            if publication.source_title:
                pub_info_parts.append(f'<span class="source-title">{escape(publication.source_title)}</span>')
            if publication.publication_date:
                pub_info_parts.append(f'<span class="publication-date">{publication.publication_date.strftime("%Y-%m-%d")}</span>')
            
            if pub_info_parts:
                header_parts.append(f'<p class="publication-info">{" · ".join(pub_info_parts)}</p>')
            
            header_html = "\n".join(header_parts)
            parts.append(f'<header class="publication-header">\n{header_html}\n</header>')
        
        # Sections
        for section in publication.sections:
            parts.append(self.render_section(section, section_heading_level, rendered_refs))

        inner_html = "\n".join(parts)
        id_attr = f' id="{escape(publication.id)}"' if publication.id else ""
        return f'<article{id_attr} class="publication">\n{inner_html}\n</article>'
        

    @classmethod
    def from_publication(
            cls,
            publication: Publication
    ) -> HTMLRenderer:
        return cls(
            figures=publication.figures,
            tables=publication.tables,
        )