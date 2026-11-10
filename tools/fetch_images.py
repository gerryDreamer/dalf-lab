import json
import os
import time
from pathlib import Path
import requests

# --- Chargement .env ---
ENV = {}
if Path(".env").exists():
    with open(".env", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                ENV[k.strip()] = v.strip().strip('"').strip("'")

API_KEY = ENV.get("PIXABAY_API_KEY")
if not API_KEY:
    print("❌ Ajoute PIXABAY_API_KEY dans .env")
    raise SystemExit(1)

INPUT  = "data/edito-c1.structured.json"
OUTPUT = "data/edito-c1.structured.json"

with open(INPUT, encoding="utf-8") as f:
    data = json.load(f)

def clean_query(recto: str) -> str:
    q = recto.split("(")[0]
    q = q.replace("Le/la ", "").replace("L'", "").replace("le/la ", "")
    q = q.replace("/", " ").replace("un ", "").replace("une ", "").strip()
    return q

stats = {"ok": 0, "miss": 0, "err": 0}

for theme in data["themes"]:
    if theme["theme"] != 1: continue
    
    cahier = theme["parties"].get("cahier", {})
    for section in cahier.get("sections", []):
        if section.get("type") == "vocabulaire":
            cards = section.get("flashcards", [])
            print(f"🔍 Recherche d'images pour {len(cards)} flashcards...")
            
            for card in cards:
                if card.get("image_url"):
                    print(f"  ⏩ {card['recto']} (déjà fait)")
                    continue
                
                query = clean_query(card["recto"])
                if not query:
                    stats["miss"] += 1
                    continue
                    
                url = (
                    f"https://pixabay.com/api/?key={API_KEY}"
                    f"&q={requests.utils.quote(query)}"
                    f"&image_type=photo&per_page=3&safesearch=true&lang=fr"
                )
                try:
                    r = requests.get(url, timeout=10)
                    r.raise_for_status()
                    hits = r.json().get("hits", [])
                    if hits:
                        card["image_url"] = hits[0]["webformatURL"]
                        print(f"  ✅ {query}")
                        stats["ok"] += 1
                    else:
                        print(f"  ⚠️  {query} (aucun résultat)")
                        stats["miss"] += 1
                except Exception as e:
                    print(f"  ❌ {query} → {e}")
                    stats["err"] += 1
                time.sleep(0.4) 

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n✅ Fichier mis à jour : {OUTPUT}")
print(f"   ok={stats['ok']}  miss={stats['miss']}  err={stats['err']}")
