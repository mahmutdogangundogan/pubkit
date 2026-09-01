# pubkit

Typed data models and renderers for scientific publications.

`pubkit` lets you represent a publication (sections, paragraphs, figures, tables, references, math, and more) as Pydantic models, serialize it to flat records for storage, rebuild it back, and render it to HTML, Markdown, or plain text.

## Features

- **Domain models** — `Publication`, `Section`, `Paragraph`, `Figure`, `Table`, `TextRun`, `Math`, `Reference`, `Footnote`, and other content nodes, built on Pydantic v2.
- **Transform layer** — dump a publication into flat records (`PublicationRecord`, `SectionRecord`, `ParagraphRecord`, …) and rebuild the full object tree from them with `dump_publication` / `rebuild_publication`.
- **Renderers** — render publications or individual nodes to:
  - HTML (`HTMLRenderer`, `node_content_to_html`)
  - Markdown (`MarkdownRenderer`, `node_content_to_md`)
  - Plain text (`PlaintextRenderer`, `node_content_to_text`)

## Requirements

- Python 3.10+
- [Pydantic](https://docs.pydantic.dev/) v2

## Installation

From GitHub:

```sh
uv add git+https://github.com/mahmutdogangundogan/pubkit
# or
pip install git+https://github.com/mahmutdogangundogan/pubkit
```

### Using a local checkout

To use `pubkit` from another project on the same machine (e.g. as a dev dependency):

```sh
uv add --dev /path/to/pubkit
```

Add `--editable` if you want changes in the `pubkit` source to be picked up without reinstalling:

```sh
uv add --dev --editable /path/to/pubkit
```

## Usage

```python
from pubkit import (
    Publication,
    MarkdownRenderer,
    dump_publication,
    rebuild_publication,
)

# Render a publication's content to Markdown
renderer = MarkdownRenderer(figures=figures, tables=tables)
md = renderer.render_paragraph(paragraph)

# Serialize to flat records and rebuild
record = dump_publication(publication)
publication = rebuild_publication(record)
```

## Development

The project is managed with [uv](https://docs.astral.sh/uv/).

```sh
# Build sdist and wheel into dist/
uv build
```

## License

Copyright © 2026 Mahmut Doğan Gündoğan. All rights reserved.

This code is made available for viewing only. No permission is granted to use, copy, modify, or distribute it without explicit written consent from the author.
