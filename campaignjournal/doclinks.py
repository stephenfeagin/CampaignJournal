import re
from typing import NoReturn, Tuple, Union
from xml.etree import ElementTree

import markdown
from flask import current_app, url_for
from markdown.inlinepatterns import InlineProcessor
from mdx_headdown import DowngradeHeadingsExtension

from .core import slugify


class DocLinkInlineProcessor(InlineProcessor):
    def __init__(self, pattern, config):
        super().__init__(pattern)
        self.config = config

    url_patterns = {
        "location": "locations.loc_detail",
        "character": "characters.char_detail",
        "npc": "characters.char_detail",
    }

    def handleMatch(
        self, m: re.Match, data: str
    ) -> Tuple[Union[ElementTree.Element, str], int, int]:
        a: Union[ElementTree.Element, str] = ""
        if m.group(1).strip():
            category, name, label = (g.strip() if g else None for g in m.groups())
            if label is None:
                label = name

            url = self.url_patterns.get(category.lower())
            if url is not None:
                if self.config.get("testing"):
                    full_url = f"url_for('{url}', slug='{slugify(name)}')"
                else:
                    full_url = url_for(url, slug=slugify(name))

                a = ElementTree.Element("a")
                a.text = label
                a.set("href", full_url)

        return a, m.start(0), m.end(0)


class DocLinkExtension(markdown.Extension):
    def __init__(self, **kwargs):
        self.config = {
            "testing": [
                False,
                "Generate string for url instead of calling flask.url_for",
            ]
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md: markdown.Markdown) -> NoReturn:
        self.md = md
        DOCLINK_RE = r"\[\[([\w ]+)[ \t]*:[ \t]*([\w ]+)[ \t]*:?[ \t]*([\w ]+)?\]\]"
        doclinkPattern = DocLinkInlineProcessor(DOCLINK_RE, self.getConfigs())
        doclinkPattern.md = md
        md.inlinePatterns.register(doclinkPattern, "doclink", 75)


def render_markdown(text: str) -> str:
    return markdown.markdown(
        text,
        extensions=[
            DocLinkExtension(testing=current_app.config.get("TESTING", False)),
            DowngradeHeadingsExtension(),
        ],
    )
