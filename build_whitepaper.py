"""Render the English Markdown source as the published FixedCoin whitepaper."""
from pathlib import Path
import argparse
import html
import re

import reportlab
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    Preformatted, KeepTogether,
)

ROOT = Path(__file__).resolve().parent
NAVY = colors.HexColor('#182C40')
GOLD = colors.HexColor('#B98120')
INK = colors.HexColor('#243444')
MUTED = colors.HexColor('#526477')
PALE = colors.HexColor('#F2F5F8')
RULE = colors.HexColor('#DCE3E9')
LINK = colors.HexColor('#176A92')
WIDTH, HEIGHT = A4
MARGIN = 48
CONTENT = WIDTH - 2 * MARGIN

fontdir = Path(reportlab.__file__).resolve().parent / 'fonts'
for name, filename in [('Body', 'Vera.ttf'), ('Body-Bold', 'VeraBd.ttf'), ('Body-Italic', 'VeraIt.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(fontdir / filename)))
pdfmetrics.registerFontFamily('Body', normal='Body', bold='Body-Bold', italic='Body-Italic', boldItalic='Body-Bold')

styles = {
    'body': ParagraphStyle('body', fontName='Body', fontSize=9.35, leading=13.2,
                           textColor=INK, spaceAfter=7, allowWidows=0, allowOrphans=0),
    'h1': ParagraphStyle('h1', fontName='Body-Bold', fontSize=35, leading=43,
                         textColor=NAVY, spaceBefore=19, spaceAfter=8),
    'h2': ParagraphStyle('h2', fontName='Body-Bold', fontSize=18, leading=23,
                         textColor=NAVY, spaceBefore=7, spaceAfter=12, keepWithNext=True),
    'h3': ParagraphStyle('h3', fontName='Body-Bold', fontSize=11, leading=15,
                         textColor=NAVY, spaceBefore=7, spaceAfter=6, keepWithNext=True),
    'cell': ParagraphStyle('cell', fontName='Body', fontSize=8.3, leading=11,
                           textColor=INK, spaceAfter=0),
    'cell_head': ParagraphStyle('cell_head', fontName='Body-Bold', fontSize=8.2,
                                leading=11, textColor=colors.white),
    'code': ParagraphStyle('code', fontName='Courier', fontSize=8.3, leading=11.6,
                           textColor=NAVY, backColor=PALE, borderPadding=9,
                           spaceBefore=4, spaceAfter=11),
    'reference': ParagraphStyle('reference', fontName='Body', fontSize=8.05,
                                leading=11.3, textColor=MUTED, spaceAfter=5),
}


def inline(text):
    text = html.escape(text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)',
                  lambda m: f'<link href="{m[2]}" color="#176A92">{m[1]}</link>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'`([^`]+)`', r'<font name="Courier">\1</font>', text)
    return text


def table(lines, section):
    rows = [[x.strip() for x in line.strip().strip('|').split('|')] for line in lines]
    rows = [r for r in rows if not all(re.fullmatch(r':?-+:?', c.replace(' ', '')) for c in r)]
    n = len(rows[0])
    if n == 4:
        widths = [37, 147, 116, CONTENT - 300]
    elif n == 3:
        widths = [CONTENT / 3] * 3 if section == 0 else [108, (CONTENT - 108) / 2, (CONTENT - 108) / 2]
    else:
        widths = [186, CONTENT - 186] if section == 2 else [168, CONTENT - 168]
    rendered = [[Paragraph(inline(c), styles['cell_head'] if i == 0 else styles['cell'])
                 for c in r] for i, r in enumerate(rows)]
    t = Table(rendered, colWidths=widths, repeatRows=1, hAlign='LEFT')
    padding = 3.0 if section == 3 else 4.6
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [PALE, colors.white]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), padding),
        ('BOTTOMPADDING', (0, 0), (-1, -1), padding),
        ('LINEBELOW', (0, -1), (-1, -1), 0.5, RULE),
    ]))
    return t


def story_from_markdown(source):
    lines = source.splitlines()
    story = []
    i = 0
    section = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line == '<!-- pagebreak -->':
            story.append(PageBreak())
            section += 1
            i += 1
            continue
        if line.startswith('```'):
            code = []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                code.append(lines[i])
                i += 1
            story.append(Preformatted('\n'.join(code), styles['code']))
            i += 1
            continue
        if line.startswith('|'):
            group = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                group.append(lines[i])
                i += 1
            story.extend([Spacer(1, 3), table(group, section), Spacer(1, 10)])
            continue
        heading = re.match(r'^(#{1,3}) (.*)', line)
        if heading:
            story.append(Paragraph(inline(heading[2]), styles['h' + str(len(heading[1]))]))
            i += 1
            continue
        paragraph = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(('#', '|', '```', '<!--')):
            # Numbered contents are separate paragraphs rather than a dense run-on line.
            if re.match(r'^\d+\. ', lines[i]):
                break
            paragraph.append(lines[i].strip())
            i += 1
        value = ' '.join(paragraph)
        style = styles['reference'] if re.match(r'^\[\d+\]', value) else styles['body']
        story.append(Paragraph(inline(value), style))
    return story


def page(canvas, doc):
    canvas.saveState()
    canvas.setTitle('FixedCoin Technical Whitepaper - Core v30.0.0')
    canvas.setAuthor('FixedCoin Team')
    canvas.setSubject('Historical consensus, mainnet activation at block 52,560, and v30 rules')
    canvas.setFillColor(GOLD)
    canvas.rect(MARGIN, HEIGHT - 35, 25, 3, fill=1, stroke=0)
    canvas.setFont('Body-Bold', 8)
    canvas.setFillColor(NAVY)
    canvas.drawString(MARGIN + 35, HEIGHT - 35, 'FIXEDCOIN')
    canvas.setFont('Body', 7.8)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(WIDTH - MARGIN, HEIGHT - 35, 'TECHNICAL WHITEPAPER  /  V30.0.0')
    canvas.setStrokeColor(RULE)
    canvas.line(MARGIN, 40, WIDTH - MARGIN, 40)
    canvas.setFont('Body', 7.1)
    canvas.drawString(MARGIN, 27, 'FixedCoin Team  |  7 November 2026  |  Mainnet')
    canvas.drawRightString(WIDTH - MARGIN, 27, str(doc.page))
    canvas.restoreState()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'FixedCoin_Whitepaper.pdf')
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(args.output), pagesize=A4, leftMargin=MARGIN,
                            rightMargin=MARGIN, topMargin=55, bottomMargin=54,
                            title='FixedCoin Technical Whitepaper - Core v30.0.0',
                            author='FixedCoin Team', pageCompression=1)
    doc.build(story_from_markdown((ROOT / 'FixedCoin_Whitepaper.md').read_text(encoding='utf-8')),
              onFirstPage=page, onLaterPages=page)
    print(args.output)


if __name__ == '__main__':
    main()
