"""Reusable primitives to rebuild an HTML slide deck as a native, editable
PowerPoint deck made of text boxes and vector autoshapes only -- no images.

Why this module exists:
    A browser-rendered HTML deck can be turned into a .pptx in two ways. One
    screenshots each slide and drops the picture on a slide: pixel-faithful
    but frozen -- nobody can edit a word in PowerPoint. The other rebuilds
    each slide from real PowerPoint objects: text frames, rounded rectangles,
    ovals, colored bars. This module is the toolbox for the second way, so
    every title, bullet and box stays editable while still matching the look
    of the source HTML.

    The trick that keeps the visual match cheap: an HTML deck authored on a
    fixed pixel canvas (here 1280x720) maps one-to-one onto a 16:9 PowerPoint
    slide (13.333in x 7.5in). 1 px == 13.333/1280 in horizontally and
    7.5/720 in vertically, and for a matched aspect ratio those two factors
    are equal. So the pixel x/y/width/height read straight out of the HTML
    become slide coordinates through Theme.inx / Theme.iny -- no re-layout,
    no guessing.

How to use it:
    Build a Theme with your brand colors and canvas size, then compose slides
    from the primitives (textbox, rect, oval, box, arrow) and the ready-made
    components (card, feature_item, header, title, footer). See
    build_llm_shared_pptx.py in this folder for a full 13-slide worked
    example, and README.md for the step-by-step method.
"""

from dataclasses import dataclass, field

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE


def rgb(hex6):
    """Return an RGBColor from a 6-char hex string such as '00566f'."""
    return RGBColor(int(hex6[0:2], 16), int(hex6[2:4], 16), int(hex6[4:6], 16))


@dataclass
class Theme:
    """Brand colors, fonts and canvas geometry shared by every slide.

    Args:
        primary: main brand color (titles, brand name, filled boxes).
        accent: secondary color for highlights and the right accent bar.
        muted: gray used for subtitles, topic tags and secondary text.
        faint: light gray used for the footer line and page number.
        white: text color used on filled brand/accent boxes.
        font: font family applied to every run.
        canvas_px_w / canvas_px_h: pixel size of the source HTML slide.
        slide_in_w / slide_in_h: target PowerPoint slide size in inches.
        extra: free dict for any additional named colors the deck needs
            (light backgrounds, teal, dark code panel, and so on).
    """

    primary: RGBColor
    accent: RGBColor
    muted: RGBColor
    faint: RGBColor
    white: RGBColor = field(default_factory=lambda: rgb("ffffff"))
    font: str = "Segoe UI"
    canvas_px_w: int = 1280
    canvas_px_h: int = 720
    slide_in_w: float = 13.333
    slide_in_h: float = 7.5
    extra: dict = field(default_factory=dict)

    def inx(self, px):
        """Convert a horizontal pixel position/size to slide inches."""
        return Inches(px * self.slide_in_w / self.canvas_px_w)

    def iny(self, px):
        """Convert a vertical pixel position/size to slide inches."""
        return Inches(px * self.slide_in_h / self.canvas_px_h)


# --- presentation and slide scaffolding ------------------------------------
def make_presentation(theme):
    """Return a new Presentation sized to the theme (defaults to 16:9)."""
    prs = Presentation()
    prs.slide_width = Inches(theme.slide_in_w)
    prs.slide_height = Inches(theme.slide_in_h)
    return prs


def blank_slide(prs):
    """Add and return a slide using the blank layout (index 6)."""
    return prs.slides.add_slide(prs.slide_layouts[6])


def fill_background(slide, color):
    """Paint the whole slide background one solid color (title slides)."""
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


# --- text ------------------------------------------------------------------
def run(text, size, color, bold=False, italic=False):
    """Describe one styled text run as a tuple for add_paragraph.

    Keeping runs as plain tuples lets a single paragraph mix colors and
    weights -- for example a black sentence with an orange slash-command in
    the middle -- which is how the HTML inline <code> spans are reproduced.
    """
    return (text, size, color, bold, italic)


def add_paragraph(tf, runs, theme, align=PP_ALIGN.LEFT, first=False,
                  space_after=2, line_spacing=1.0):
    """Append (or fill the first) paragraph in a text frame from runs.

    Args:
        tf: the text_frame of a textbox or autoshape.
        runs: list of run() tuples placed side by side in one paragraph.
        theme: supplies the font family.
        first: reuse the frame's pre-existing empty paragraph instead of
            adding one (a fresh text frame always starts with one paragraph).
    """
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_after = Pt(space_after)
    p.space_before = Pt(0)
    if line_spacing:
        p.line_spacing = line_spacing
    for text, size, color, bold, italic in runs:
        r = p.add_run()
        r.text = text
        f = r.font
        f.size = Pt(size)
        f.bold = bold
        f.italic = italic
        f.color.rgb = color
        f.name = theme.font
    return p


def textbox(slide, theme, x, y, w, h, anchor=MSO_ANCHOR.TOP):
    """Add an empty textbox at pixel coordinates and return its text frame."""
    tb = slide.shapes.add_textbox(theme.inx(x), theme.iny(y),
                                  theme.inx(w), theme.iny(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = Pt(3)
    tf.margin_right = Pt(3)
    tf.margin_top = Pt(1)
    tf.margin_bottom = Pt(1)
    return tf


# --- shapes ----------------------------------------------------------------
def rect(slide, theme, x, y, w, h, fill=None, line=None, rounded=False,
         line_w=1.5):
    """Add a rectangle (optionally rounded) at pixel coordinates.

    Pass fill=None for a transparent body and line=None for no border, so the
    same helper draws a filled chip, an outlined box, or a thin colored bar.
    """
    kind = MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE
    s = slide.shapes.add_shape(kind, theme.inx(x), theme.iny(y),
                               theme.inx(w), theme.iny(h))
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(line_w)
    s.shadow.inherit = False
    return s


def oval(slide, theme, x, y, w, h, fill, line=None):
    """Add a filled circle/ellipse, used for numbered step badges."""
    s = slide.shapes.add_shape(MSO_SHAPE.OVAL, theme.inx(x), theme.iny(y),
                               theme.inx(w), theme.iny(h))
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
    s.shadow.inherit = False
    return s


def shape_text(shape, lines, theme, anchor=MSO_ANCHOR.MIDDLE, pad=4):
    """Fill a shape's text frame with a list of (runs, align, space_after).

    Centering vertically (MIDDLE) is the default because most boxes hold one
    or two short centered lines.
    """
    tf = shape.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = Pt(pad)
    tf.margin_right = Pt(pad)
    tf.margin_top = Pt(2)
    tf.margin_bottom = Pt(2)
    for i, (runs, align, sa) in enumerate(lines):
        add_paragraph(tf, runs, theme, align=align, first=(i == 0),
                      space_after=sa)
    return tf


def box(slide, theme, x, y, w, h, main, fill=None, line=None, tcolor=None,
        size=10.4, bold=True, rounded=True, sub=None, subcolor=None,
        subsize=8.0, align=PP_ALIGN.CENTER):
    """Draw a rounded box with a centered main line and optional sub line.

    This is the workhorse for flow diagrams: a filled brand box, an outlined
    box, or a two-line box (a label plus a smaller caption underneath).
    """
    tcolor = tcolor if tcolor is not None else theme.primary
    s = rect(slide, theme, x, y, w, h, fill=fill, line=line, rounded=rounded)
    lines = [([run(main, size, tcolor, bold)], align, 0)]
    if sub is not None:
        lines.append(([run(sub, subsize, subcolor or tcolor)], align, 0))
    shape_text(s, lines, theme)
    return s


def arrow(slide, theme, x, y, w, glyph="▼", color=None, size=13):
    """Place a small centered connector glyph (▼, →, 'ou', ...)."""
    color = color if color is not None else theme.muted
    tf = textbox(slide, theme, x, y, w, 20, anchor=MSO_ANCHOR.MIDDLE)
    add_paragraph(tf, [run(glyph, size, color)], theme, align=PP_ALIGN.CENTER,
                  first=True, space_after=0)


# --- reusable components ---------------------------------------------------
def card(slide, theme, x, y, w, h, ctitle, body, accent=None, icon=None,
         bg=None, title_size=13, body_size=10):
    """A rounded panel with a top accent bar, a colored title and body text.

    Mirrors the HTML .card component (top border in the accent color).
    """
    accent = accent if accent is not None else theme.primary
    bg = bg if bg is not None else theme.extra.get("light", rgb("f0f4f6"))
    rect(slide, theme, x, y, w, h, fill=bg, rounded=True)
    rect(slide, theme, x, y, w, 6, fill=accent)
    tf = textbox(slide, theme, x + 16, y + 16, w - 32, h - 28)
    if icon:
        add_paragraph(tf, [run(icon, 24, theme.extra.get("text", rgb(
            "333333")))], theme, first=True, space_after=4)
        add_paragraph(tf, [run(ctitle, title_size, accent, True)], theme,
                      space_after=6)
    else:
        add_paragraph(tf, [run(ctitle, title_size, accent, True)], theme,
                      first=True, space_after=6)
    add_paragraph(tf, [run(body, body_size, theme.extra.get(
        "muted2", rgb("555555")))], theme, space_after=0, line_spacing=1.15)


def feature_item(slide, theme, x, y, w, h, head, body, accent=None,
                 head_size=11.5, body_size=9.5):
    """A rounded panel with a left accent bar, a heading and body text.

    Mirrors the HTML .feature-item component (left border in the accent).
    """
    accent = accent if accent is not None else theme.primary
    bg = theme.extra.get("light", rgb("f0f4f6"))
    rect(slide, theme, x, y, w, h, fill=bg, rounded=True)
    rect(slide, theme, x, y, 6, h, fill=accent)
    tf = textbox(slide, theme, x + 16, y + 12, w - 26, h - 20)
    add_paragraph(tf, [run(head, head_size, theme.primary, True)], theme,
                  first=True, space_after=4)
    add_paragraph(tf, [run(body, body_size, theme.extra.get(
        "muted", rgb("666666")))], theme, space_after=0, line_spacing=1.15)


def feature_row(slide, theme, feats, y, w=380, h=110, gap=20, x0=50):
    """Lay a list of (head, body, accent) feature items in one row."""
    for i, (head, body, accent) in enumerate(feats):
        feature_item(slide, theme, x0 + i * (w + gap), y, w, h, head, body,
                     accent=accent)


# --- shared chrome (header band, title block, footer) ----------------------
def header(slide, theme, brand_name, brand_sub, topic, name_color=None,
           sub_color=None, topic_color=None, split=0.6):
    """Draw the top brand line, the topic tag and the two-tone accent bar.

    The accent bar is two rectangles: primary on the left `split` fraction,
    accent on the remainder -- the same 60/40 blue/orange split as the HTML.
    """
    name_color = name_color or theme.primary
    sub_color = sub_color or theme.muted
    topic_color = topic_color or theme.muted
    tf = textbox(slide, theme, 40, 12, 500, 40)
    add_paragraph(tf, [run(brand_name, 13, name_color, True)], theme,
                  first=True, space_after=1)
    add_paragraph(tf, [run(brand_sub, 7, sub_color)], theme, space_after=0)
    tf2 = textbox(slide, theme, 780, 20, 460, 20)
    add_paragraph(tf2, [run(topic, 8.5, topic_color)], theme,
                  align=PP_ALIGN.RIGHT, first=True, space_after=0)
    split_px = theme.canvas_px_w * split
    rect(slide, theme, 0, 58, split_px, 5, fill=theme.primary)
    rect(slide, theme, split_px, 58, theme.canvas_px_w - split_px, 5,
         fill=theme.accent)


def title(slide, theme, t, sub):
    """Draw the slide title and subtitle block below the accent bar."""
    tf = textbox(slide, theme, 50, 72, 1180, 44)
    add_paragraph(tf, [run(t, 21, theme.primary, True)], theme, first=True,
                  space_after=0)
    tf2 = textbox(slide, theme, 50, 116, 1180, 28)
    add_paragraph(tf2, [run(sub, 10.5, theme.muted)], theme, first=True,
                  space_after=0)


def footer(slide, theme, left, num):
    """Draw the bottom-left caption and the bottom-right page number."""
    tf = textbox(slide, theme, 40, 700, 500, 16)
    add_paragraph(tf, [run(left, 7.5, theme.faint)], theme, first=True,
                  space_after=0)
    tf2 = textbox(slide, theme, 1150, 700, 90, 16)
    add_paragraph(tf2, [run(str(num), 7.5, theme.faint)], theme,
                  align=PP_ALIGN.RIGHT, first=True, space_after=0)


# eof
