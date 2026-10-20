"""Read the finished site, including editor CSS, rather than just its template.

The generated ladder must equal the native bench's answer. Drawing SVGs have
their own pending palette contract (T-0023 V2); this law reads the interface.
"""
from html.parser import HTMLParser
import json
from pathlib import Path
import re


class Styles(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sheets, self.rules, self.inline = [], [], []
        self.svg, self.style = 0, False

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'svg':
            self.svg += 1
        if self.svg:
            return
        if tag == 'link' and values.get('rel') == 'stylesheet':
            self.sheets.append(values['href'])
        if tag == 'style':
            self.style = True
        if 'style' in values:
            self.inline.append(values['style'])

    def handle_endtag(self, tag):
        if tag == 'svg':
            self.svg -= 1
        if tag == 'style':
            self.style = False

    def handle_data(self, value):
        if self.style and not self.svg:
            self.rules.append(value)


def declarations(css):
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    for selector, body in re.findall(r'([^{}]+)\{([^{}]*)\}', css):
        for item in body.split(';'):
            if ':' in item:
                name, value = item.split(':', 1)
                yield selector.strip(), name.strip(), value.strip()


def check_css(css, address, constants, known=None):
    errors = []
    for selector, prop, value in declarations(css):
        if (selector, prop, value) in constants:
            continue
        where = address + ': ' + selector + ' ' + prop + ': ' + value
        if known is not None:
            if prop.startswith('--'):
                errors.append(where + ' — a second interface token outside ladder.css')
            for name in re.findall(r'var\((--[a-z-]+)', value):
                if name not in known:
                    errors.append(where + ' — an undeclared token reference ' + name)
        if re.search(r'#[\da-fA-F]{3,8}\b|\b(?:rgba?|hsla?|color)\(', value):
            errors.append(where + ' — a colour outside the generated palette')
        elif re.search(r'\b(?:white|black|red|silver|gr[ae]y|blue|yellow|green|orange|purple|aqua|navy|teal|maroon|lime|olive|fuchsia)\b', value):
            errors.append(where + ' — a named colour outside the generated palette')
        if prop in ('font', 'font-family', 'font-size', 'line-height') and not (
                value.startswith('var(') or value in ('inherit', 'initial', 'unset')):
            errors.append(where + ' — a font outside the declared registers')
        if re.fullmatch(r'(?:padding|margin)(?:-[a-z]+)?|(?:row-|column-)?gap', prop) and re.search(r'[\d.]px\b', value):
            errors.append(where + ' — a pixel gap outside the declared ladder')
    return errors


def audit_site(root, expected_ladder):
    root = Path(root).resolve()
    registry = json.loads((Path(__file__).resolve().parent.parent / 'web/bench-technical.json').read_text())
    constants = {(r['selector'], r['property'], r['value']) for r in registry['constants']}
    known = set(re.findall(r'(--[a-z-]+)\s*:', expected_ladder)) | {'--textline', '--u', '--shade'}
    assert all(r['name'] and r['reason'] for r in registry['constants'])
    errors, sheets, pages = [], set(), list(root.rglob('*.html'))
    for page in pages:
        reader = Styles()
        reader.feed(page.read_text())
        address = str(page.relative_to(root))
        for css in reader.rules:
            errors += check_css(css, address + ' <style>', constants, known)
        for css in reader.inline:
            errors += check_css('inline{' + css + '}', address + ' style=', set(), known)
        for href in reader.sheets:
            sheet = (root / href.lstrip('/') if href.startswith('/') else page.parent / href).resolve()
            if not sheet.is_relative_to(root) or not sheet.is_file():
                errors.append(address + ': missing or external stylesheet ' + href)
            else:
                sheets.add(sheet)
    # Read even a CSS file with no link: an omitted consumer is not permission
    # for a second palette to wait beside the generated one.
    sheets.update(root.rglob('*.css'))
    for sheet in sheets:
        css = sheet.read_text()
        if sheet.name == 'ladder.css':
            if css != expected_ladder:
                errors.append(str(sheet.relative_to(root)) + ': differs from the native declared tokens')
        else:
            errors += check_css(css, str(sheet.relative_to(root)), constants, known)
    if errors:
        raise ValueError('\n'.join(errors))
    return dict(pages=len(pages), stylesheets=len(sheets), technical_constants=len(constants))
