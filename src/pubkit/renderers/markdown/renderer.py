from __future__ import annotations
from typing import TYPE_CHECKING
from .converter import node_content_to_md
if TYPE_CHECKING:
    from pubkit.models import (
        Publication, Section, Paragraph, Figure, Table
    )

MAX_HEADING_LEVEL = 6

class MarkdownRenderer:
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
            return node_content_to_md([self.figures[refid]])
        
        if refid in self.tables:
            return node_content_to_md([self.tables[refid]])
        
        return ""

    def render_paragraph(
            self,
            paragraph: Paragraph,
            rendered_refs: set[str] | None = None
    ):
        if rendered_refs is None:
            rendered_refs = set()
        
        parts = []
        
        content_md = node_content_to_md(paragraph.content)
        parts.append(content_md)
        
        for ref in paragraph.references:
            refid = ref.refid
            if refid not in rendered_refs:
                ref_md = self.render_reference(refid)
                if ref_md:
                    parts.append(ref_md)
                    rendered_refs.add(refid)
        
        return "\n\n".join(parts)
    
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
            heading_parts.append(node_content_to_md(section.label))
        
        if section.title:
            heading_parts.append(node_content_to_md(section.title))
        
        if heading_parts:
            level = min(heading_level, MAX_HEADING_LEVEL)
            prefix = "#" * level
            heading = " ".join(heading_parts)
            parts.append(f"{prefix} {heading}")
        
        # Content (Paragraph veya nested Section)
        for item in section.content:
            if item.type == "Paragraph":
                parts.append(self.render_paragraph(item, rendered_refs))
            elif item.type == "Section":
                parts.append(self.render_section(item, heading_level + 1, rendered_refs))
        
        return "\n\n".join(parts)

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
            parts.append(f"# {publication.title}")
            
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
        
        return "\n\n".join(parts)

    @classmethod
    def from_publication(
            cls,
            publication: Publication
    ) -> MarkdownRenderer:
        return cls(
            figures=publication.figures,
            tables=publication.tables,
        )