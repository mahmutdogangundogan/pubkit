from __future__ import annotations
from typing import TYPE_CHECKING
from .text_run import text_run_to_html
from html import escape

if TYPE_CHECKING:
    from pubkit.models import (
        TextRun, Math, Image, Link, Formula, DocList, DocListItem,
        Figure, TableItem, Table
    )

def node_content_to_html(content: list[TextRun | Math | Image | Link | Formula | Figure | Table | DocList]) -> str:
    output = []
    text_run_buffer: list[TextRun] = []

    def flush_text_runs():
        if text_run_buffer:
            output.append(text_run_to_html(text_run_buffer))
            text_run_buffer.clear()

    for node in content:
        if node.type == "TextRun":
            text_run_buffer.append(node)
        else:
            flush_text_runs()
            if node.type == "Math":
                output.append(math_to_html(node))
            elif node.type == "Image":
                output.append(image_to_html(node))
            elif node.type == "Link":
                output.append(link_to_html(node))
            elif node.type == "Formula":
                output.append(formula_to_html(node))
            elif node.type == "Figure":
                output.append(figure_to_html(node))
            elif node.type == "Table":
                output.append(table_to_html(node))
            elif node.type == "DocList":
                output.append(doclist_to_html(node))
            else:
                raise ValueError(f"Unknown node type: {node.type}")
    
    flush_text_runs()
    return "".join(output)

def math_to_html(math: Math) -> str:
    return math.to_html()

def image_to_html(image: Image) -> str:
    alt_text = ""
    if image.content:
        alt_parts = [text_run_to_html(tr) for tr in image.content]
        alt_text = "".join(alt_parts)
    
    src = escape(image.src)
    return f'<img src="{src}" alt="{alt_text}" />'

def link_to_html(link: Link) -> str:
    href = escape(link.href)
    inner_html = node_content_to_html(link.content)
    return f'<a href="{href}">{inner_html}</a>'


def formula_to_html(formula: Formula) -> str:
    parts = []
    
    if formula.label:
        label_html = node_content_to_html(formula.label)
        parts.append(f'<span class="formula-label">{label_html}</span>')
    
    content_html = node_content_to_html(formula.content)
    parts.append(content_html)
    
    inner_html = "".join(parts)
    return f'<div class="formula">{inner_html}</div>'

def doclist_item_to_html(doclist_item: DocListItem) -> str:
    label_html = node_content_to_html(doclist_item.label) if doclist_item.label else ""
    content_html = node_content_to_html(doclist_item.content)
    
    label_span_html = ""
    if label_html:
        label_span_html = f'<span class="list-label">{label_html}</span>'
    
    return f'<li>{label_span_html}{content_html}</li>'

def doclist_to_html(doclist: DocList) -> str:
    parts = []
    
    if doclist.label:
        label_html = node_content_to_html(doclist.label)
        parts.append(f'<span class="list-label">{label_html}</span>')
    
    if doclist.title:
        title_html = node_content_to_html(doclist.title)
        parts.append(f'<span class="list-title">{title_html}</span>')
    
    if doclist.items:
        items_html = "".join(
            doclist_item_to_html(item)
            for item in doclist.items
        )
        parts.append(f'<ul>{items_html}</ul>')
    
    return "".join(parts)

# In future, inline figures may be changed to css
def figure_to_html(figure: Figure) -> str:
    parts = []
    
    if figure.srcs:
        for src in figure.srcs:
            src_escaped = escape(src)
            parts.append(f'<img src="{src_escaped}" alt="" style="max-width: 100%; height: auto;" />')
    
    # Caption (label + caption)
    caption_parts = []
    
    if figure.label:
        label_html = node_content_to_html(figure.label)
        caption_parts.append(f'<span class="figure-label">{label_html}</span>')
    
    if figure.caption:
        caption_html = node_content_to_html(figure.caption)
        caption_parts.append(f'<span class="figure-caption">{caption_html}</span>')
    
    if caption_parts:
        parts.append(f'<div class="figure-caption-container">{" ".join(caption_parts)}</div>')
    
    # Div wrapper
    inner_html = "\n".join(parts)
    id_attr = f' id="{escape(figure.id)}"' if figure.id else ""
    
    return f'<div{id_attr} class="figure-container">\n{inner_html}\n</div>'

def table_item_to_html(table_item: TableItem) -> str:
    parts = []
    
    if table_item.header:
        header_parts = []
        for row in table_item.header:
            row_parts = []
            for cell in row.cells:
                cell_content = node_content_to_html(cell.content)
                cell_html = f'<th>{cell_content}</th>'
                row_parts.append(cell_html)
            row_html =  f'<tr>{"".join(row_parts)}</tr>'
            header_parts.append(row_html)
        header_html = f'<thead>{"".join(header_parts)}</thead>'
        parts.append(header_html)
    

    if table_item.body:
        body_parts = []
        for row in table_item.body:
            row_parts = []
            for cell in row.cells:
                cell_content = node_content_to_html(cell.content)
                cell_html = f'<td>{cell_content}</td>'
                row_parts.append(cell_html)
            row_html =  f'<tr>{"".join(row_parts)}</tr>'
            body_parts.append(row_html)
        body_html = f'<tbody>{"".join(body_parts)}</tbody>'
        parts.append(body_html)
    
    return "".join(parts)

def table_to_html(table: Table) -> str:
    parts = []
    
    for item in table.content:
        if item.type == "TableItem":
            caption_parts = []
            
            if table.label:
                label_html = node_content_to_html(table.label)
                caption_parts.append(f'<span class="table-label">{label_html}</span>')
            
            if table.caption:
                caption_html = node_content_to_html(table.caption)
                caption_parts.append(f'<span class="table-caption">{caption_html}</span>')
            
            caption_element = ""
            if caption_parts:
                caption_element = f'<caption>{" ".join(caption_parts)}</caption>'

            table_item_html = table_item_to_html(item)
            parts.append(f'<table>{caption_element}{table_item_html}</table>')
        elif item.type == "Image":
            parts.append(image_to_html(item))
    
    if table.footnotes:
        footnotes_html = "".join(
            node_content_to_html(fn.content)
            for fn in table.footnotes
        )
        parts.append(f'<div class="table-footnotes">{footnotes_html}</div>')
    
    # Div wrapper
    inner_html = "\n".join(parts)
    id_attr = f' id="{escape(table.id)}"' if table.id else ""
    
    return f'<div{id_attr} class="table-container">\n{inner_html}\n</div>'