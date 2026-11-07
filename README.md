# DALF Lab

Application web (PWA) pour préparer le DALF C1/C2 à partir de manuels
(Édito C1, Cosmopolite 5…). Transforme un manuel en exercices
interactifs, relie automatiquement les ressources (transcriptions,
corrigés) et permet de s'entraîner hors ligne.

## État actuel

**Pipeline d'extraction TXT fonctionnel** ✅

- 12 thèmes structurés (conteneurs, sections, questions)
- 34 transcriptions (audio + vidéo)
- 48 corrigés
- 475 questions brutes (à transformer en QCM)
- Squelette `lecons.json` généré

**Application web** (prototype statique) :
- 4 leçons interactives (QCM + textes à trous) sur Édito C1, thème 1
- Lecteur de texte avec surlignage
- Production écrite avec compteur de mots
- Import PDF (pdf.js) : détection des transcriptions/corrigés
- Études extra avec l'IA (Gemini, Mistral, Groq, OpenRouter, DeepSeek)
- PWA installable, fonctionne hors ligne

** Arbre ** :

├── index.html                 Coquille HTML (~30 lignes)
├── app.css                    Styles (~200 lignes)
├── app.js                     Logique applicative (~600 lignes)
├── manifest.json              Manifest PWA
├── sw.js                      Service Worker (cache dalf-v7)
├── icon-192.png               Icône PWA
├── icon-512.png               Icône PWA
├── data/
│   ├── edito-c1.manuel.json       Contenu structuré du manuel (329 questions)
│   ├── edito-c1.ressources.json   Transcriptions + corrigés (34 + 48)
│   └── edito-c1.lecons.json       Squelette leçons (475 questions, QCM vides)
├── profiles/
│   ├── edito-c1.json          Règles de détection pour Édito C1
│   └── cosmopolite-5.json     Règles de détection pour Cosmopolite 5
├── tools/
│   ├── label-txt.py           ★ Parser TXT Édito C1 (v8)
│   ├── gen-lecons.py          ★ Générateur lecons.json
│   ├── label.py               Parser PDF (archivé, v4)
│   ├── extract.py             Extracteur PDF (archivé, v4)
│   ├── poc.mjs                POC extraction PDF (archivé)
│   ├── debug-theme.py         Debug parser (archivé)
│   └── test-layout.py         Test layout PDF (archivé)
├── docs/
│   ├── ARCHITECTURE.md        Documentation technique
│   ├── CHANGELOG.md           Historique des versions
│   └── PIPELINE.md            Pipeline d'extraction TXT
├── text-edito.txt             Contenu intégral du manuel (gitignored)
└── README.md

## Lancer en local

```bash
cd ~/dalf-lab
python3 -m http.server 8000
# puis http://localhost:8000 dans le navigateur


