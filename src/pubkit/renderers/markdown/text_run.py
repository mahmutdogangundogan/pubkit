from __future__ import annotations
from typing import TYPE_CHECKING

from pubkit.renderers.styles import MarkdownStyleMap
if TYPE_CHECKING:
    from pubkit.models import (
        TextRun
    )

def _split_whitespaces(text: str) -> tuple[str, str, str]:
    n = len(text)

    left_idx = 0
    while left_idx < n and text[left_idx].isspace():
        left_idx += 1
    
    if left_idx == n:
        return text, "", ""

    right_idx = n - 1
    while right_idx >= 0 and text[right_idx].isspace():
        right_idx -= 1


    return text[:left_idx], text[left_idx:right_idx+1], text[right_idx+1:]

def text_run_to_md(text_runs: list[TextRun]) -> str:
    style_map = MarkdownStyleMap
    output: list[str] = []
    space_buffer: str = ""
    active_styles: list[str] = []

    for text_run in text_runs:
        current_styles = style_map.sort_styles(text_run.styles)
        left_ws, text, right_ws = _split_whitespaces(text_run.content)

        closing_styles: list[str] = []

        for style in active_styles:
            if style not in current_styles:
                closing_styles.append(style)

        # close old styles in reverse order
        for style in reversed(closing_styles):
            while active_styles and style != active_styles[-1]:
                output.append(style_map.close(active_styles[-1]))
                active_styles.pop()

            output.append(style_map.close(style))
            active_styles.pop()

        if len(space_buffer) > 0:
            output.append(space_buffer)

        # add new styles and the text
        # leftspace|style1|style2|text
        output.append(left_ws)
        for style in current_styles:
            if style not in active_styles:
                output.append(style_map.open(style))
                active_styles.append(style) # first in
        output.append(text)

        space_buffer = right_ws


    while active_styles:
        style = active_styles.pop()
        output.append(style_map.close(style))

    if len(space_buffer) > 0:
        output.append(space_buffer)
        
    return "".join(output)