#!/usr/bin/env python3
"""
tools/label.py — Étiquetage automatique des colonnes extraites.

Version 3 : utilise les plages explicites ET rattache chaque
ressource à un thème (via profiles/edito-c1.json).

Usage :
    python3 tools/label.py [raw.json] [profile.json] [out_dir]
"""
import json
import re
import sys
import os
from collections import defaultdict

# ─── Valeurs par défaut (si le profil est absent) ───
DEFAULT_RANGES = {
    "transcription_audio": (198, 217),
    "transcription_video": (218, 221),
    "corrige":             (222, 237),
}
DEFAULT_THEMES = [
    {"n": 1,  "titre": "Justice, quelles alternatives ?",          "pages": [11, 22] },
    {"n": 2,  "titre": "SOS démocratie",                           "pages": [23, 38] },
    {"n": 3,  "titre": "Souffler le chaud et le froid",            "pages": [39, 50] },
    {"n": 4,  "titre": "Travail en cours",                         "pages": [51, 68] },
    {"n": 5,  "titre": "Les nouveaux visages de la culture",       "pages": [69, 80] },
    {"n": 6,  "titre": "La vie privée : un droit, une liberté ?",  "pages": [81, 98] },
    {"n": 7,  "titre": "Jouons cartes sur table !",                "pages": [99, 110] },
    {"n": 8,  "titre": "Ma belle famille !",                       "pages": [111, 126] },
    {"n": 9,  "titre": "Villes en mouvement, vies en transition",  "pages": [127, 144] },
    {"n": 10, "titre": "Santé 3.0",                                "pages": [145, 156] },
    {"n": 11, "titre": "Solidarité, un bel élan !",                "pages": [157, 168] },
    {"n": 12, "titre": "Protéger la terre, réparer le vivant",     "pages": [169, 188] },
]

RE_TRANSCRIPTION_ENTRY = re.compile(r"^Page\s+(\d+),\s*([A-Z])\s*[–\-]\s*(.+)$")
RE_CORRIGE_ENTRY       = re.compile(r"^Page\s+(\d+),\s*(.+)$")


def load_profile(path):
    """Charge le profil, ou utilise les défauts."""
    if path and os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            prof = json.load(f)
        ranges = DEFAULT_RANGES.copy()
        if "transcriptions" in prof and "pages" in prof["transcriptions"]:
            ranges["transcription_audio"] = tuple(prof["transcriptions"]["pages"]["audio"])
            ranges["transcription_video"] = tuple(prof["transcriptions"]["pages"]["video"])
        if "corriges" in prof and "pages" in prof["corriges"]:
            ranges["corrige"] = tuple(prof["corriges"]["pages"])
        themes = prof.get("themes", DEFAULT_THEMES)
        return ranges, themes
    return DEFAULT_RANGES, DEFAULT_THEMES


def page_type(page_n, ranges):
    for ptype, (start, end) in ranges.items():
        if start <= page_n <= end:
            return ptype
    return "livre"


def theme_of_page(page_n, themes):
    """Retourne le thème (n) auquel appartient une page, ou None."""
    for t in themes:
        a, b = t["pages"]
        if a <= page_n <= b:
            return t["n"]
    return None


def clean_lines(lines):
    """Filtre les lignes d'en-tête."""
    return [l["text"].strip() for l in lines
            if not re.match(r"^(Transcriptions?|Documents?\s+audios?|Documents?\s+videos?|Corriges?|Th[eè]me\s+\d+|Justice,\s+quelles)", l["text"].strip(), re.I)
            and not re.match(r"^\d{1,3}$", l["text"].strip())
            and not re.match(r"^\d{1,3}\s+(cent|I\b)", l["text"].strip())]


def extract_transcription_blocks(page, themes):
    all_lines = []
    for col in page.get("columns", []):
        all_lines.extend(clean_lines(col["lines"]))

    blocks, current = [], None
    for line in all_lines:
        m = RE_TRANSCRIPTION_ENTRY.match(line)
        if m:
            if current:
                blocks.append(current)
            current = {
                "page_livre": int(m.group(1)),
                "document": m.group(2),
                "titre": m.group(3).strip(),
                "page_pdf": page["n"],
                "lines": [],
            }
        elif current:
            current["lines"].append(line)
    if current:
        blocks.append(current)

    for b in blocks:
        b["texte"] = "\n".join(b.pop("lines")).strip()
        b["type"] = "transcription"
        b["theme"] = theme_of_page(b["page_livre"], themes)
    return blocks


def extract_corrige_blocks(page, themes):
    all_lines = []
    for col in page.get("columns", []):
        all_lines.extend(clean_lines(col["lines"]))

    blocks, current = [], None
    for line in all_lines:
        m = RE_CORRIGE_ENTRY.match(line)
        if m:
            if current:
                blocks.append(current)
            current = {
                "page_livre": int(m.group(1)),
                "titre": m.group(2).strip(),
                "page_pdf": page["n"],
                "lines": [],
            }
        elif current:
            current["lines"].append(line)
    if current:
        blocks.append(current)

    for b in blocks:
        b["texte"] = "\n".join(b.pop("lines")).strip()
        b["type"] = "corrige"
        b["theme"] = theme_of_page(b["page_livre"], themes)
    return blocks


def main(raw_path, profile_path, out_dir):
    ranges, themes = load_profile(profile_path)

    with open(raw_path, encoding="utf-8") as f:
        data = json.load(f)

    stats = defaultdict(int)
    stats_theme = defaultdict(lambda: defaultdict(int))
    ressources = []
    labeled_pages = []

    for page in data["pages"]:
        if "error" in page:
            continue

        ptype = page_type(page["n"], ranges)
        stats[ptype] += 1

        labeled_page = {"n": page["n"], "type": ptype,
                        "columns_count": len(page.get("columns", [])), "blocks": []}

        if ptype in ("transcription_audio", "transcription_video"):
            blocks = extract_transcription_blocks(page, themes)
            src = "audio" if ptype == "transcription_audio" else "video"
            for b in blocks:
                b["source"] = src
                ressources.append(b)
                stats_theme[ptype][b.get("theme")] += 1
            labeled_page["blocks"] = blocks
        elif ptype == "corrige":
            blocks = extract_corrige_blocks(page, themes)
            for b in blocks:
                ressources.append(b)
                stats_theme[ptype][b.get("theme")] += 1
            labeled_page["blocks"] = blocks

        labeled_pages.append(labeled_page)

    os.makedirs(out_dir, exist_ok=True)
    os.makedirs("data", exist_ok=True)

    res_out = {
        "source": data["source"],
        "pages_total": data["pages_total"],
        "ranges": {k: {"start": v[0], "end": v[1]} for k, v in ranges.items()},
        "themes": themes,
        "ressources": ressources,
    }
    with open("data/edito-c1.ressources.json", "w", encoding="utf-8") as f:
        json.dump(res_out, f, ensure_ascii=False, indent=2)

    with open(os.path.join(out_dir, "edito-c1.labeled.json"), "w", encoding="utf-8") as f:
        json.dump({"pages": labeled_pages}, f, ensure_ascii=False, indent=2)

    # Rapport
    lines = [
        f"Rapport d'étiquetage — {data['source']}",
        f"Pages totales : {data['pages_total']}",
        "",
        "Plages utilisées :",
    ]
    for k, (a, b) in ranges.items():
        lines.append(f"  {k:22} pages {a}–{b}  ({b-a+1} pages)")
    lines += ["", "Statistiques par type :"]
    for k, v in sorted(stats.items(), key=lambda x: -x[1]):
        lines.append(f"  {k:22} {v:4} pages")

    lines += ["", f"Ressources extraites : {len(ressources)}"]
    for r in ressources:
        th = f"T{r['theme']}" if r.get("theme") else "T?"
        lines.append(f"  [{r['type']:14}] [{th:3}] page_livre={r['page_livre']:3} pdf={r['page_pdf']:3}  {r['titre'][:60]}  ({len(r['texte'])} car.)")

    lines += ["", "Ressources par type et par thème :"]
    for ptype, by_theme in stats_theme.items():
        lines.append(f"  {ptype}:")
        for th in sorted(by_theme.keys(), key=lambda x: (x is None, x)):
            th_label = f"Thème {th}" if th else "sans thème"
            lines.append(f"    {th_label:12} {by_theme[th]:3} ressources")

    report = "\n".join(lines)
    with open(os.path.join(out_dir, "edito-c1.labeled.report.txt"), "w", encoding="utf-8") as f:
        f.write(report)
    print(report)


if __name__ == "__main__":
    raw_path = sys.argv[1] if len(sys.argv) > 1 else "tools/out/edito-c1.raw.json"
    profile_path = sys.argv[2] if len(sys.argv) > 2 else "profiles/edito-c1.json"
    out_dir = sys.argv[3] if len(sys.argv) > 3 else "tools/out"
    main(raw_path, profile_path, out_dir)
