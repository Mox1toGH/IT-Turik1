"""Tiptap content builders for the development seeder.

Every node and mark emitted here exists in the editor schema actually used by
the frontend. The single source of truth for that schema is
``frontend/src/components/ui/RichTextEditor/extensions.ts``, which is built from
Tiptap ``StarterKit`` 3.22 plus ``Highlight`` and a configured ``Link``.

StarterKit 3.22 ships: Blockquote, Bold, Code, CodeBlock, Document, HardBreak,
Heading, HorizontalRule, Italic, Link, BulletList/ListItem/ListKeymap/
OrderedList, Paragraph, Strike, Text, Underline, Dropcursor, Gapcursor,
TrailingNode, UndoRedo.

Deliberately NOT emitted, because no extension provides them anywhere in the
project: image, table/tableRow/tableCell/tableHeader, taskList, mention,
emoji, subscript, superscript, textStyle, and any custom node or mark.
"""

from __future__ import annotations

from typing import Any, Iterable, Sequence

JSONContent = dict[str, Any]

# Matches Link.configure({ HTMLAttributes: ... }) in the frontend.
LINK_ATTRS = {
    'target': '_blank',
    'rel': 'noopener noreferrer nofollow',
    'class': None,
}

# Matches the toolbar default: chain().setHighlight({ color: '#8ce99a' }).
HIGHLIGHT_COLOR = '#8ce99a'

TEXT_ALIASES = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
}


def _escape(value: str) -> str:
    for char, replacement in TEXT_ALIASES.items():
        value = value.replace(char, replacement)
    return value


# ---------------------------------------------------------------------------
# Marks
# ---------------------------------------------------------------------------

def bold(node: JSONContent) -> JSONContent:
    return _with_mark(node, {'type': 'bold'})


def italic(node: JSONContent) -> JSONContent:
    return _with_mark(node, {'type': 'italic'})


def underline(node: JSONContent) -> JSONContent:
    return _with_mark(node, {'type': 'underline'})


def strike(node: JSONContent) -> JSONContent:
    return _with_mark(node, {'type': 'strike'})


def code(node: JSONContent) -> JSONContent:
    return _with_mark(node, {'type': 'code'})


def highlight(node: JSONContent) -> JSONContent:
    return _with_mark(node, {'type': 'highlight', 'attrs': {'color': HIGHLIGHT_COLOR}})


def link(node: JSONContent, href: str) -> JSONContent:
    """Wrap an inline node in a link mark.

    ``setLink`` is emitted by the editor as an *inline node* wrapping its text,
    not as a mark, so this produces the node form Tiptap actually round-trips.
    """
    children = node.get('content') or [node]
    return {
        'type': 'link',
        'attrs': {'href': href, **LINK_ATTRS},
        'content': children,
    }


def _with_mark(node: JSONContent, mark: dict[str, Any]) -> JSONContent:
    node = dict(node)
    marks = list(node.get('marks') or [])
    marks.append(mark)
    node['marks'] = marks
    return node


# ---------------------------------------------------------------------------
# Inline nodes
# ---------------------------------------------------------------------------

def text(value: str) -> JSONContent:
    return {'type': 'text', 'text': _escape(value)}


def raw_text(value: str) -> JSONContent:
    """Text node without HTML escaping, for code blocks where `<` is literal."""
    return {'type': 'text', 'text': value}


def hard_break() -> JSONContent:
    return {'type': 'hardBreak'}


# ---------------------------------------------------------------------------
# Block nodes
# ---------------------------------------------------------------------------

def doc(*content: JSONContent) -> JSONContent:
    return {'type': 'doc', 'content': [node for node in content if node]}


def para(*content: JSONContent) -> JSONContent:
    if not content:
        return {'type': 'paragraph'}
    return {'type': 'paragraph', 'content': list(content)}


def heading(level: int, value: str) -> JSONContent:
    assert 1 <= level <= 6, 'StarterKit Heading supports levels 1-6'
    return {'type': 'heading', 'attrs': {'level': level}, 'content': [text(value)]}


def bullet_list(items: Sequence[Sequence[JSONContent]]) -> JSONContent:
    return {'type': 'bulletList', 'content': [_list_item(item) for item in items]}


def ordered_list(items: Sequence[Sequence[JSONContent]], start: int = 1) -> JSONContent:
    return {
        'type': 'orderedList',
        'attrs': {'start': start},
        'content': [_list_item(item) for item in items],
    }


def _list_item(content: Sequence[JSONContent]) -> JSONContent:
    # A listItem may hold several blocks, which is how nested lists are expressed.
    return {'type': 'listItem', 'content': list(content)}


def blockquote(*content: JSONContent) -> JSONContent:
    return {'type': 'blockquote', 'content': list(content)}


def code_block(source: str, language: str | None = None) -> JSONContent:
    attrs = {'language': language} if language else None
    node: JSONContent = {'type': 'codeBlock', 'content': [raw_text(source.rstrip('\n'))]}
    if attrs:
        node['attrs'] = attrs
    return node


def horizontal_rule() -> JSONContent:
    return {'type': 'horizontalRule'}


# ---------------------------------------------------------------------------
# Composite helpers
# ---------------------------------------------------------------------------

def bullet_item(value: str) -> list[JSONContent]:
    return [para(text(value))]


def nested_bullet_item(value: str, children: Sequence[Sequence[JSONContent]]) -> list[JSONContent]:
    """A list item that nests one more list inside it."""
    return [para(text(value)), bullet_list(children)]


def round_task_description(*, round_label: str, tournament_name: str, focus: str) -> JSONContent:
    """Round `description` — full coverage of the StarterKit schema."""
    return doc(
        heading(2, f'{round_label}: {focus}'),
        para(
            text('In '),
            bold(text(tournament_name)),
            text(' you must deliver a working '),
            italic(text(focus)),
            text(' implementation. Partial credit applies.'),
        ),
        para(
            text('Scoring emphasises '),
            bold(text('working software')),
            text(' over documentation, but a '),
            underline(text('readable README')),
            text(' is expected. Legacy approaches such as '),
            strike(text('monolithic single-file scripts')),
            text(' are penalised.'),
        ),
        heading(3, 'What is graded'),
        bullet_list([
            [para(text('Functionality'), hard_break(), text('does it do what the spec says?'))],
            nested_bullet_item('Code quality', [
                bullet_item('Typed, no `any` casts'),
                bullet_item('Tests for the core paths'),
                bullet_item('No secrets committed'),
            ]),
            bullet_item('Design — see the architecture notes below'),
        ]),
        heading(3, 'Workflow'),
        ordered_list([
            bullet_item('Fork the starter repository'),
            nested_bullet_item('Implement the feature', [
                bullet_item('Add endpoints under `/api/v1`'),
                bullet_item('Cover them with integration tests'),
            ]),
            [para(link(text('Open the submission checklist'), 'https://docs.python.org/3/'))],
            bullet_item('Submit before the deadline'),
        ]),
        blockquote(
            para(
                text('If you cannot finish, submit what you have. '),
                highlight(text('A partial submission is far better than a missing one.')),
            ),
        ),
        horizontal_rule(),
        heading(3, 'Reference skeleton'),
        code_block(
            'from dataclasses import dataclass\n\n\n'
            '@dataclass\n'
            'class Submission:\n'
            '    team: str\n'
            '    round_id: int\n'
            '    github_url: str\n',
            language='python',
        ),
    )


def round_tech_requirements(*, stack: Sequence[str], focus: str) -> JSONContent:
    """Round `tech_requirements` — stack list with nested detail."""
    return doc(
        heading(2, 'Technical requirements'),
        para(text('The submission must be built with the following stack:')),
        bullet_list(
            [[para(code(text(item)))] for item in stack]
            + [nested_bullet_item('Anything versioned below is not accepted', [
                bullet_item(f'Minimum {stack[0]} version is pinned in CI'),
                bullet_item('No external services without a local fallback'),
            ])],
        ),
        para(
            text('Keep the build reproducible — a developer must be able to clone and run the project without extra steps. '),
            italic(text(f'See the {focus} notes in the round description for context.')),
        ),
    )


def round_must_have_requirements(*, checks: Sequence[str], penalty_note: str) -> JSONContent:
    """Round `must_have_requirements` — checklist plus policy note."""
    return doc(
        heading(2, 'Must have'),
        para(text('A submission is only scored if every item below is satisfied.')),
        ordered_list([bullet_item(item) for item in checks]),
        blockquote(para(text(penalty_note))),
    )


def news_article_content(*, headline: str, standfirst: str, sections: Sequence[tuple[str, str]]) -> JSONContent:
    """News content — StarterKit plus the `highlight` mark (news viewer has it)."""
    blocks: list[JSONContent] = [
        heading(2, headline),
        para(text(standfirst)),
    ]
    for index, (title, body) in enumerate(sections, start=1):
        blocks.append(heading(3, f'{index}. {title}'))
        blocks.append(para(text(body)))
    return doc(*blocks)


def news_feature_content(*, headline: str, blocks: Sequence[JSONContent]) -> JSONContent:
    """Long-form article; the caller supplies the body blocks."""
    return doc(heading(2, headline), *blocks)


def full_schema_showcase() -> JSONContent:
    """One document exercising every node and mark the editor supports.

    Used by the news seeder so a developer can confirm rendering of the whole
    schema in a single article.
    """
    return doc(
        heading(1, 'Schema showcase'),
        para(text('This article exercises every node and mark the editor enables.')),
        heading(2, 'Inline marks'),
        para(
            text('bold'),
            text(', '),
            italic(text('italic')),
            text(', '),
            underline(text('underline')),
            text(', '),
            strike(text('strike-through')),
            text(', '),
            code(text('inline code')),
            text(', and '),
            highlight(text('highlight')),
            text('.'),
        ),
        heading(2, 'Lists'),
        bullet_list([
            bullet_item('Bullet level one'),
            nested_bullet_item('Bullet level two', [
                bullet_item('Bullet level three, via a nested list item'),
            ]),
        ]),
        ordered_list([
            bullet_item('Ordered level one'),
            [para(text('Ordered level two')), ordered_list([bullet_item('Ordered level three')])],
        ]),
        heading(2, 'Blockquote'),
        blockquote(para(text('Evaluation feedback is released once every jury member has scored.'))),
        heading(2, 'Code block'),
        code_block(
            'def compute_rank(scores: list[int]) -> int:\n'
            '    return sorted(scores, reverse=True).index(max(scores)) + 1\n',
            language='python',
        ),
        heading(2, 'Link and rule'),
        para(link(text('Tiptap JSON documentation'), 'https://tiptap.dev/docs/editor/api/utilities/json')),
        horizontal_rule(),
        para(text('End of showcase.'), hard_break(), text('Second line after a hard break.')),
    )


def empty_doc() -> JSONContent:
    return doc(para(text('')))


def as_document(value: Any) -> JSONContent:
    """Coerce legacy ``{'text': ...}`` blobs into a renderable document.

    Older seeded rows stored an ad-hoc shape that Tiptap cannot render. Rather
    than dropping the text, wrap it in a minimal document.
    """
    if isinstance(value, dict) and value.get('type') == 'doc':
        return value
    if isinstance(value, dict) and isinstance(value.get('text'), str):
        return doc(para(text(value['text'])))
    if isinstance(value, str) and value.strip():
        return doc(para(text(value)))
    return empty_doc()


def iter_text_nodes(node: Any) -> Iterable[str]:
    """Yield every text fragment, used by the verification pass."""
    if isinstance(node, dict):
        if node.get('type') == 'text' and isinstance(node.get('text'), str):
            yield node['text']
        for child in node.get('content') or []:
            yield from iter_text_nodes(child)