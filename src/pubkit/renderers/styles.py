from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class Tag:
    opening_tag: str
    closing_tag: str
    priority: int

class BaseStyleMap:
    _aliases: dict[str, str] = {}
    _ignored: set[str] = set()

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
    
    @classmethod
    def sort_styles(cls, styles: set[str]) -> list[str]:
        tagged: list[tuple[str, Tag]] = []
        for s in styles:
            if s in cls._ignored:
                continue
            tag = cls._get_tag(s)
            tagged.append((s, tag))

        tagged.sort(key=lambda x: x[1].priority)
        return [s for s, _ in tagged]

class MarkdownStyleMap(BaseStyleMap):
    bold = Tag("**", "**", 10)
    cross_out = Tag("~~", "~~", 20)
    italic = Tag("*", "*", 30)
    underline = Tag("<u>", "</u>", 40)
    superscript = Tag("<sup>", "</sup>", 50)
    subscript = Tag("<sub>", "</sub>", 50)
    monospace = Tag("`", "`", 60)
    
    small_caps = None
    sans_serif = None

    _aliases = {
        "cross-out": "cross_out",
        "small-caps": "small_caps",
        "sans-serif": "sans_serif"
    }

    _ignored = {
        "small-caps",
        "sans-serif"
    }

# class HTMLStyleMap(BaseStyleMap):
#     bold = Tag("<strong>", "</strong>")
#     italic = Tag("<em>", "</em>")
#     monospace = Tag("<code>", "</code>")
#     cross_out = Tag("<del>", "</del>")
#     underline = Tag("<u>", "</u>")
#     small_caps = Tag('<span style="font-variant: small-caps;">', "</span>")
#     sans_serif = Tag('<span style="font-family: sans-serif;">', "</span>")
#     superscript = Tag("<sup>", "</sup>")
#     subscript = Tag("<sub>", "</sub>")

#     _aliases = {
#         "cross-out": "cross_out",
#         "small-caps": "small_caps",
#         "sans-serif": "sans_serif"
#     }

    
