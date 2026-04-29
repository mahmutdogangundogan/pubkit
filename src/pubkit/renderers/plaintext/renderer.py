from __future__ import annotations
from typing import TYPE_CHECKING
from .converter import node_content_to_text, normalize_whitespace
if TYPE_CHECKING:
    from pubkit.models import (
        Publication, Section, Paragraph, Figure, Table
    )

MAX_HEADING_LEVEL = 6

class PlaintextRenderer:
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
            return node_content_to_text([self.figures[refid]])
        
        if refid in self.tables:
            return node_content_to_text([self.tables[refid]])
        
        return ""

    def render_paragraph(
            self,
            paragraph: Paragraph,
            rendered_refs: set[str] | None = None
    ):
        if rendered_refs is None:
            rendered_refs = set()
        
        parts = []
        
        content_text = node_content_to_text(paragraph.content)
        if content_text:
            parts.append(content_text)
        
        for ref in paragraph.references:
            refid = ref.refid
            if refid not in rendered_refs:
                ref_text = self.render_reference(refid)
                if ref_text:
                    parts.append(ref_text)
                    rendered_refs.add(refid)
        text = " ".join(parts)
        return normalize_whitespace(text)
    
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
            heading_parts.append(node_content_to_text(section.label))
        
        if section.title:
            heading_parts.append(node_content_to_text(section.title))
        
        if heading_parts:
            heading = " ".join(heading_parts)
            parts.append(heading)
        
        # Content (Paragraph veya nested Section)
        for item in section.content:
            if item.type == "Paragraph":
                parts.append(self.render_paragraph(item, rendered_refs))
            elif item.type == "Section":
                parts.append(self.render_section(item, heading_level + 1, rendered_refs))
        
        text = " ".join(parts)
        return normalize_whitespace(text)

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
            # Title (H1)
            parts.append(publication.title)
            
            # Publication info (container_title ve publication_date)
            pub_info_parts = []
            if publication.source_title:
                pub_info_parts.append(publication.source_title)
            if publication.publication_date:
                pub_info_parts.append(publication.publication_date.strftime("%Y-%m-%d"))
            
            if pub_info_parts:
                parts.append(f"*{' · '.join(pub_info_parts)}*")
            
            # Separator
            parts.append("---")
        
        # Sections
        for section in publication.sections:
            parts.append(self.render_section(section, section_heading_level, rendered_refs))
        
        text = "\n".join(parts)
        return normalize_whitespace(text)

    @classmethod
    def from_publication(
            cls,
            publication: Publication
    ) -> PlaintextRenderer:
        return cls(
            figures=publication.figures,
            tables=publication.tables,
        )