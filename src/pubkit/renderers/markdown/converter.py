from __future__ import annotations
from typing import TYPE_CHECKING
from .text_run import text_run_to_md

if TYPE_CHECKING:
    from pubkit.models import (
        TextRun, Math, Image, Link, Formula, DocList, DocListItem,
        Figure, TableItem, Table
    )

def node_content_to_md(content: list[TextRun | Math | Image | Link | Formula | Figure | Table | DocList]) -> str:
    output = []
    text_run_buffer: list[TextRun] = []

    def flush_text_runs():
        if text_run_buffer:
            output.append(text_run_to_md(text_run_buffer))
            text_run_buffer.clear()

    for node in content:
        if node.type == "TextRun":
            text_run_buffer.append(node)
        else:
            flush_text_runs()
            if node.type == "Math":
                output.append(math_to_md(node))
            elif node.type == "Image":
                output.append(image_to_md(node))
            elif node.type == "Link":
                output.append(link_to_md(node))
            elif node.type == "Formula":
                output.append(formula_to_md(node))
            elif node.type == "Figure":
                output.append(figure_to_md(node))
            elif node.type == "Table":
                output.append(table_to_md(node))
            elif node.type == "DocList":
                output.append(doclist_to_md(node))
            else:
                raise ValueError(f"Unknown node type: {node.type}")
    
    flush_text_runs()
    return "".join(output)

def math_to_md(math: Math) -> str:
    # Markdown not supported YET!
    return math._json_to_plaintext()

def image_to_md(image: Image) -> str:
    alt_text = text_run_to_md(image.content)
    return f"![{alt_text}]({image.src})" 

def link_to_md(link: Link) -> str:
    label = node_content_to_md(link.content)
    return f"[{label}]({link.href})"

def formula_to_md(formula: Formula) -> str:
    label = ""

    if formula.label:
        label = node_content_to_md(formula.label) + " " 
    content = node_content_to_md(formula.content)
    return f"\n$${label}{content}$$\n"

def doclist_item_to_md(doclist_item: DocListItem, indent: int = 0) -> str:
    prefix = "  " * indent + "- "
    
    label = ""
    if doclist_item.label:
        label = node_content_to_md(doclist_item.label) + " "
    
    content = node_content_to_md(doclist_item.content)
    
    return f"{prefix}{label}{content}"

def doclist_to_md(doclist: DocList, indent: int = 0) -> str:
    parts = []

    title_parts = []
    if doclist.label:
        title_parts.append(node_content_to_md(doclist.label))

    if doclist.title:
        title_parts.append(node_content_to_md(doclist.title))

    if title_parts:
        parts.append(" ".join(title_parts))

    
    for item in doclist.items:
        parts.append(doclist_item_to_md(item, indent))
    
    return "\n".join(parts)

def figure_to_md(figure: Figure) -> str:
    parts = []
    
    for src in figure.srcs:
        parts.append(f"![{figure.id}]({src})")
    
    caption_parts = []
    if figure.label:
        caption_parts.append(node_content_to_md(figure.label))
    if figure.caption:
        caption_parts.append(node_content_to_md(figure.caption))
    
    if caption_parts:
        parts.append(" ".join(caption_parts))
    
    return "\n\n".join(parts)

def table_item_to_md(item: TableItem) -> str:
    rows = []
    
    if item.header:
        for row in item.header:
            cells = [node_content_to_md(cell.content) for cell in row.cells]
            rows.append("| " + " | ".join(cells) + " |")
        
        # Separator
        if item.header and item.header[0].cells:
            sep = "| " + " | ".join(["---"] * len(item.header[0].cells)) + " |"
            rows.append(sep)
    
    for row in item.body:
        cells = [node_content_to_md(cell.content) for cell in row.cells]
        rows.append("| " + " | ".join(cells) + " |")
    
    return "\n".join(rows)

def table_to_md(table: Table) -> str:
    parts = []
    
    caption_parts = []
    if table.label:
        caption_parts.append(node_content_to_md(table.label))
    if table.caption:
        caption_parts.append(node_content_to_md(table.caption))
    
    if caption_parts:
        parts.append(" ".join(caption_parts))
    
    for item in table.content:
        if item.type == "TableItem":
            parts.append(table_item_to_md(item))
        elif item.type == "Image":
            parts.append(image_to_md(item))
    
    return "\n\n".join(parts)