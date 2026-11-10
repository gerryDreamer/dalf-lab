#!/usr/bin/env python3
"""
tools/label-txt.py — Parsing du TXT Édito C1 (v14).

Version 14 :
- Retrait de seen_questions (cassait les conteneurs)
- T12 A retiré (absent du TXT)
- Matching par titre exact + 3 premiers mots
- Toutes les corrections précédentes (v12)

Usage :
    python3 tools/label-txt.py [txt_path]
"""
import json
import re
import sys
import os
import unicodedata

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

PAGES_CAHIER = {
    1: (17, 22), 2: (35, 38), 3: (45, 50), 4: (61, 68),
    5: (75, 80), 6: (89, 98), 7: (105, 110), 8: (119, 126),
    9: (133, 144), 10: (149, 156), 11: (163, 168), 12: (177, 188),
}

# Pages à ignorer : table des matières (1-10) + index (238+)
IGNORE_PAGES = set(range(1, 11)) | set(range(238, 251))

# ─── Dictionnaire des conteneurs (T12 A retiré — absent du TXT) ───
CONTAINERS = {
    1: [
        {"lettre": "A", "titre": "Je verrai toujours vos visages"},
        {"lettre": "B", "titre": "Vers un horizon d'apaisement"},
        {"lettre": "C", "titre": "L'équithérapie en prison"},
    ],
    2: [
        {"lettre": "A", "titre": "Tu voteras oui ou oui au référendum"},
        {"lettre": "B", "titre": "Comment les populistes s'introduisent dans les démocraties"},
        {"lettre": "C", "titre": "La crise démocratique est devenue structurelle"},
        {"lettre": "D", "titre": "Quand les jeunes se mêlent de politique"},
        {"lettre": "E", "titre": "Tu sais pour qui tu vas voter"},
    ],
    3: [
        {"lettre": "A", "titre": "Change toujours, tu m'intéresses"},
        {"lettre": "B", "titre": "Changer de métier, oui"},
        {"lettre": "C", "titre": "Le changement, ça s'accompagne"},
    ],
    4: [
        {"lettre": "A", "titre": "Que faire contre le gaspi"},
        {"lettre": "B", "titre": "Mourir de chaud"},
        {"lettre": "C", "titre": "Petite et grande histoire du chauffage"},
        {"lettre": "D", "titre": "Kumulus, le générateur d'eau atmosphérique et solaire"},
        {"lettre": "E", "titre": "Tahiti, l'hôpital climatisé grâce à l'eau de mer"},
        {"lettre": "F", "titre": "Ça nous paraît aberrant d'arroser l'hiver"},
    ],
    5: [
        {"lettre": "A", "titre": "Les jeunes et la culture"},
        {"lettre": "B", "titre": "Les publics des musées, visiteurs ou acteurs"},
        {"lettre": "C", "titre": "Liseuse versus livre, le match"},
    ],
    6: [
        {"lettre": "A", "titre": "Les jouets ont-ils un genre"},
        {"lettre": "B", "titre": "C'est quoi, le féminisme"},
        {"lettre": "C", "titre": "Une bibliothèque féministe"},
        {"lettre": "D", "titre": "Être un homme aujourd'hui"},
        {"lettre": "E", "titre": "Vie commune"},
        {"lettre": "F", "titre": "On ne peut plus rien dire"},
    ],
    7: [
        {"lettre": "A", "titre": "Requiem pour un joueur"},
        {"lettre": "B", "titre": "Jouer pour guérir"},
        {"lettre": "C", "titre": "Le jeu des 1 000 euros"},
    ],
    8: [
        {"lettre": "A", "titre": "Mode d'emploi pour les grands-parents"},
        {"lettre": "B", "titre": "Alors, cette rentrée"},
        {"lettre": "C", "titre": "Ils ont un enfant à trois et ne vivent pas ensemble"},
        {"lettre": "D", "titre": "Belles-mères, les grandes invisibles"},
        {"lettre": "E", "titre": "Belles-mères au bord de la crise de nerfs"},
        {"lettre": "F", "titre": "Sous contrôle parental"},
    ],
    9: [
        {"lettre": "A", "titre": "Vieillir sans en avoir le droit"},
        {"lettre": "B", "titre": "Le sentiment de l'âge"},
        {"lettre": "C", "titre": "C'est pas tous les jours qu'on prend sa retraite"},
    ],
    10: [
        {"lettre": "A", "titre": "Science friction"},
        {"lettre": "B", "titre": "Résistance 2050"},
        {"lettre": "C", "titre": "SonarVision, un guide pour les personnes déficientes visuelles"},
        {"lettre": "D", "titre": "Quand marcher redevient possible"},
        {"lettre": "E", "titre": "Les technologies de la santé au service des soins à domicile"},
        {"lettre": "F", "titre": "Je n'arrive pas à faire mon choix"},
    ],
    11: [
        {"lettre": "A", "titre": "Les bienfaits des comportements de solidarité"},
        {"lettre": "B", "titre": "Poursuivi pour délit de solidarité"},
        {"lettre": "C", "titre": "Tu souhaites t'engager toi aussi"},
    ],
    12: [
        # T12 A ("Le vivant entre dans le champ politique") absent du TXT et du PDF.
        # {"lettre": "A", "titre": "Le vivant entre dans le champ politique"},
        {"lettre": "B", "titre": "Pour une nouvelle conception des animaux"},
        {"lettre": "C", "titre": "Loup, comment vivre avec"},
        {"lettre": "D", "titre": "Madagascar : à la découverte du parc d'Andasibe-Mantadia"},
        {"lettre": "E", "titre": "Une forêt primaire en Europe de l'Ouest"},
        {"lettre": "F", "titre": "Je m'émerveille de voir un animal sauvage, mais"},
    ],
}

RANGES = {
    "transcription_audio": (198, 217),
    "transcription_video": (218, 221),
    "corrige":             (222, 237),
}

# ─── Regex ───
#RE_PAGE_MARK = re.compile(r"(\d{1,3})\s+I\s*\w+")
RE_PAGE_MARK = re.compile(r"(\d{1,3})\s+I\s*\w+")
RE_PAGE_MARK_INV = re.compile(r"\w+\s+I\s+(\d{1,3})")
RE_SECTION = re.compile(
    r"^\s*(?:\d+\s+)?(Compréhension audiovisuelle|Compréhension orale|Compréhension écrite|"
    r"Production orale|Production écrite|Grammaire|Vocabulaire|Francophonie|"
    r"Fiche méthodologique|Atelier médiation|Documents|Cahier d'activités|"
    r"Produire|À bâtons rompus)\s*$",
    re.I,
)
RE_QUESTION = re.compile(r"^\s*(\d{1,2})\s+([A-ZÀ-Ý].{5,})$")
RE_TRANSCRIPTION = re.compile(r"Page\s+(\d+),\s*([A-Z])\s*[–\-]\s*(.+)$")
RE_CORRIGE = re.compile(
    r"Page\s+(\d+),\s*(Vocabulaire|Grammaire|À bâtons rompus|Produire|"
    r"Compréhension orale|Compréhension écrite|Production orale|Production écrite|"
    r"Francophonie|Fiche méthodologique|Atelier médiation)\b",
    re.I,
)
RE_THEME = re.compile(r"^Th[eè]me\s+(\d+)\s+p\.\s*(\d+)", re.I)
RE_THEME_SIMPLE = re.compile(r"^Th[eè]me\s+(\d+)\s*$", re.I)


def nz(s):
    """Normalise une chaîne : minuscules, sans accents, sans ponctuation."""
    s = s.lower()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("œ", "oe").replace("æ", "ae")
    s = s.replace("’", "'").replace("‘", "'")
    s = s.replace("–", "-").replace("—", "-")
    s = re.sub(r"[^a-z0-9' ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def normalize_line(line):
    """Nettoie une ligne : espaces insécables, ligatures, apostrophes."""
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


def match_container(line, theme_n):
    """Cherche si la ligne contient le titre d'un conteneur du thème donné.
    Le titre doit être en début de ligne (ou précédé de A-G).
    """
    if theme_n is None or theme_n not in CONTAINERS:
        return None
    line_stripped = line.strip()
    line_nz = nz(line_stripped)
    if len(line_nz) < 5 or len(line_nz) > 100:
        return None

    for c in CONTAINERS[theme_n]:
        titre_nz = nz(c["titre"])
        # 1. Match exact en début de ligne
        if line_nz.startswith(titre_nz):
            return (c["lettre"], c["titre"])
        # 2. Match avec lettre devant (A Titre)
        if re.match(rf"^[a-g]\s+{re.escape(titre_nz)}", line_nz):
            return (c["lettre"], c["titre"])
        # 3. Match partiel (3 premiers mots) en début de ligne
        mots = titre_nz.split()
        if len(mots) >= 3:
            prefix = " ".join(mots[:3])
            if len(prefix) >= 10 and line_nz.startswith(prefix):
                return (c["lettre"], c["titre"])
    return None
    
def parse_txt(txt_path):
    with open(txt_path, encoding="utf-8") as f:
        raw = f.read()

    raw = raw.replace("\u00a0", " ").replace("\u202f", " ").replace("\u200b", " ")
    raw = raw.replace("ﬁ", "fi").replace("ﬂ", "fl")
    raw = raw.replace("ﬀ", "ff").replace("ﬃ", "ffi").replace("ﬄ", "ffl")
    raw = raw.replace("’", "'").replace("‘", "'")
    raw = raw.replace("–", "-").replace("—", "-")

    n_trans_lines = sum(1 for l in raw.split("\n") if re.search(r"Page\s+\d+,\s*[A-Z]\s*[–\-]", l))
    n_corr_lines = sum(1 for l in raw.split("\n") if re.search(r"Page\s+\d+,\s*(Vocabulaire|Grammaire|À bâtons rompus|Produire)", l, re.I))
    print(f"  Lignes 'Page XX, [A-Z] - ...' : {n_trans_lines}")
    print(f"  Lignes 'Page XX, Titre'       : {n_corr_lines}")

    pages_raw = re.split(r"-{10,}", raw.replace("\f", "\n--------PAGE--------\n"))
    pages_raw = [p for p in pages_raw if p.strip()]
    print(f"  {len(pages_raw)} pages détectées (non vides)")

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
    in_cahier = False
    seen_containers = set()

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
                if current_conteneur not in themes_data[current_theme]["conteneurs"]:
                    themes_data[current_theme]["conteneurs"].append(current_conteneur)
        current_conteneur = None

    for page_idx, page_raw in enumerate(pages_raw):
        page_lines = [normalize_line(l) for l in page_raw.split("\n")]
        page_lines = [l for l in page_lines if l]

        if not page_lines:
            continue

        # Détection du numéro de page (deux formats : "12 I douze" et "douze I 12")
        page_n = None
        for line in page_lines:
            m = RE_PAGE_MARK.search(line)
            if m:
                n = int(m.group(1))
                if 1 <= n <= 250 and (page_n is None or n > page_n):
                    page_n = n
            else:
                m = RE_PAGE_MARK_INV.search(line)
                if m:
                    n = int(m.group(1))
                    if 1 <= n <= 250 and (page_n is None or n > page_n):
                        page_n = n

        if page_n is None and last_page_n is not None:
            page_n = last_page_n + 1
        if page_n is not None:
            last_page_n = page_n

        if page_n is not None and page_n in IGNORE_PAGES:
            continue

        page_theme = theme_of_page(page_n)
        if page_theme is not None and current_theme != page_theme:
            flush_conteneur()
            current_theme = page_theme
            in_cahier = False

        if current_theme and page_n:
            cahier_start, cahier_end = PAGES_CAHIER.get(current_theme, (999, 999))
            in_cahier = cahier_start <= page_n <= cahier_end

        for line in page_lines:
            # Thème explicite
            m = RE_THEME.match(line) or RE_THEME_SIMPLE.match(line)
            if m:
                n = int(m.group(1))
                if n in themes_data:
                    flush_conteneur()
                    current_theme = n
                    in_cahier = False
                continue

            # Transcription
            m = RE_TRANSCRIPTION.search(line)
            if m and len(m.group(3)) > 3:
                page_livre = int(m.group(1))
                titre = m.group(3).strip()
                source = "video" if page_n and 218 <= page_n <= 221 else "audio"
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

            # Corrigé
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

            if current_theme is None:
                continue

            # Conteneur (matching par titre, même dans le cahier)
            matched = match_container(line, current_theme)
            if matched:
                lettre, titre = matched
                if current_conteneur and current_conteneur["etiquette"] == lettre:
                    continue
                key = (current_theme, lettre)
                if key in seen_containers:
                    flush_conteneur()
                    for c in themes_data[current_theme]["conteneurs"]:
                        if c["etiquette"] == lettre:
                            current_conteneur = c
                            break
                    current_section = None
                else:
                    seen_containers.add(key)
                    flush_conteneur()
                    current_conteneur = {
                        "etiquette": lettre,
                        "titre": titre,
                        "page": page_n,
                        "sections": [],
                    }
                continue

            # Section (ignorer dans le cahier)
            if in_cahier:
                continue

            m = RE_SECTION.match(line)
            if m and current_conteneur is not None:
                flush_section()
                sec_name = m.group(1).lower().replace(" ", "_")
                target = current_conteneur["sections"]
                existing = None
                for s in target:
                    if s["type"] == sec_name:
                        existing = s
                        break
                if existing:
                    current_section = existing
                else:
                    target.append({"type": sec_name, "page": page_n, "questions": []})
                    current_section = target[-1]
                continue

            # Question
            m = RE_QUESTION.match(line)
            if m and current_section is not None:
                flush_question()
                n = len(current_section["questions"]) + 1
                pending_question = {"n": n, "texte": m.group(2).strip()}
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
    total_q = 0
    total_c = 0
    for t in manuel["themes"]:
        nq = sum(len(s["questions"]) for c in t["conteneurs"] for s in c["sections"])
        nq += sum(len(s["questions"]) for s in t["sections_directes"])
        nc = len(t["conteneurs"])
        attendu = len(CONTAINERS[t["n"]])
        total_q += nq
        total_c += nc
        check = "✅" if nc == attendu else f"⚠️ (attendu {attendu})"
        print(f"  Thème {t['n']:2} : {nc} conteneurs {check}, {nq} questions")

    print(f"\n  Transcriptions : {len(transcriptions)}")
    print(f"  Corrigés       : {len(corriges)}")
    print(f"  Total          : {total_c} conteneurs, {total_q} questions")


if __name__ == "__main__":
    txt_path = sys.argv[1] if len(sys.argv) > 1 else "text-edito.txt"
    main(txt_path)
