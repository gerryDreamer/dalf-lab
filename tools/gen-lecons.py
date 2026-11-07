#!/usr/bin/env python3
"""
tools/gen-lecons.py — Génère data/edito-c1.lecons.json (squelette).

Lit :
- data/edito-c1.manuel.json     (thèmes → conteneurs → sections → questions)
- data/edito-c1.ressources.json (transcriptions, corrigés)

Produit :
- data/edito-c1.lecons.json     (squelette prêt pour l'atelier)

Chaque question a un id unique (ex. "T1-A-comp_audio-q1").
Les QCM sont vides ("qcm": []) — à remplir à l'atelier.

Usage :
    python3 tools/gen-lecons.py
"""
import json
import os
import sys
from datetime import datetime

# ─── Mapping type de section → identifiant court ───
SECTION_SHORT = {
    "compréhension_audiovisuelle": "comp_audio",
    "compréhension_orale": "comp_orale",
    "compréhension_écrite": "comp_ecrite",
    "production_orale": "prod_orale",
    "production_écrite": "prod_ecrite",
    "grammaire": "grammaire",
    "vocabulaire": "vocabulaire",
    "francophonie": "francophonie",
    "fiche_méthodologique": "fiche_methodo",
    "atelier_médiation": "atelier_mediation",
    "documents": "documents",
    "cahier_d'activités": "cahier",
    "produire": "produire",
    "à_bâtons_rompus": "a_batons_rompus",
}


def short_type(type_section):
    """Retourne un identifiant court pour un type de section."""
    return SECTION_SHORT.get(type_section.lower(), type_section.lower())


def load_json(path):
    if not os.path.exists(path):
        print(f"❌ Fichier introuvable : {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def theme_of_page(page_n, themes):
    """Retourne le numéro de thème pour une page donnée."""
    if page_n is None:
        return None
    for t in themes:
        a, b = t["pages"]
        if a <= page_n <= b:
            return t["n"]
    return None


def rattacher_ressources(ressources, themes):
    """Rattache chaque ressource à un thème (via page_livre)."""
    trans_par_theme = {}
    corr_par_theme = {}

    for t in ressources.get("transcriptions", []):
        th = t.get("theme") or theme_of_page(t.get("page_livre"), themes)
        if th is not None:
            trans_par_theme.setdefault(th, []).append(t)

    for c in ressources.get("corriges", []):
        th = c.get("theme") or theme_of_page(c.get("page_livre"), themes)
        if th is not None:
            corr_par_theme.setdefault(th, []).append(c)

    return trans_par_theme, corr_par_theme


def rattacher_transcriptions_aux_conteneurs(theme_data, trans_du_theme):
    """Rattache chaque transcription à un conteneur (via page_livre)."""
    if not trans_du_theme:
        return

    # Pour chaque transcription, trouver le conteneur dont la page est la plus proche
    for trans in trans_du_theme:
        page = trans.get("page_livre")
        if page is None:
            continue

        # Chercher le conteneur dont la page est dans [page, page+2]
        best = None
        for cont in theme_data.get("conteneurs", []):
            cont_page = cont.get("page")
            if cont_page is None:
                continue
            if cont_page <= page <= cont_page + 2:
                best = cont
                break

        if best:
            best.setdefault("transcriptions", []).append({
                "page_livre": trans.get("page_livre"),
                "document": trans.get("document"),
                "titre": trans.get("titre"),
                "source": trans.get("source", "audio"),
                "texte": trans.get("texte", ""),
            })


"""def gen_lecons(manuel, ressources):
    #Génère le squelette lecons.json.
    themes = manuel["themes"]
    trans_par_theme, corr_par_theme = rattacher_ressources(ressources, themes)

    lecons = {
        "meta": {
            "manuel": "Édito C1 (2e édition, 2024)",
            "source": "text-edito.txt",
            "date_generation": datetime.now().strftime("%Y-%m-%d"),
            "version": "1.0",
            "description": "Squelette généré depuis manuel.json et ressources.json. QCM vides (à remplir à l'atelier)."
        },
        "themes": [],
    }

    for t in themes:
        n = t["n"]
        theme_data = {
            "n": n,
            "titre": t["titre"],
            "pages": t["pages"],
            "conteneurs": [],
            "sections_directes": [],
            "ressources": {
                "transcriptions": trans_par_theme.get(n, []),
                "corriges": corr_par_theme.get(n, []),
            },
        }

        # Rattacher les transcriptions aux conteneurs
        rattacher_transcriptions_aux_conteneurs(theme_data, trans_par_theme.get(n, []))

        # Conteneurs
        for cont in t.get("conteneurs", []):
            cont_data = {
                "etiquette": cont.get("etiquette"),
                "titre": cont.get("titre", ""),
                "page": cont.get("page"),
                "sections": [],
                "transcriptions": cont.get("transcriptions", []),
            }

            for sec in cont.get("sections", []):
                sec_type = sec.get("type", "")
                sec_short = short_type(sec_type)
                sec_id = f"T{n}-{cont.get('etiquette', '?')}-{sec_short}"

                questions = []
                for q in sec.get("questions", []):
                    q_id = f"{sec_id}-q{q.get('n', 0)}"
                    questions.append({
                        "id": q_id,
                        "n": q.get("n"),
                        "texte": q.get("texte", ""),
                        "qcm": [],  # à remplir
                    })

                sec_data = {
                    "id": sec_id,
                    "type": sec_type,
                    "page": sec.get("page"),
                    "questions": questions,
                }
                cont_data["sections"].append(sec_data)

            theme_data["conteneurs"].append(cont_data)

        # Sections directes
        for sec in t.get("sections_directes", []):
            sec_type = sec.get("type", "")
            sec_short = short_type(sec_type)
            sec_id = f"T{n}-direct-{sec_short}"

            questions = []
            for q in sec.get("questions", []):
                q_id = f"{sec_id}-q{q.get('n', 0)}"
                questions.append({
                    "id": q_id,
                    "n": q.get("n"),
                    "texte": q.get("texte", ""),
                    "qcm": [],
                })

            sec_data = {
                "id": sec_id,
                "type": sec_type,
                "page": sec.get("page"),
                "questions": questions,
            }
            theme_data["sections_directes"].append(sec_data)

        lecons["themes"].append(theme_data)

    return lecons
"""

def gen_lecons(manuel, ressources):
    """Génère le squelette lecons.json."""
    themes = manuel["themes"]
    trans_par_theme, corr_par_theme = rattacher_ressources(ressources, themes)

    lecons = {
        "meta": {
            "manuel": "Édito C1 (2e édition, 2024)",
            "source": "text-edito.txt",
            "date_generation": datetime.now().strftime("%Y-%m-%d"),
            "version": "1.0",
            "description": "Squelette généré depuis manuel.json et ressources.json. QCM vides (à remplir à l'atelier)."
        },
        "themes": [],
    }

    seen_ids = set()  # ← AJOUTER

    for t in themes:
        n = t["n"]
        theme_data = {
            "n": n,
            "titre": t["titre"],
            "pages": t["pages"],
            "conteneurs": [],
            "sections_directes": [],
            "ressources": {
                "transcriptions": trans_par_theme.get(n, []),
                "corriges": corr_par_theme.get(n, []),
            },
        }

        rattacher_transcriptions_aux_conteneurs(theme_data, trans_par_theme.get(n, []))

        for cont in t.get("conteneurs", []):
            cont_data = {
                "etiquette": cont.get("etiquette"),
                "titre": cont.get("titre", ""),
                "page": cont.get("page"),
                "sections": [],
                "transcriptions": cont.get("transcriptions", []),
            }

            for sec in cont.get("sections", []):
                sec_type = sec.get("type", "")
                sec_short = short_type(sec_type)
                sec_id = f"T{n}-{cont.get('etiquette', '?')}-{sec_short}"

                questions = []
                for q in sec.get("questions", []):
                    q_id = f"{sec_id}-q{q.get('n', 0)}"
                    if q_id in seen_ids:  # ← AJOUTER
                        continue
                    seen_ids.add(q_id)
                    questions.append({
                        "id": q_id,
                        "n": q.get("n"),
                        "texte": q.get("texte", ""),
                        "qcm": [],
                    })

                if questions:  # ← ne garder que les sections non vides
                    sec_data = {
                        "id": sec_id,
                        "type": sec_type,
                        "page": sec.get("page"),
                        "questions": questions,
                    }
                    cont_data["sections"].append(sec_data)

            theme_data["conteneurs"].append(cont_data)

        # Sections directes
        for sec in t.get("sections_directes", []):
            sec_type = sec.get("type", "")
            sec_short = short_type(sec_type)
            sec_id = f"T{n}-direct-{sec_short}"

            questions = []
            for q in sec.get("questions", []):
                q_id = f"{sec_id}-q{q.get('n', 0)}"
                if q_id in seen_ids:  # ← AJOUTER
                    continue
                seen_ids.add(q_id)
                questions.append({
                    "id": q_id,
                    "n": q.get("n"),
                    "texte": q.get("texte", ""),
                    "qcm": [],
                })

            if questions:
                sec_data = {
                    "id": sec_id,
                    "type": sec_type,
                    "page": sec.get("page"),
                    "questions": questions,
                }
                theme_data["sections_directes"].append(sec_data)

        lecons["themes"].append(theme_data)

    return lecons

def main(out_dir="data"):
    manuel_path = os.path.join(out_dir, "edito-c1.manuel.json")
    ressources_path = os.path.join(out_dir, "edito-c1.ressources.json")
    lecons_path = os.path.join(out_dir, "edito-c1.lecons.json")

    print(f"📖 Chargement de {manuel_path}")
    manuel = load_json(manuel_path)
    print(f"📖 Chargement de {ressources_path}")
    ressources = load_json(ressources_path)

    print("🔧 Génération du squelette…")
    lecons = gen_lecons(manuel, ressources)

    with open(lecons_path, "w", encoding="utf-8") as f:
        json.dump(lecons, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Écrit : {lecons_path}")

    # Rapport
    print(f"\n📊 Statistiques :")
    total_q = 0
    total_sections = 0
    total_conteneurs = 0
    for t in lecons["themes"]:
        nq = sum(len(s["questions"]) for c in t["conteneurs"] for s in c["sections"])
        nq += sum(len(s["questions"]) for s in t["sections_directes"])
        ns = sum(len(c["sections"]) for c in t["conteneurs"]) + len(t["sections_directes"])
        nc = len(t["conteneurs"])
        nt = len(t["ressources"]["transcriptions"])
        ncorr = len(t["ressources"]["corriges"])
        total_q += nq
        total_sections += ns
        total_conteneurs += nc
        print(f"  Thème {t['n']:2} : {nc} conteneurs, {ns} sections, {nq} questions, "
              f"{nt} trans, {ncorr} corrigés")

    print(f"\n  Total : {total_conteneurs} conteneurs, {total_sections} sections, {total_q} questions")


if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "data"
    main(out_dir)
