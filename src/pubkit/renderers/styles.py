from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class Tag:
    opening_tag: str
    closing_tag: str

class BaseStyleMap:
    _aliases: dict[str, str] = {}

    @classmethod
    def _get_tag(cls, name: str) -> Tag:
        alias = cls._aliases.get(name, name)
        tag = getattr(cls, alias, None)
        if not isinstance(tag, Tag):
            raise AttributeError(f"Unknown style: {name}")
        return tag

    @classmethod
    def open(cls, name: str) -> str:
        return cls._get_tag(name).opening_tag

    @classmethod
    def close(cls, name: str) -> str:
        return cls._get_tag(name).closing_tag

class MarkdownStyleMap(BaseStyleMap):
    bold = Tag("**", "**")
    italic = Tag("*", "*")
    monospace = Tag("`", "`")
    cross_out = Tag("~~", "~~")
    underline = Tag("<u>", "</u>")
    small_caps = Tag('<span style="font-variant: small-caps;">', "</span>")
    sans_serif = Tag('<span style="font-family: sans-serif;">', "</span>")
    superscript = Tag("<sup>", "</sup>")
    subscript = Tag("<sub>", "</sub>")

    _aliases = {
        "cross-out": "cross_out",
        "small-caps": "small_caps",
        "sans-serif": "sans_serif"
    }

class HTMLStyleMap(BaseStyleMap):
    bold = Tag("<strong>", "</strong>")
    italic = Tag("<em>", "</em>")
    monospace = Tag("<code>", "</code>")
    cross_out = Tag("<del>", "</del>")
    underline = Tag("<u>", "</u>")
    small_caps = Tag('<span style="font-variant: small-caps;">', "</span>")
    sans_serif = Tag('<span style="font-family: sans-serif;">', "</span>")
    superscript = Tag("<sup>", "</sup>")
    subscript = Tag("<sub>", "</sub>")

    _aliases = {
        "cross-out": "cross_out",
        "small-caps": "small_caps",
        "sans-serif": "sans_serif"
    }

    
