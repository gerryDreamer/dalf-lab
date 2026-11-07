#!/usr/bin/env python3
"""
tools/extract.py — Extraction PDF → JSON structuré pour DALF Lab.

Version 4 : projection verticale sur les caractères pour séparer les colonnes.
"""
import json
import sys
import os
from collections import defaultdict


def find_column_walls(chars, page_width):
    """Détecte les gouttières verticales par projection des x0."""
    # Histogramme des x0 (arrondi au pixel)
    hist = defaultdict(int)
    for c in chars:
        hist[int(c["x0"])] += 1

    # Trouver les zones où hist est faible (vallées)
    # Une vallée = suite de pixels avec hist < seuil, largeur >= 8px
    if not hist:
        return []

    max_x = max(hist.keys())
    min_x = min(hist.keys())
    threshold = max(1, sum(hist.values()) // (max_x - min_x + 1) // 3)

    walls = []
    valley_start = None
    for x in range(min_x, max_x + 1):
        if hist.get(x, 0) <= threshold:
            if valley_start is None:
                valley_start = x
        else:
            if valley_start is not None and x - valley_start >= 8:
                walls.append((valley_start + x) / 2)
            valley_start = None
    if valley_start is not None and max_x - valley_start >= 8:
        walls.append((valley_start + max_x) / 2)

    # Filtrer les murs aux bords (marges)
    return [w for w in walls if 30 < w < page_width - 30]


def extract_page(page, page_num):
    """Extrait une page avec colonnes via projection verticale."""
    chars = page.chars
    if not chars:
        return {
            "n": page_num, "width": page.width, "height": page.height,
            "words_count": 0, "lines_count": 0, "blocks_count": 0,
            "columns": [],
        }

    # 1. Détecter les colonnes (gouttières verticales)
    walls = find_column_walls(chars, page.width)

    # 2. Assigner chaque caractère à une colonne (par x0 vs walls)
    def col_of(x):
        c = 0
        for w in walls:
            if x >= w:
                c += 1
            else:
                break
        return c

    # 3. Regrouper les caractères par (colonne, ligne)
    #    Ligne = top arrondi (tolérance 3px)
    by_col = defaultdict(lambda: defaultdict(list))
    for c in chars:
        col = col_of(c["x0"])
        line_key = round(c["top"] / 3) * 3
        by_col[col][line_key].append(c)

    # 4. Reconstruire chaque colonne (ligne par ligne, triée par y puis x)
    columns = []
    for col_idx in sorted(by_col.keys()):
        lines_dict = by_col[col_idx]
        lines = []
        for y in sorted(lines_dict.keys()):
            chars_in_line = sorted(lines_dict[y], key=lambda c: c["x0"])
            # Reconstituer le texte avec espaces
            text = ""
            prev_x1 = None
            for c in chars_in_line:
                if prev_x1 is not None and c["x0"] - prev_x1 > 2:
                    text += " "
                text += c["text"]
                prev_x1 = c["x1"]
            text = " ".join(text.split())  # normaliser les espaces
            if text:
                lines.append({"y": y, "text": text})
        if lines:
            columns.append({"idx": col_idx, "x0": min(c["x0"] for c in chars if col_of(c["x0"]) == col_idx), "lines": lines})
            
            
 # Nettoyage : ne garder que les colonnes avec >= 2 lignes significatives
    columns = [c for c in columns
               if len(c["lines"]) >= 2
               and any(len(l["text"]) >= 10 for l in c["lines"])]

    return {
        "n": page_num,
        "width": page.width,
        "height": page.height,
        "words_count": len(page.extract_words()),
        "lines_count": sum(len(c["lines"]) for c in columns),
        "blocks_count": sum(len(c["lines"]) for c in columns),
        "columns": columns,
    }



def main(pdf_path, out_path):
    if not os.path.exists(pdf_path):
        print(f"❌ Fichier introuvable : {pdf_path}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    pages = []

    import pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        print(f"📖 {total} pages à traiter", file=sys.stderr)
        for i, page in enumerate(pdf.pages, start=1):
            try:
                data = extract_page(page, i)
                pages.append(data)
                if i % 10 == 0 or i == total:
                    print(f"   page {i}/{total} — {len(data['columns'])} colonnes", file=sys.stderr)
            except Exception as e:
                print(f"⚠️  page {i} échouée : {e}", file=sys.stderr)
                pages.append({"n": i, "error": str(e)})

    result = {
        "source": os.path.basename(pdf_path),
        "pages_total": len(pages),
        "pages": pages,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"✅ Écrit : {out_path}", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage : python3 tools/extract.py <pdf> <out.json>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
