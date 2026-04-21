from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Annotated, Union, Literal
#import pypandoc
from datetime import date
from uuid import UUID

class ContentNode(BaseModel):
    type: str = Field(..., frozen=True)

class TextRun(ContentNode):
    type: Literal["TextRun"] = Field("TextRun", repr=False)
    content: str
    styles: set[str] = Field(default_factory=set)

class Math(ContentNode):
    type: Literal["Math"] = Field("Math", repr=False)
    mathml_json: dict

    @staticmethod
    def _json_to_mathml(node) -> str:
        """MathML JSON'ı MathML string'e çevirir (HTML için)."""
        ### !!! TEMP FIX !!! ###
        if node is None:
            return ""
        ### !!! Will investigate later !!! ###
        
        if isinstance(node, str):
            return node

        tag = node.get("#name")
        attrs = node.get("attributes", {})
        children = node.get("children", [])

        attr_str = "".join(
            f' {k}="{v}"' for k, v in attrs.items() if k != "is"
        )

        if isinstance(children, list):
            inner = "".join(Math._json_to_mathml(c) for c in children)
        else:
            inner = str(children)

        return f"<{tag}{attr_str}>{inner}</{tag}>"

    @staticmethod
    def _json_to_plaintext(node) -> str:
        """MathML JSON'dan düz text çıkarır (full-text search için)."""
        if node is None:
            return ""
        
        if isinstance(node, str):
            return node
        
        children = node.get("children", [])
        
        if isinstance(children, list):
            return "".join(
                c if isinstance(c, str) else Math._json_to_plaintext(c)
                for c in children
            )
        
        return str(children) if children else ""

    def to_html(self) -> str:
        """MathML HTML string döndürür."""
        return self._json_to_mathml(self.mathml_json)
    
    def to_markdown(self) -> str:
        return self._json_to_plaintext(self.mathml_json)
        """MathML'i pandoc ile Markdown'a çevirir."""
        html = self._json_to_mathml(self.mathml_json)
        return pypandoc.convert_text(
            f"<span>{html}</span>",
            to="markdown",
            format="html"
        )
    
    def to_plaintext(self) -> str:
        """MathML'den düz text çıkarır."""
        return self._json_to_plaintext(self.mathml_json)

class Image(ContentNode):
    type: Literal["Image"] = Field("Image", repr=False)
    content: list[TextRun] = Field(default_factory=list)
    src: str

class Link(ContentNode):
    type: Literal["Link"] = Field("Link", repr=False)
    content: list[
        Annotated[
            Union[TextRun, Math, Image],
            Field(discriminator="type"),
        ]
    ] = Field(default_factory=list)
    href: str

# Figure, Table, Bibliography gibi referans verilen nesneler için
class Reference(ContentNode):
    type: Literal["Reference"] = Field("Reference", repr=False)
    refid: str
    ref_type: str

class Footnote(ContentNode):
    type: Literal["Footnote"] = Field("Footnote", repr=False)
    label: list[
        Annotated[
            Union[TextRun, Image, Math],
            Field(discriminator="type"),
        ]
    ] = Field(default_factory=list)
    content: list[
        Annotated[
            Union[TextRun, Image, Math, Link],
            Field(discriminator="type"),
        ]
    ] = Field(default_factory=list)

class Formula(ContentNode): # bloktur
    type: Literal["Formula"] = Field("Formula", repr=False)
    label: list[
        Annotated[
            Union[TextRun, Image, Math],
            Field(discriminator="type"),
        ]
    ] = Field(default_factory=list)
    content: list[
        Annotated[
            Union[TextRun, Image, Math, Link],
            Field(discriminator="type"),
        ]
    ] =  Field(default_factory=list)

class DocListItem(ContentNode):
    type: Literal["DocListItem"] = Field("DocListItem", repr=False)
    label: list[
        Annotated[
            Union[TextRun, Image, Math],
            Field(discriminator="type"),
        ]
    ] = Field(default_factory=list)
    content: list[
        Annotated[
            Union[TextRun, Image, Link, DocList, Math],
            Field(discriminator="type"),
        ]
    ] = Field(default_factory=list)

class DocList(ContentNode):
    type: Literal["DocList"] = Field("DocList", repr=False)
    label: list[
        Annotated[
            Union[TextRun, Image, Math],
            Field(discriminator="type"),
        ]
    ] = Field(default_factory=list)
    title: list[
        Annotated[
            Union[TextRun, Image, Math, Link],
            Field(discriminator="type"),
        ]
    ] = Field(default_factory=list)
    items: list[DocListItem] = Field(default_factory=list)

class Paragraph(ContentNode):
    type: Literal["Paragraph"] = Field("Paragraph", repr=False)
    id: UUID | None = Field(default=None)
    content: list[
        Annotated[
            Union[TextRun, Image, Link, DocList, Formula, Math],
            Field(discriminator="type"),
        ]
    ] = Field(default_factory=list)
    references: list[Reference] = Field(default_factory=list)

class Figure(ContentNode):
    type: Literal["Figure"] = Field("Figure", repr=False)
    id: str
    label: list[
        Annotated[
            Union[TextRun, Image, Math],
            Field(discriminator="type"),
        ]
    ] = Field(default_factory=list)
    caption: list[
        Annotated[
            Union[TextRun, Image, Math, Link],
            Field(discriminator="type"),
        ]
    ] = Field(default_factory=list)
    srcs: list[str] = Field(default_factory=list)

class TableCell(ContentNode):
    type: Literal["TableCell"] = Field("TableCell", repr=False)
    content: list[
        Annotated[
            Union[TextRun, Image, Figure, Link, Math],
            Field(discriminator="type"),
        ]
    ] = Field(default_factory=list)

class TableRow(ContentNode):
    type: Literal["TableRow"] = Field("TableRow", repr=False)
    cells: list[TableCell] = Field(default_factory=list)

class TableItem(ContentNode):
    type: Literal["TableItem"] = Field("TableItem", repr=False)
    header: list[TableRow] = Field(default_factory=list)
    body: list[TableRow] = Field(default_factory=list)

class Table(ContentNode):
    type: Literal["Table"] = Field("Table", repr=False)
    id: str
    label: list[
        Annotated[
            Union[TextRun, Image, Math],
            Field(discriminator="type"),
        ]
    ] = Field(default_factory=list)
    caption: list[
        Annotated[
            Union[TextRun, Image, Math, Link],
            Field(discriminator="type"),
        ]
    ] = Field(default_factory=list)
    content: list[
        Annotated[
            Union[TableItem, Image],
            Field(discriminator="type"),
        ]
    ] = Field(default_factory=list) # tablo ya da tablonun resmi olabilir
    footnotes: list[Footnote] = Field(default_factory=list)


class ChemExp(ContentNode):
    type: Literal["ChemExp"] = Field("ChemExp", repr=False)

class Section(ContentNode):
    type: Literal["Section"] = Field("Section", repr=False)
    id: str | None = Field(default=None)
    label: list[
        Annotated[
            Union[TextRun, Image, Math],
            Field(discriminator="type"),
        ]
    ] = Field(default_factory=list)
    title: list[
        Annotated[
            Union[TextRun, Image, Math, Link],
            Field(discriminator="type"),
        ]
    ] = Field(default_factory=list)
    content: list[
        Annotated[
            Union["Section", Paragraph],
            Field(discriminator="type"),
        ]
    ] = Field(default_factory=list)

class Publication(ContentNode):
    type: Literal["Publication"] = Field("Publication", repr=False)
    id: UUID
    title: str
    doi: str | None = Field(default=None)
    authors: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    publication_date: date | None = Field(default=None)
    publication_type: Literal[
        "ARTICLE", "REVIEW", 'CONFERENCE_PAPER', 'BOOK',
        'BOOK_CHAPTER', 'EDITORIAL', 'OTHER'
    ]
    source_title: str | None = Field(default=None)
    sections: list[Section] = Field(default_factory=list)
    figures: dict[str, Figure] = Field(default_factory=dict) # her birinin id'si olmalı
    tables: dict[str, Table] = Field(default_factory=dict) # her birinin id'si olmalı
