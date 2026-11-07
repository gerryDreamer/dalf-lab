
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




---

## 📄 2. `docs/ARCHITECTURE.md`

```markdown
# Architecture — DALF Lab

Documentation technique du projet. Dernière mise à jour : 2025-11-07.

## 1. Vue d'ensemble

DALF Lab est une **PWA statique** (pas de backend) qui transforme des
manuels DALF en exercices interactifs. Elle est servie par GitHub Pages
et fonctionne **hors ligne** grâce à un Service Worker.

### Principes directeurs

1. **Aucun contenu protégé dans le dépôt** — les manuels restent sur
   l'appareil de l'utilisateur (`text-edito.txt` est gitignored).
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
| PWA | Service Worker + Manifest | — |
| IA (optionnelle) | API compatible OpenAI | — |
| Pipeline TXT | Python 3 | — |

---

## 2. Structure des fichiers

### Application web

- **`index.html`** : coquille (~30 lignes)
- **`app.js`** : logique (~600 lignes, 3 sections)
- **`app.css`** : styles (~200 lignes)
- **`sw.js`** : Service Worker (`dalf-v7`)

### Données

- **`data/edito-c1.manuel.json`** : contenu structuré du manuel
  (12 thèmes, conteneurs, sections, 329 questions brutes)
- **`data/edito-c1.ressources.json`** : 34 transcriptions + 48 corrigés
- **`data/edito-c1.lecons.json`** : squelette prêt pour l'atelier
  (12 thèmes, 475 questions, QCM vides)

### Pipeline TXT

- **`tools/label-txt.py`** (v8) : parse `text-edito.txt` → 2 JSON
- **`tools/gen-lecons.py`** : génère le squelette `lecons.json`
- **`tools/label.py`** et **`tools/extract.py`** : pipeline PDF (archivé)

### Documentation

- **`docs/ARCHITECTURE.md`** : ce fichier
- **`docs/CHANGELOG.md`** : historique
- **`docs/PIPELINE.md`** : pipeline d'extraction TXT

---

## 3. Pipeline TXT (actif)

### Entrée

`text-edito.txt` : contenu intégral du manuel en texte, avec :
- Pages séparées par `--------` (10+ tirets)
- Pied de page `NNN I mot` (ex. `198 I cent quatre-vingt-dix-huit`)
- Conteneurs `A`, `B`, `C`… (isolés ou collés au titre)
- Sections `Compréhension audiovisuelle`, etc.
- Questions `1  Quel est...`
- Transcriptions `Page 14, C – Titre`
- Corrigés `Page 17, Vocabulaire`

### Étapes

1. **`tools/label-txt.py`** :
   - Découpe par pages
   - Détecte `page_n` (pied de page, `n` sans `-1`)
   - Détecte les zones (transcriptions p.198–221, corrigés p.222–237)
   - Détecte les thèmes (p.11–22 pour T1, etc.)
   - Détecte les conteneurs (whitelist A-G)
   - Détecte les sections et les questions
   - Sortie : `manuel.json` + `ressources.json`

2. **`tools/gen-lecons.py`** :
   - Lit les 2 JSON
   - Rattache les ressources aux thèmes
   - Génère les 12 leçons avec conteneurs, sections, questions
   - Chaque question a un `id` unique (ex. `T1-A-comp_audio-q1`)
   - QCM vides (`"qcm": []`)
   - Sortie : `lecons.json`

### Sorties

- `manuel.json` : ~330 questions, ~36 conteneurs, ~150 sections
- `ressources.json` : 34 transcriptions, 48 corrigés
- `lecons.json` : squelette prêt pour l'atelier

### État actuel

| Élément | Attendu | Obtenu | Verdict |
|---|---|---|---|
| Transcriptions | 34 | 34 | ✅ 100% |
| Corrigés | 48 | 48 | ✅ 100% |
| Questions | ~329 | 475 | ⚠️ doublons |
| Conteneurs | ~36 | 23 | ⚠️ manquants |

**À corriger** : détection des conteneurs collés au titre (`B Vers un horizon...`), dédup par texte dans `gen-lecons.py`.

---

## 4. Modèle de données

### `manuel.json`

```json
{
  "themes": [
    {
      "n": 1,
      "titre": "Justice, quelles alternatives ?",
      "pages": [11, 22],
      "conteneurs": [
        {
          "etiquette": "A",
          "titre": "Je verrai toujours vos visages",
          "page": 12,
          "sections": [
            {
              "type": "compréhension_audiovisuelle",
              "page": 12,
              "questions": [
                {"n": 1, "texte": "Quel est le thème du film ?"},
                ...
              ]
            }
          ]
        }
      ],
      "sections_directes": []
    }
  ]
}

