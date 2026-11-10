import json

# On charge les deux fichiers
with open("data/edito-c1.theme1.json", encoding="utf-8") as f:
    gemini = json.load(f)

with open("data/edito-c1.final-images.json", encoding="utf-8") as f:
    ancien = json.load(f)

# On trouve le thème 1 dans l'ancien fichier
ancien_theme1 = next(t for t in ancien["themes"] if t["theme"] == 1)

# 1. On récupère les 8 flashcards de Gemini (elles sont déjà bonnes)
flashcards = gemini["parties"]["cahier"]["sections"][0].get("flashcards", [])

# 2. On récupère les 8 images Pixabay de l'ancien fichier (au cas où Gemini les aurait perdues)
images_anciennes = {}
for sec in ancien_theme1["parties"]["cahier"]["sections"]:
    if sec.get("type") == "vocabulaire" and "flashcards" in sec:
        for card in sec["flashcards"]:
            if card.get("image_url"):
                images_anciennes[card["recto"]] = card["image_url"]

# On réinjecte les images dans les flashcards de Gemini
for card in flashcards:
    if card["recto"] in images_anciennes:
        card["image_url"] = images_anciennes[card["recto"]]

# 3. On récupère les questions d'"À bâtons rompus" (Q11-15) de l'ancien fichier
# On va chercher large pour être sûr de les avoir
abr_questions = []
for partie in ["manuel", "cahier"]:
    for c in ancien_theme1["parties"].get(partie, {}).get("conteneurs", []):
        for s in c.get("sections", []):
            for q in s.get("questions", []):
                txt = q.get("texte", "").lower()
                if any(m in txt for m in ["débat", "monologue", "écoutez", "quel est le thème", "favorise l'émergence", "trois catégories"]):
                    abr_questions.append(q)
    for s in ancien_theme1["parties"].get(partie, {}).get("sections", []):
        for q in s.get("questions", []):
            txt = q.get("texte", "").lower()
            if any(m in txt for m in ["débat", "monologue", "écoutez", "quel est le thème", "favorise l'émergence", "trois catégories"]):
                abr_questions.append(q)

# On déduplique
vus = set()
abr_unique = []
for q in abr_questions:
    if q["texte"] not in vus:
        vus.add(q["texte"])
        abr_unique.append(q)
abr_unique = abr_unique[:5]

# 4. On récupère les questions de grammaire (générées précédemment)
gram_questions = []
for sec in ancien_theme1["parties"]["cahier"]["sections"]:
    if sec.get("type") == "grammaire" and "questions" in sec:
        gram_questions = sec["questions"]
        break

# Si on n'a pas de grammaire, on garde celle de Gemini
if not gram_questions:
    gemini_gram = gemini["parties"]["cahier"]["sections"][1]
    gram_questions = gemini_gram.get("questions", [])

# 5. On construit le cahier final
sections = [
    {"type": "vocabulaire", "titre": "Vocabulaire", "flashcards": flashcards},
    {"type": "grammaire", "titre": "Grammaire", "questions": gram_questions},
    {"type": "a_batons_rompus", "titre": "À bâtons rompus", "questions": abr_unique}
]

gemini["parties"]["cahier"]["sections"] = sections

# 6. On sauvegarde le tout dans un nouveau fichier
with open("data/edito-c1.structured.json", "w", encoding="utf-8") as f:
    json.dump({"themes": [gemini]}, f, ensure_ascii=False, indent=2)

print("✅ Fusion réussie !")
print(f"   - Vocabulaire : {len(flashcards)} flashcards (avec {sum(1 for c in flashcards if c.get('image_url'))} images)")
print(f"   - Grammaire : {len(gram_questions)} questions")
print(f"   - À bâtons rompus : {len(abr_unique)} questions")
