
---

## 📄 3. `docs/CHANGELOG.md`

```markdown
# Changelog — DALF Lab

## [0.4.0] — 2025-11-07 — `feat: pipeline TXT`

### Ajouté
- `tools/label-txt.py` (v8) : parser TXT Édito C1
  - Découpe par pages (`--------`)
  - Détecte 34 transcriptions + 48 corrigés (100%)
  - Détecte conteneurs A-G, sections, 475 questions
  - Whitelist conteneurs, filtre pages vides, fusion conteneurs
- `tools/gen-lecons.py` : génère `data/edito-c1.lecons.json`
  - 12 thèmes, 23 conteneurs, 134 sections, 475 questions
  - IDs uniques (`T1-A-comp_audio-q1`)
  - QCM vides (`"qcm": []`)
- `data/edito-c1.manuel.json` : contenu structuré
- `data/edito-c1.ressources.json` : 34 trans + 48 corr
- `data/edito-c1.lecons.json` : squelette
- `docs/PIPELINE.md` : pipeline TXT (remplace PDF)

### Modifié
- `README.md` : vue d'ensemble TXT
- `docs/ARCHITECTURE.md` : pipeline TXT
- `sw.js` : `dalf-v6` → `dalf-v7` (si applicable)

### Archivé
- `tools/label.py` (PDF, v4)
- `tools/extract.py` (PDF, v4)
- `tools/poc.mjs`, `tools/debug-theme.py`, `tools/test-layout.py`

### TODO
- Améliorer détection conteneurs collés (`B Vers un horizon...`)
- Dédupliquer les questions par texte
- Atelier d'étiquetage manuel

---

## [0.3.0] — 2025-11-05 — `docs: documentation complète`

### Ajouté
- `docs/ARCHITECTURE.md`, `docs/CHANGELOG.md`, `docs/PIPELINE.md`
- `README.md` réécrit

### Documenté
- 7 tentatives `seg()` → `seg7()` (échecs)
- Bascule PDF → TXT

---

## [0.2.0] — 2025-11-01 — `refactor: découpage + robustesse`

### Modifié
- `index.html` → `app.js` + `app.css` + `data/`
- `sw.js` : `dalf-v5` → `dalf-v6`

### Corrigé
- `esc()` échappe `"` et `'`
- `nz()` gère `œ`/`æ`/`ß`
- Garde-fou Gemini, AbortController, etc.

---

## [0.1.0] — 2025-10-31 — `feat: prototype initial`

### Ajouté
- Prototype monolithique
- Manifest, Service Worker
- Profils Édito C1, Cosmopolite 5
- 4 leçons, lecteur, écriture, liens, import PDF, IA
