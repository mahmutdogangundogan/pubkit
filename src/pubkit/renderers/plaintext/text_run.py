from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pubkit.models import (
        TextRun
    )

def text_run_to_text(text_runs: list[TextRun]) -> str:
    output: list[str] = []

    for text_run in text_runs:
        output.append(text_run.content)

    return "".join(output)