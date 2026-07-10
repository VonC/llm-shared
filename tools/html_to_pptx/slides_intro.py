"""Slides 1-8 of the llm-shared deck.

They cover the title, the agenda, the problem, the solution, the
self-review principle and its two worked examples.

Every pixel coordinate is read from the matching slide in
docs/llm-shared_presentation.html; the Theme maps 1280x720 px onto a
13.333in x 7.5in 16:9 slide, so the numbers transfer without re-layout.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Pt

from tools.html_to_pptx.deck_parts import (
    BannerStyle,
    ExCellStyle,
    LoopLayout,
    LoopStep,
    brand_top_left,
    ex_banner,
    ex_cell,
    ex_connector,
    loop_col,
    phase_box,
)
from tools.html_to_pptx.deck_theme import (
    BLUE,
    BRAND,
    BRAND_SUB,
    GRAY,
    LIGHT,
    LIGHTBLUE,
    MUTED2,
    ORANGE,
    TEAL,
    THEME,
    TMUTED,
    TSOFT,
    WARM,
    WHITE,
)
from tools.html_to_pptx.pptx_helpers import (
    Area,
    CardStyle,
    FrameWriter,
    SlideCanvas,
    blank_slide,
    fill_background,
    run,
)

if TYPE_CHECKING:
    from pptx.presentation import Presentation

CENTER = PP_ALIGN.CENTER
MIDDLE = MSO_ANCHOR.MIDDLE


def _canvas(prs: Presentation) -> SlideCanvas:
    """Add a blank slide to the deck and wrap it in a SlideCanvas."""
    return SlideCanvas(blank_slide(prs), THEME)


def slide_01_title(prs: Presentation) -> None:
    """Dark title slide: brand, deck name, subtitle and date line."""
    c = _canvas(prs)
    fill_background(c.slide, BLUE)
    c.rect(Area(768, 0, 512, 5), fill=ORANGE)
    brand_top_left(c)
    w1 = c.frame(Area(0, 250, 1280, 70), anchor=MIDDLE)
    w1.add([run("llm-shared", 42, WHITE, bold=True)], align=CENTER,
           space_after=0)
    w2 = c.frame(Area(240, 340, 800, 70), anchor=MIDDLE)
    w2.add([run("Framework de développement assisté par IA", 16, TSOFT)],
           align=CENTER, space_after=2)
    w2.add([run("De l'idée brute à la release taguée", 16, TSOFT)],
           align=CENTER, space_after=0)
    w3 = c.frame(Area(0, 450, 1280, 30), anchor=MIDDLE)
    w3.add([run("Direction Informatique - 2025", 13, TMUTED)], align=CENTER,
           space_after=0)


def slide_02_agenda(prs: Presentation) -> None:
    """Agenda slide: two columns of numbered topics."""
    c = _canvas(prs)
    c.header(BRAND, BRAND_SUB, "llm-shared")
    c.title("Agenda", "Framework de développement structuré avec l'IA")
    items = [
        "Le problème du « vibe-coding »",
        "La solution : un workflow structuré",
        "Principe clé : l'auto-revue IA",
        "Vue d'ensemble du workflow",
        "Phase documentaire",
        "Phase d'implémentation",
        "Commits conventionnels & release",
        "Groundhog & automatisation",
        "Sécurité : deux garde-fous",
    ]
    col_x = [150, 700]
    y0, dy = 190, 78
    for i, text in enumerate(items):
        x = col_x[i % 2]
        y = y0 + (i // 2) * dy
        num_writer = c.frame(Area(x, y, 50, 44), anchor=MIDDLE)
        num_writer.add([run(str(i + 1), 26, ORANGE, bold=True)],
                       space_after=0)
        text_writer = c.frame(Area(x + 55, y, 420, 44), anchor=MIDDLE)
        text_writer.add([run(text, 13, BLUE, bold=True)], space_after=0)
    c.footer("llm-shared - Agenda", 2)


def slide_03_problem(prs: Presentation) -> None:
    """Problem slide: three vibe-coding cards and the refusal banner."""
    c = _canvas(prs)
    c.header(BRAND, BRAND_SUB, "1. Problème")
    c.title("Le problème du « vibe-coding »",
            "Générer du code vite sans spécifier ce qu'on veut vraiment")
    cards = [
        ("💡", "L'idée",
         "« J'ai une idée, génère-moi du code, je verrai les détails plus "
         "tard. »"),
        ("⚡", "Le code arrive vite",
         "Mais il s'appuie sur des hypothèses non écrites. Il casse au "
         "premier cas réel non prévu."),
        ("💥", "La conséquence",
         "Code sans documentation d'intention. Difficile à maintenir, à "
         "expliquer, à étendre : même par l'auteur."),
    ]
    x0, w, gap = 50, 380, 20
    for i, (icon, ct, body) in enumerate(cards):
        c.card(Area(x0 + i * (w + gap), 165, w, 190), ct, body,
               CardStyle(accent=ORANGE, icon=icon))
    c.rect(Area(50, 385, 1180, 115), fill=WARM, line=ORANGE, rounded=True)
    writer = c.frame(Area(60, 400, 1160, 95), anchor=MIDDLE)
    writer.add([run("⚠️ Ce que refuse le workflow", 14, ORANGE, bold=True)],
               align=CENTER, space_after=6)
    writer.add([run("Passer directement à l'implémentation sans exigence "
                    "écrite · Sans design · Sans tests · Sans scénarios "
                    "d'acceptation", 11, MUTED2)], align=CENTER,
               space_after=0)
    c.footer("llm-shared - Problème", 3)


def slide_04_solution(prs: Presentation) -> None:
    """Solution slide: the six workflow phases and two takeaway cards."""
    c = _canvas(prs)
    c.header(BRAND, BRAND_SUB, "2. Solution")
    c.title("La solution : un workflow en phases",
            "Garder la créativité, refuser le raccourci vers le code")
    phases = [
        ("1", "Brouillon", "Note libre en langage naturel", "plain"),
        ("2", "Exigence", "Document structuré + revue", "active-orange"),
        ("3", "Design", "Solution + scénarios d'acceptation", "active"),
        ("4", "Plan", "Étapes numérotées + tests", "active-orange"),
        ("5", "Implémentation", "Code + tests + auto-revue", "active"),
        ("6", "Release", "Notes + tag de version", "active-orange"),
    ]
    w, gap = 178, 18
    total = len(phases) * w + (len(phases) - 1) * gap
    x0 = (1280 - total) / 2
    y = 165
    for i, phase in enumerate(phases):
        x = x0 + i * (w + gap)
        phase_box(c, Area(x, y, w, 150), phase)
        if i < len(phases) - 1:
            c.arrow(Area(x + w, y + 55, gap, 20), glyph="→", size=16)
    c.card(Area(50, 355, 580, 175), "Chaque phase laisse une trace",
           "Brouillon, exigence, design, plan, validation, commits groupés : "
           "le workflow double comme documentation du processus de "
           "développement.", CardStyle(accent=BLUE))
    c.card(Area(650, 355, 580, 175), "Compatible avec tout LLM",
           "Les commandes slash se résolvent en markdown brut. Copilot, "
           "Claude Code, ChatGPT Codex : tout agent qui lit et écrit des "
           "fichiers peut suivre le workflow.", CardStyle(accent=ORANGE))
    c.footer("llm-shared - Solution", 4)


def slide_05_review(prs: Presentation) -> None:
    """Self-review principle: the two review loops side by side."""
    c = _canvas(prs)
    c.header(BRAND, BRAND_SUB, "3. Auto-revue")
    c.title("Principe clé : l'IA révise son propre travail",
            "Ne jamais faire confiance au premier passage : même pour la "
            "documentation")
    left = [
        LoopStep("Écriture du document", "filled"),
        LoopStep("IA pose des questions ouvertes", "orange",
                 note="[STOP] Humain répond", note_color=ORANGE),
        LoopStep("Consolidation des réponses", "plain",
                 note="↻ Nouvelles questions ? Boucle", note_color=BLUE),
        LoopStep("Document validé ✓", "filled-orange"),
    ]
    right = [
        LoopStep("Génération du code", "filled"),
        LoopStep("Vérification : code = plan ?", "orange",
                 note="[STOP] Écarts détectés ?", note_color=ORANGE),
        LoopStep("Corrections itératives", "plain",
                 note="↻ Vérification jusqu'à conformité", note_color=BLUE),
        LoopStep("Étape validée ✓", "filled-orange"),
    ]
    loop_col(c, LoopLayout(cx=340, y0=230), "Revue documentaire", None, left)
    loop_col(c, LoopLayout(cx=940, y0=230), "Revue d'implémentation", None,
             right)
    c.footer("llm-shared - Auto-revue", 5)


def slide_06_review_practice(prs: Presentation) -> None:
    """Self-review in practice: the two dedicated skills, step by step."""
    c = _canvas(prs)
    c.header(BRAND, BRAND_SUB, "3. Auto-revue")
    c.title("L'auto-revue en pratique : deux skills dédiés",
            "/review-ask-questions relit le document, /implementation-check "
            "relit le code")
    left = [
        LoopStep("Question : contexte & problème", "filled"),
        LoopStep("Reformulation BBQ des enjeux", "plain"),
        LoopStep("Options X1 / X2 / X3 : pour & contre", "orange"),
        LoopStep("Option recommandée + arguments", "plain",
                 note="[STOP] Humain répond", note_color=ORANGE),
        LoopStep("Réponse : option XY + tableau récap ✓", "filled-orange"),
    ]
    right = [
        LoopStep("Verdict : Oui / Non - étape N", "filled"),
        LoopStep("Ce qui est fait / travail manquant", "orange",
                 note="[STOP] Écarts → implement-missing", note_color=ORANGE),
        LoopStep("Architecture DDD-Hexagonal", "plain"),
        LoopStep("Performance : pas de O(n²)", "plain"),
        LoopStep("Couverture unitaire 100% ?", "plain"),
        LoopStep("Intégrité fonctionnelle préservée ✓", "filled-orange"),
    ]
    sub_l = [run("l'IA relit ce qu'elle vient de rédiger : ", 9, GRAY,
                 italic=True),
             run("/review-ask-questions", 9, ORANGE, italic=True)]
    sub_r = [run("l'IA relit ce qu'elle vient de coder : ", 9, GRAY,
                 italic=True),
             run("/implementation-check", 9, ORANGE, italic=True)]
    loop_col(c, LoopLayout(cx=340, y0=235, box_h=38), "Revue documentaire",
             sub_l, left)
    loop_col(c, LoopLayout(cx=940, y0=235, box_h=38),
             "Revue d'implémentation", sub_r, right)
    c.footer("llm-shared - Auto-revue en pratique", 6)


def slide_07_doc_example(prs: Presentation) -> None:
    """Documentary self-review example: the my-project Q01 walkthrough."""
    c = _canvas(prs)
    c.header(BRAND, BRAND_SUB, "3. Auto-revue")
    c.title("Auto-revue documentaire : un exemple réel",
            "my-project v9.1.0 « date validation » : de la phrase ambiguë à "
            "la décision tracée")
    ex_banner(c, Area(50, 152, 1180, 52),
              ("AVANT",
               '"If the date in the filename is invalid, the file is renamed '
               '_DATE_INCOHERENTE and not processed."'),
              BannerStyle(WARM, ORANGE, ORANGE),
              [run("  — « invalid » cache deux cas différents.", 11, ORANGE)])
    ex_connector(c, 208, [run("/review-ask-questions", 10, ORANGE, bold=True),
                          run(" : l'IA détecte l'ambiguïté et pose Q01", 10,
                              GRAY)])
    # Q01: the wordy phrasing next to the readable one
    ex_cell(c, Area(50, 232, 580, 80), "Q01 — version verbeuse",
            [[run('"Should an eight-digit token failing calendar-level '
                  'plausibility verification be assimilated to the '
                  'incoherence semantics of the ten-year window rule…?"',
                  10, MUTED2)]],
            ExCellStyle(LIGHTBLUE, BLUE))
    ex_cell(c, Area(650, 232, 580, 80), "Q01 — la même, lisible",
            [[run('"When the token is not a real date (like 32132024): '
                  'block the file, or just use today\'s date?"', 10,
                  MUTED2)]],
            ExCellStyle(LIGHTBLUE, BLUE, accent=ORANGE))
    # options with pros and cons; A2 carries the recommendation border
    ex_cell(c, Area(50, 318, 380, 84), "A1 — Block the file",
            [[run("✓ operator sees every odd token", 10, MUTED2)],
             [run("✗ goes beyond the CDC rule", 10, MUTED2)]],
            ExCellStyle(LIGHT, BLUE))
    ex_cell(c, Area(450, 318, 380, 84), "A2 — Use today's date ★",
            [[run("✓ matches the CDC, backward compatible", 10, MUTED2)],
             [run("✗ a typo is processed silently", 10, MUTED2)]],
            ExCellStyle(LIGHTBLUE, BLUE, line=BLUE))
    ex_cell(c, Area(850, 318, 380, 84), "A3 — Fuzzy typo filter",
            [[run("✓ catches likely typos", 10, MUTED2)],
             [run("✗ arbitrary, hard to test", 10, MUTED2)]],
            ExCellStyle(LIGHT, BLUE))
    # the pre-filled answer and the free human choice
    ex_cell(c, Area(50, 408, 580, 72), "Réponse pré-remplie par l'IA",
            [[run('"Answer to Q01: option A2 — matches the CDC scope and '
                  'the behavior in production."', 10, MUTED2)]],
            ExCellStyle(LIGHT, BLUE))
    ex_cell(c, Area(650, 408, 580, 72), "[STOP] Réponse humaine — libre",
            [[run('"Answer to Q01: A4 — today\'s date, but log a WARNING." ',
                  10, MUTED2),
              run("Un 4e choix est permis.", 10, MUTED2)]],
            ExCellStyle(WARM, ORANGE))
    ex_connector(c, 484,
                 [run("/consolidate-then-review-ask-questions", 10, ORANGE,
                      bold=True),
                  run(" : la réponse est pliée dans le document", 10, GRAY)])
    # one-row decision table
    c.rect(Area(50, 508, 1180, 62), fill=LIGHT, rounded=True)
    cols = [
        (66, 50, "ID", "Q01"),
        (126, 360, "Question", "Impossible date: incoherent or missing?"),
        (496, 250, "Chosen option", "A2 + WARNING (A4)"),
        (756, 460, "Rationale",
         'CDC scopes "incoherent" to the 10-year window.'),
    ]
    for x, w, head, value in cols:
        writer = c.frame(Area(x, 514, w, 50))
        writer.add([run(head, 10, BLUE, bold=True)], space_after=2)
        writer.add([run(value, 9.5, MUTED2)], space_after=0)
    ex_banner(c, Area(50, 576, 1180, 56),
              ("APRÈS",
               '"A real date outside [today - 10 years, today] → file '
               'renamed, not processed. A token that is not a real date → '
               'missing date: the process starts with today\'s date."'),
              BannerStyle(TEAL, None, WHITE))
    c.footer("llm-shared - Auto-revue : exemple documentaire", 7)


def slide_08_impl_example(prs: Presentation) -> None:
    """Implementation self-review example: the missing-wire walkthrough."""
    c = _canvas(prs)
    c.header(BRAND, BRAND_SUB, "3. Auto-revue")
    c.title("Auto-revue d'implémentation : un exemple réel",
            "my-project v9.11.0 : le plan disait « fait », la revue du "
            "comportement réel a trouvé le morceau manquant")
    ex_cell(c, Area(50, 170, 580, 110), "🎯 Ce que le plan demandait",
            [[run("Show the preparation progress in two places: the live "
                  "widget on screen, and the progress log file that "
                  "operators read.", 11, MUTED2)]],
            ExCellStyle(LIGHTBLUE, BLUE, hsize=13))
    ex_cell(c, Area(650, 170, 580, 110), "AVANT — Implémenté au premier jet",
            [[run("The widget shows the progress, live. The log file is "
                  "ready to display it too. All tests are green. ✓", 11,
                  MUTED2)]],
            ExCellStyle(WARM, ORANGE, line=ORANGE, hsize=13))
    ex_connector(c, 292, [run("/implementation-check", 10, ORANGE, bold=True),
                          run(" + revue du comportement réel → ", 10, GRAY),
                          run("verdict : Non", 10, ORANGE, bold=True)])
    ex_cell(c, Area(50, 320, 580, 200), "🔍 L'écart détecté par la revue",
            [[run("The log file never receives the progress. The widget "
                  "moves forward, but the file stays frozen on an old "
                  "value. The display side was built — the part that "
                  "writes the progress into the file was not.", 10.5,
                  MUTED2)],
             [run("Why did it slip through? ", 10.5, ORANGE, bold=True),
              run("The AI built each half separately — and tested each "
                  "half separately: the widget with live data, the log "
                  "display with a hand-written file. Both halves pass. The "
                  "wire between them was never written, so no test could "
                  "fail.", 10.5, MUTED2)]],
            ExCellStyle(WHITE, ORANGE, line=ORANGE, dashed=True, hsize=13))
    ex_cell(c, Area(650, 320, 580, 200), "🔧 Le correctif",
            [[run("One fix commit: recognize the progress signal during "
                  "preparation, pass the counters to the file before each "
                  "write, and keep a preparation update from blocking the "
                  "next splitting update.", 10.5, MUTED2)],
             [run("Plus the missing test: ", 10.5, BLUE, bold=True),
              run("a new test now follows the progress end to end, from "
                  "the running phase to the file content — the gap can no "
                  "longer come back.", 10.5, MUTED2)]],
            ExCellStyle(LIGHTBLUE, BLUE, hsize=13))
    ex_connector(c, 532, [run("nouvelle passe ", 10, GRAY),
                          run("/implementation-check", 10, ORANGE, bold=True),
                          run(" → ", 10, GRAY),
                          run("verdict : Oui", 10, TEAL, bold=True)])
    b = c.rect(Area(50, 560, 1180, 70), fill=TEAL, rounded=True)
    tf = b.text_frame
    tf.vertical_anchor = MIDDLE
    tf.word_wrap = True
    tf.margin_left = Pt(10)
    writer = FrameWriter(tf, THEME)
    writer.add([run("APRÈS   ", 11, WHITE, bold=True),
                run("The log file now moves at the same pace as the "
                    "widget: operators see the same progress in both "
                    "places. Three new tests lock the behavior — full "
                    "suite green, coverage 100%.", 11, WHITE)],
               space_after=0, line_spacing=1.1)
    c.footer("llm-shared - Auto-revue : exemple implémentation", 8)


def add_intro_slides(prs: Presentation) -> None:
    """Add slides 1 to 8 to the deck, in order."""
    slide_01_title(prs)
    slide_02_agenda(prs)
    slide_03_problem(prs)
    slide_04_solution(prs)
    slide_05_review(prs)
    slide_06_review_practice(prs)
    slide_07_doc_example(prs)
    slide_08_impl_example(prs)


# eof
