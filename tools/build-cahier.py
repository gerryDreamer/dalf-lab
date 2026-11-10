import json
import re

INPUT = "data/edito-c1.final-images.json"
OUTPUT = "data/edito-c1.structured.json"

with open(INPUT, encoding="utf-8") as f:
    data = json.load(f)

theme1 = next(t for t in data["themes"] if t["theme"] == 1)

# On rassemble TOUTES les questions du Thème 1, peu importe où elles sont
toutes_les_questions = []
for partie in ["manuel", "cahier"]:
    for conteneur in theme1.get("parties", {}).get(partie, {}).get("conteneurs", []):
        for section in conteneur.get("sections", []):
            for q in section.get("questions", []):
                if isinstance(q, dict) and q.get("texte"):
                    toutes_les_questions.append(q)
    for section in theme1.get("parties", {}).get(partie, {}).get("sections", []):
        for q in section.get("questions", []):
            if isinstance(q, dict) and q.get("texte"):
                toutes_les_questions.append(q)

print(f"📊 {len(toutes_les_questions)} questions trouvées au total dans le Thème 1.")

# Mots-clés pour classer
mots_vocab = ["signifie", "définition", "terme", "mot", "expression", "synonyme", "acteur", "greffier", "juge", "procureur", "avocat", "juré", "infraction", "crime", "délit", "procédure", "tribunal", "cour"]
mots_gram = ["voix", "active", "passive", "conjugue", "accord", "temps", "verbe", "participe", "grammaire", "règle", "transforme", "phrase"]
mots_abr = ["débat", "monologue", "écoutez", "compréhension", "production", "rédigez", "argumentez", "discutez", "échangez", "exprimez"]

vocab_questions = []
gram_questions = []
abr_questions = []
autres_questions = []

for q in toutes_les_questions:
    texte = q.get("texte", "").lower()
    
    # Priorité à la grammaire (car très spécifique)
    if any(m in texte for m in mots_gram):
        gram_questions.append(q)
    # Ensuite le vocabulaire
    elif any(m in texte for m in mots_vocab):
        vocab_questions.append(q)
    # Enfin "À bâtons rompus" (compréhension/production)
    elif any(m in texte for m in mots_abr) or q.get("choix") is None or len(q.get("choix", [])) == 0:
        abr_questions.append(q)
    else:
        autres_questions.append(q)

# Si on n'a pas assez, on pioche dans les "autres"
if len(vocab_questions) < 5:
    manque = 5 - len(vocab_questions)
    vocab_questions.extend(autres_questions[:manque])
    autres_questions = autres_questions[manque:]

if len(gram_questions) < 5:
    manque = 5 - len(gram_questions)
    gram_questions.extend(autres_questions[:manque])
    autres_questions = autres_questions[manque:]

# On garde au maximum 5 par section
vocab_questions = vocab_questions[:5]
gram_questions = gram_questions[:5]
abr_questions = abr_questions[:5]

sections = [
    {"type": "vocabulaire", "titre": "Vocabulaire", "questions": vocab_questions},
    {"type": "grammaire", "titre": "Grammaire", "questions": gram_questions},
    {"type": "a_batons_rompus", "titre": "À bâtons rompus", "questions": abr_questions}
]

theme1["parties"]["cahier"]["sections"] = sections

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ Cahier reconstruit !")
for s in sections:
    print(f"   - {s['titre']} : {len(s['questions'])} questions")
    for q in s['questions']:
        print(f"       • {q['texte'][:60]}...")
