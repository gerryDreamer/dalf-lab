
---

## 📄 2. `docs/ARCHITECTURE.md` (à créer)

```markdown
# Architecture — DALF Lab

Documentation technique du projet. Dernière mise à jour : 2025-11-07.

## 1. Vue d'ensemble

DALF Lab est une **PWA statique** (pas de backend) qui transforme des
manuels DALF en exercices interactifs. Elle est servie par GitHub Pages
et fonctionne **hors ligne** grâce à un Service Worker.

### Principes directeurs

1. **Aucun contenu protégé dans le dépôt** — les manuels restent sur
   l'appareil de l'utilisateur.
2. **Aucune clé API dans le code** — saisie dans l'appli, stockée en
   `localStorage`.
3. **Le corrigé du manuel prime sur l'IA** — un contenu généré est
   toujours marqué « à vérifier ».
4. **Offline-first** — le Service Worker cache tous les assets.

### Stack

| Couche | Techno | Version |
|---|---|---|
| UI | HTML/CSS/JS vanilla (modules ES) | — |
| Lecture PDF (navigateur) | pdf.js (CDN) | 3.11.174 |
| Lecture PDF (Node) | pdfjs-dist | 3.11.174 |
| PWA | Service Worker + Manifest | — |
| IA (optionnelle) | API compatible OpenAI | — |

---

## 2. Structure des fichiers

### `index.html` (~30 lignes)

Coquille minimale :
- `<head>` : meta, manifest, icône, `app.css`
- `<body>` : `<main id="app">` + `<script src="app.js" type="module">`

### `app.js` (~600 lignes)

Trois sections commentées :

1. **État, helpers, données** : `S` (état persistant), `esc()`, `nz()`,
   `ok()`, chargement de `data/edito-c1.lecons.json` et des profils.
2. **Navigation et onglets** : `home()`, `lessons()`, `reader()`,
   `writer()`, `links()`.
3. **Import, IA, démarrage** : `importer()`, `fromPdf()`, `runImp()`,
   `extra()`, `ai()`, `gen()`, pont `window.App`, enregistrement SW.

### `data/edito-c1.lecons.json`

Données du manuel Édito C1 :

```json
{
  "id": "edito-c1",
  "sujet": "Justice, quelles alternatives ?",
  "lecons": [ { "id": 1, "t": "...", "q": [ ... ] } ],
  "liens": [ { "h": "...", "r": [ ... ] } ],
  "sujets_ia": [ "..." ],
  "types_ia": { "qcm": "...", ... },
  "taches": [ { "id": "r", "n": 233, "m": 1, ... } ],
  "connecteurs": [ "de plus", "en effet", ... ]
}

.
├── index.html                 Coquille HTML (~30 lignes)
├── app.css                    Styles (~200 lignes)
├── app.js                     Logique applicative (~600 lignes, 3 sections)
├── manifest.json              Manifest PWA
├── sw.js                      Service Worker (cache dalf-v6)
├── icon-192.png               Icône PWA
├── icon-512.png               Icône PWA
├── data/
│   └── edito-c1.lecons.json   Données du manuel Édito C1 (leçons, liens, tâches)
├── profiles/
│   ├── edito-c1.json          Règles de détection pour Édito C1
│   └── cosmopolite-5.json     Règles de détection pour Cosmopolite 5
├── tools/                     Outils d'extraction PDF (Node, hors appli)
│   ├── poc.mjs                Preuve de concept d'extraction
│   └── out/                   Sorties brutes (gitignored)
├── docs/
│   └── ARCHITECTURE.md        Documentation technique
└── README.md
