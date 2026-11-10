import json
import os

def merge():
    final_data = {"manuel": "Édito C1", "themes": []}
    themes_trouves = 0

    for i in range(1, 13):
        path = f"data/edito-c1.theme{i}.json"
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                theme_data = json.load(f)
                final_data["themes"].append(theme_data)
                themes_trouves += 1
        else:
            print(f"⚠️ Thème {i} manquant.")

    final_data["themes"].sort(key=lambda x: x.get("theme", 0))

    output_path = "data/edito-c1.final.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Fusion terminée ! {themes_trouves}/12 thèmes fusionnés dans {output_path}")

if __name__ == "__main__":
    merge()
