"""The published bench keeps the same reading and gesture roles on every door.

These are chosen layout contracts, not a claim that the spacing ladder proves
usability. Real geometry is checked by the headless acceptance matrix too.
"""
from html.parser import HTMLParser
from pathlib import Path
import re


class Note(HTMLParser):
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.disclosure = self.reset = False
        self.words = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id') == 'published-note':
            self.depth = 1
        elif self.depth:
            self.depth += 1
            self.disclosure |= tag == 'details' and 'open' not in attrs
            self.reset |= tag == 'a' and attrs.get('id') == 'reset-demo'

    def handle_endtag(self, tag):
        if self.depth:
            self.depth -= 1

    def handle_data(self, text):
        if self.depth:
            self.words.append(text)


def rules(css):
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    found = {}
    for selectors, body in re.findall(r'([^{}]+)\{([^{}]*)\}', css):
        declarations = dict(item.strip().split(':', 1) for item in body.split(';') if ':' in item)
        for selector in selectors.split(','):
            found.setdefault(selector.strip(), {}).update({k.strip(): v.strip() for k, v in declarations.items()})
    return found


def check(page, editor, address):
    note = Note(); note.feed(page)
    words = ' '.join(note.words)
    assert note.disclosure and note.reset and 'git clone' in words, address + ': copy instructions remain available in a closed disclosure, beside reset'
    css = '\n'.join(re.findall(r'<style[^>]*>(.*?)</style>', page, re.S))
    narrow = css.split('@media(max-width:40rem){', 1)[-1]
    assert narrow != css, address + ': narrow reading contract is absent'
    base, small, full = rules(css.split('@media(max-width:40rem){', 1)[0]), rules(narrow), rules(editor)
    assert base['#nav-seg button']['font'] == 'var(--control)', address + ': history is a gesture, not a heading'
    assert base['#canvas-host']['overflow'] == 'auto' and base['#canvas-host svg']['max-width'] == 'none', address + ': stated pages scroll instead of shrinking their measured letters'
    assert base['#published-note']['overflow'] == 'auto' and base['#published-note details[open]']['flex-basis'] == '100%', address + ': expanded instructions remain readable in their own flow'
    for selector in ['.refusal', '.pending']:
        assert small[selector]['flex-direction'] == 'column' and small[selector]['overflow-wrap'] == 'anywhere', address + ': the whole address precedes the whole answer on a narrow panel'
    for selector in ['.refusal code', '.pending code']:
        assert small[selector]['white-space'] == 'normal', address + ': an address may wrap'
    assert small['#view-seg']['order'] == small['#keys-btn']['order'] == '1', address + ': views and help follow history and state'
    assert full['.CodeMirror-lines']['padding'] == 'var(--snug) 0' and full['.CodeMirror-linenumber']['padding'] == '0 var(--snug) 0 var(--near)', address + ': Full takes Snug within its row and Near at the outer number edge'


def run(site):
    for path in Path(site).rglob('*.html'):
        editor = (path.parent / 'codemirror.css').read_text()
        page = path.read_text()
        check(page, editor, str(path))
        # The law must bite on each independent obligation on the finished page.
        for old, new, source in [
            ('<details><summary>browser copy', '<details open><summary>browser copy', 'page'),
            ('font:var(--control);line-height:1', 'font:var(--brand);line-height:1', 'page'),
            ('max-width:none', 'max-width:100%', 'page'),
            ('flex-direction:column;align-items:stretch', 'flex-direction:row;align-items:stretch', 'page'),
            ('#view-seg,#keys-btn{order:1}', '#view-seg,#keys-btn{order:0}', 'page'),
            ('.CodeMirror-lines{padding:var(--snug) 0}', '.CodeMirror-lines{padding:var(--near) 0}', 'editor'),
        ]:
            text = page if source == 'page' else editor
            assert old in text, str(path) + ': layout negative control lost its subject'
            changed = text.replace(old, new, 1)
            try:
                check(changed if source == 'page' else page, changed if source == 'editor' else editor, str(path))
            except AssertionError:
                pass
            else:
                raise AssertionError(str(path) + ': layout control was accepted: ' + old)


if __name__ == '__main__':
    import sys
    run(sys.argv[1])
