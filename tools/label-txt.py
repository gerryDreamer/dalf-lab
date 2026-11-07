#!/usr/bin/env python3
"""
tools/label-txt.py — Parsing du TXT Édito C1 (v7).

Version 7 :
- page_n = n (pas n - 1) : le pied de page indique la page elle-même
- RE_CORRIGE stricte : liste de titres connus
- Essayer transcription ET corrigé sur chaque ligne

Usage :
    python3 tools/label-txt.py [txt_path]
"""
import json
import re
import sys
import os

# ─── Profil Édito C1 ───
THEMES = [
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

RANGES = {
    "transcription_audio": (198, 217),
    "transcription_video": (218, 221),
    "corrige":             (222, 237),
}

# ─── Regex ───

# Marque de page : "12 I douze", "198 I cent..."
RE_PAGE_MARK = re.compile(r"(\d{1,3})\s+I\s*\w+")

# Conteneur : ligne isolée "A", "B", "C"
RE_CONTAINER = re.compile(r"^[A-Z]$")

# Section
RE_SECTION = re.compile(
    r"^\s*(?:\d+\s+)?(Compréhension audiovisuelle|Compréhension orale|Compréhension écrite|"
    r"Production orale|Production écrite|Grammaire|Vocabulaire|Francophonie|"
    r"Fiche méthodologique|Atelier médiation|Documents|Cahier d'activités|"
    r"Produire|À bâtons rompus)\s*$",
    re.I,
)

# Question
RE_QUESTION = re.compile(r"^\s*(\d{1,2})\s+([A-ZÀ-Ý].{5,})$")

# Transcription : "Page 14, C – Titre"
RE_TRANSCRIPTION = re.compile(r"Page\s+(\d+),\s*([A-Z])\s*[–\-]\s*(.+)$")

# Corrigé : "Page 17, Vocabulaire" — titres connus uniquement
RE_CORRIGE = re.compile(
    r"Page\s+(\d+),\s*(Vocabulaire|Grammaire|À bâtons rompus|Produire|"
    r"Compréhension orale|Compréhension écrite|Production orale|Production écrite|"
    r"Francophonie|Fiche méthodologique|Atelier médiation)\b",
    re.I,
)

# Thème
RE_THEME = re.compile(r"^Th[eè]me\s+(\d+)\s+p\.\s*(\d+)", re.I)
RE_THEME_SIMPLE = re.compile(r"^Th[eè]me\s+(\d+)\s*$", re.I)


def normalize_line(line):
    line = line.replace("\u00a0", " ").replace("\u202f", " ").replace("\u200b", " ")
    line = line.replace("ﬁ", "fi").replace("ﬂ", "fl")
    line = line.replace("ﬀ", "ff").replace("ﬃ", "ffi").replace("ﬄ", "ffl")
    line = line.replace("’", "'").replace("‘", "'")
    line = line.replace("–", "-").replace("—", "-")
    line = re.sub(r"[ \t]+", " ", line)
    return line.strip()


def theme_of_page(page_n):
    if page_n is None:
        return None
    for t in THEMES:
        a, b = t["pages"]
        if a <= page_n <= b:
            return t["n"]
    return None


def parse_txt(txt_path):
    with open(txt_path, encoding="utf-8") as f:
        raw = f.read()

    # Normalisation globale
    raw = raw.replace("\u00a0", " ").replace("\u202f", " ").replace("\u200b", " ")
    raw = raw.replace("ﬁ", "fi").replace("ﬂ", "fl")
    raw = raw.replace("ﬀ", "ff").replace("ﬃ", "ffi").replace("ﬄ", "ffl")
    raw = raw.replace("’", "'").replace("‘", "'")
    raw = raw.replace("–", "-").replace("—", "-")

    # Debug
    n_trans_lines = sum(1 for l in raw.split("\n") if re.search(r"Page\s+\d+,\s*[A-Z]\s*[–\-]", l))
    n_corr_lines = sum(1 for l in raw.split("\n") if re.search(r"Page\s+\d+,\s*(Vocabulaire|Grammaire|À bâtons rompus|Produire)", l, re.I))
    print(f"  Lignes 'Page XX, [A-Z] - ...' : {n_trans_lines}")
    print(f"  Lignes 'Page XX, Titre'       : {n_corr_lines}")

    # Découper par pages
    pages_raw = re.split(r"-{10,}", raw.replace("\f", "\n--------PAGE--------\n"))
    print(f"  {len(pages_raw)} pages détectées")

    themes_data = {t["n"]: {
        "n": t["n"], "titre": t["titre"], "pages": t["pages"],
        "conteneurs": [], "sections_directes": [],
    } for t in THEMES}

    transcriptions = []
    corriges = []

    current_theme = None
    current_conteneur = None
    current_section = None
    pending_question = None
    last_page_n = None

    def flush_question():
        nonlocal pending_question
        if pending_question and current_section is not None:
            current_section["questions"].append(pending_question)
        pending_question = None

    def flush_section():
        nonlocal current_section
        flush_question()
        current_section = None

    def flush_conteneur():
        nonlocal current_conteneur
        flush_section()
        if current_conteneur and current_conteneur["sections"]:
            if current_theme is not None:
                themes_data[current_theme]["conteneurs"].append(current_conteneur)
        current_conteneur = None

    for page_idx, page_raw in enumerate(pages_raw):
        page_lines = [normalize_line(l) for l in page_raw.split("\n")]
        page_lines = [l for l in page_lines if l]

        if not page_lines:
            continue

        # Détecter le numéro de page : prendre le MAX
        page_n = None
        for line in page_lines:
            m = RE_PAGE_MARK.search(line)
            if m:
                n = int(m.group(1))
                if 1 <= n <= 250 and (page_n is None or n > page_n):
                    page_n = n

        # Pas de -1 : le pied de page indique la page elle-même
        if page_n is None and last_page_n is not None:
            page_n = last_page_n + 1
        if page_n is not None:
            last_page_n = page_n

        page_theme = theme_of_page(page_n)
        if page_theme is not None and current_theme != page_theme:
            flush_conteneur()
            current_theme = page_theme

        for line in page_lines:
            # Thème explicite
            m = RE_THEME.match(line) or RE_THEME_SIMPLE.match(line)
            if m:
                n = int(m.group(1))
                if n in themes_data:
                    flush_conteneur()
                    current_theme = n
                continue

            # ── Essayer transcription ET corrigé sur chaque ligne ──
            m = RE_TRANSCRIPTION.search(line)
            if m and len(m.group(3)) > 3:
                page_livre = int(m.group(1))
                titre = m.group(3).strip()
                # Déduire source (audio ou video)
                source = "audio"
                if page_n and 218 <= page_n <= 221:
                    source = "video"
                if not any(t["page_livre"] == page_livre and t["titre"] == titre for t in transcriptions):
                    transcriptions.append({
                        "page_livre": page_livre,
                        "document": m.group(2),
                        "titre": titre,
                        "page_pdf": page_n,
                        "source": source,
                        "theme": theme_of_page(page_livre),
                        "texte": [],
                    })
                continue

            m = RE_CORRIGE.search(line)
            if m:
                page_livre = int(m.group(1))
                titre = m.group(2).strip()
                if not any(c["page_livre"] == page_livre and c["titre"] == titre for c in corriges):
                    corriges.append({
                        "page_livre": page_livre,
                        "titre": titre,
                        "page_pdf": page_n,
                        "theme": theme_of_page(page_livre),
                        "texte": [],
                    })
                continue

            # ── Contenu du manuel ──
            if current_theme is None:
                continue

            # Conteneur ?
            if RE_CONTAINER.match(line):
                flush_conteneur()
                current_conteneur = {
                    "etiquette": line,
                    "titre": "",
                    "page": page_n,
                    "sections": [],
                }
                continue

            # Titre du conteneur
            if current_conteneur and not current_conteneur["titre"]:
                if line in ("À", "[]", "Documents", "A", "B", "C") or len(line) < 5:
                    continue
                if RE_PAGE_MARK.match(line):
                    continue
                if not RE_SECTION.match(line) and not RE_QUESTION.match(line):
                    current_conteneur["titre"] = line
                    continue

            # Section ?
            m = RE_SECTION.match(line)
            if m:
                flush_section()
                sec_name = m.group(1).lower().replace(" ", "_")
                target = (current_conteneur["sections"]
                          if current_conteneur
                          else themes_data[current_theme]["sections_directes"])
                target.append({"type": sec_name, "page": page_n, "questions": []})
                current_section = target[-1]
                continue

            # Question ?
            m = RE_QUESTION.match(line)
            if m and current_section is not None:
                flush_question()
                pending_question = {"n": int(m.group(1)), "texte": m.group(2).strip()}
                continue

            if pending_question is not None:
                pending_question["texte"] += " " + line

    flush_conteneur()

    for t in transcriptions + corriges:
        t["texte"] = "\n".join(t["texte"]).strip()

    return themes_data, transcriptions, corriges


def main(txt_path, out_dir="data"):
    if not os.path.exists(txt_path):
        print(f"❌ Fichier introuvable : {txt_path}", file=sys.stderr)
        sys.exit(1)

    print(f"📖 Parsing : {txt_path}")
    themes_data, transcriptions, corriges = parse_txt(txt_path)

    os.makedirs(out_dir, exist_ok=True)

    manuel = {"themes": [themes_data[t["n"]] for t in THEMES]}
    with open(os.path.join(out_dir, "edito-c1.manuel.json"), "w", encoding="utf-8") as f:
        json.dump(manuel, f, ensure_ascii=False, indent=2)

    ressources = {"transcriptions": transcriptions, "corriges": corriges}
    with open(os.path.join(out_dir, "edito-c1.ressources.json"), "w", encoding="utf-8") as f:
        json.dump(ressources, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Écrit dans {out_dir}/")
    print(f"\n📊 Statistiques :")
    for t in manuel["themes"]:
        nq = sum(len(s["questions"]) for c in t["conteneurs"] for s in c["sections"])
        ns = sum(len(c["sections"]) for c in t["conteneurs"])
        nd = len(t["sections_directes"])
        print(f"  Thème {t['n']:2} : {len(t['conteneurs'])} conteneurs, {ns} sections, {nq} questions, {nd} sections directes")

    print(f"\n  Transcriptions : {len(transcriptions)}")
    print(f"  Corrigés       : {len(corriges)}")


if __name__ == "__main__":
    txt_path = sys.argv[1] if len(sys.argv) > 1 else "text-edito.txt"
    main(txt_path)
