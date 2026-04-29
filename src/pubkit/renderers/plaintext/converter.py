from __future__ import annotations
from typing import TYPE_CHECKING
import re
from .text_run import text_run_to_text

if TYPE_CHECKING:
    from pubkit.models import (
        TextRun, Math, Image, Link, Formula, DocList, DocListItem,
        Figure, TableItem, Table
    )

def normalize_whitespace(text: str) -> str:
    lines = [re.sub(r'\s+', ' ', line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)

def node_content_to_text(content: list[TextRun | Math | Image | Link | Formula | Figure | Table | DocList]) -> str:
    output = []
    text_run_buffer: list[TextRun] = []

    def flush_text_runs():
        if text_run_buffer:
            output.append(text_run_to_text(text_run_buffer))
            text_run_buffer.clear()

    for node in content:
        if node.type == "TextRun":
            text_run_buffer.append(node)
        else:
            flush_text_runs()
            if node.type == "Math":
                output.append(math_to_text(node))
            elif node.type == "Image":
                output.append(image_to_text(node))
            elif node.type == "Link":
                output.append(link_to_text(node))
            elif node.type == "Formula":
                output.append(formula_to_text(node))
            elif node.type == "Figure":
                output.append(figure_to_text(node))
            elif node.type == "Table":
                output.append(table_to_text(node))
            elif node.type == "DocList":
                output.append(doclist_to_text(node))
            else:
                raise ValueError(f"Unknown node type: {node.type}")
    
    flush_text_runs()
    return "".join(output)

def math_to_text(math: Math) -> str:
    return math.to_plaintext()

def image_to_text(image: Image) -> str:
    alt_text = ""
    if image.content:
        alt_parts = [text_run_to_text(tr) for tr in image.content]
        alt_text = "".join(alt_parts)
    
    return alt_text

def link_to_text(link: Link) -> str:
    return node_content_to_text(link.content)

def formula_to_text(formula: Formula) -> str:
    return node_content_to_text(formula.content)

def doclist_item_to_text(doclist_item: DocListItem) -> str:
    label_text = node_content_to_text(doclist_item.label) if doclist_item.label else ""
    content_text = node_content_to_text(doclist_item.content)

    return " ".join([label_text, content_text])

def doclist_to_text(doclist: DocList) -> str:
    parts = []
    
    if doclist.label:
        label_text = node_content_to_text(doclist.label)
        parts.append(label_text)
    
    if doclist.title:
        title_text = node_content_to_text(doclist.title)
        parts.append(title_text)

    for item in doclist.items:
        parts.append(doclist_item_to_text(item))
    
    return " ".join(parts)


def figure_to_text(figure: Figure) -> str:
    parts = []

    if figure.label:
        label_text = node_content_to_text(figure.label)
        parts.append(label_text)
    
    if figure.caption:
        caption_text = node_content_to_text(figure.caption)
        parts.append(caption_text)
    
    return " ".join(parts)

def table_item_to_text(table_item: TableItem) -> str:
    cells = []
    
    for row in table_item.header:
        for cell in row.cells:
            cell_text = node_content_to_text(cell.content)
            if cell_text:
                cells.append(cell_text)
    
    for row in table_item.body:
        for cell in row.cells:
            cell_text = node_content_to_text(cell.content)
            if cell_text:
                cells.append(cell_text)
    
    return " ".join(cells)

def table_to_text(table: Table) -> str:
    parts = []

    if table.label:
        label_text = node_content_to_text(table.label)
        parts.append(label_text)
    
    if table.caption:
        caption_text = node_content_to_text(table.caption)
        parts.append(caption_text)
    
    for item in table.content:
        if item.type == "TableItem":
            parts.append(table_item_to_text(item))
        elif item.type == "Image":
            img_text = image_to_text(item)
            if img_text:
                parts.append(img_text)
    
    text = " ".join(parts)
    return text