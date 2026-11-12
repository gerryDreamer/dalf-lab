import json

# Charger l'arbre actuel
with open("data/edito-c1.final-tree.json", encoding="utf-8") as f:
    data = json.load(f)

theme1 = data["themes"][0]

# Charger les anciennes données avec images
with open("data/edito-c1.structured.json", encoding="utf-8") as f:
    old_data = json.load(f)

# Construire un dictionnaire {recto: image_url}
images = {}
old_sections = old_data["themes"][0]["parties"]["cahier"]["sections"]
for s in old_sections:
    if s.get("type") == "vocabulaire" and s.get("flashcards"):
        for card in s["flashcards"]:
            if card.get("image_url"):
                images[card["recto"]] = card["image_url"]
    # Au cas où les flashcards sont dans des sous-niveaux
    for sub in old_sections:
        pass

print(f"🖼️ {len(images)} images trouvées dans l'ancien fichier.")

# Réinjecter dans le nouvel arbre
count = 0
for s in theme1["parties"]["cahier"]["sections"]:
    if s.get("type") == "vocabulaire" and s.get("flashcards"):
        for card in s["flashcards"]:
            if card["recto"] in images:
                card["image_url"] = images[card["recto"]]
                count += 1

print(f"✅ {count} images réinjectées.")

with open("data/edito-c1.final-tree.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ Fichier sauvegardé !")
