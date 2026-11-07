# Pipeline d'extraction PDF — DALF Lab

Documentation dédiée à la transformation d'un PDF de manuel
(ex. `edito.pdf`, 242 pages, texte natif) en données exploitables
par l'appli (`data/*.lecons.json`, `data/*.ressources.json`).

Dernière mise à jour : 2025-11-07.

---

## 1. Objectif

À partir d'un PDF tout-en-un (livre + cahier + transcriptions +
corrigés, sans décalage de pagination), produire :

| Fichier | Contenu |
|---|---|
| `data/edito-c1.lecons.json` | Leçons jouables (QCM, textes à trous) |
| `data/edito-c1.ressources.json` | Transcriptions, corrigés, notes |
| `data/edito-c1.liens.json` | Carte des liens entre ressources |

**Contraintes** :
- Le PDF **ne doit jamais** entrer dans le dépôt (`.gitignore`).
- L'extraction se fait **en local**, une fois, et produit des JSON
  versionnés (ou non, cf. § 7).
- Le résultat doit être **fidèle** : aucun item perdu, aucun item
  dupliqué.

---

## 2. Structure du PDF Édito C1

D'après le profil `profiles/edito-c1.json` et l'exploration :

| Plage | Contenu | Pages |
|---|---|---|
| 1–? | Couverture, sommaire, avant-propos | ~1–10 |
| ?–? | Livre (thèmes 1 à 12) | ~11–190 |
| ?–? | Cahier d'exercices (thèmes 1 à 12) | imbriqué |
| ?–? | Transcriptions (`Documents audios`, `Documents vidéos`) | ~195–220 |
| ?–? | Corrigés | ~221–242 |

**Caractéristiques** :
- Texte natif (pas d'OCR nécessaire).
- Mise en page **multi-colonnes** (2 colonnes fréquentes, encarts).
- Numérotation : `Page XX, Y – Titre` (transcriptions),
  `Page XX, Titre` (corrigés).
- Aucun décalage entre page PDF et page livre.

---

## 3. Étapes du pipeline

### Étape 1 — Extraction brute

**Entrée** : `edito.pdf`
**Sortie** : `tools/out/edito-c1.raw.json`

Contenu : pour chaque page, la liste des items `pdf.js` bruts
(`str`, `transform`, `width`, `height`) et la liste des lignes
reconstituées par `seg()`.

**Statut** : `tools/poc.mjs` fait ça sur 3-5 pages. À généraliser.

### Étape 2 — Structuration

**Entrée** : `tools/out/edito-c1.raw.json`
**Sortie** : `tools/out/edito-c1.blocs.json`

Contenu : pour chaque page, la liste des **blocs** (colonnes, encarts,
titres) avec leur type détecté (`livre`, `transcription-audio`,
`transcription-video`, `corrige`).

**Statut** : ❌ échec des 7 tentatives `seg` → `seg7` (cf. § 4).
À reprendre avec `pdfplumber` ou un Atelier manuel.

### Étape 3 — Étiquetage

**Entrée** : `tools/out/edito-c1.blocs.json`
**Sortie** : `tools/out/edito-c1.etiquettes.json`

Contenu : pour chaque bloc, une étiquette sémantique
(`exercice`, `transcription`, `corrige`, `tribune`, `encart`, …)
et une référence (`Page 17, Vocabulaire`, `Piste 2`, …).

**Statut** : ❌ à faire. Deux options :
- **Automatique** : règles du profil `edito-c1.json` + regex.
- **Manuel assisté** : `tools/atelier.html` (cf. § 5).

### Étape 4 — Génération

**Entrée** : `tools/out/edito-c1.etiquettes.json`
**Sortie** : `data/edito-c1.lecons.json`,
`data/edito-c1.ressources.json`, `data/edito-c1.liens.json`

Contenu :
- Leçons : QCM, textes à trous (à partir des exercices étiquetés).
- Ressources : transcriptions, corrigés (rattachés aux leçons).
- Liens : associations ressource ↔ leçon ↔ question.

**Statut** : ❌ à faire.

### Étape 5 — Validation humaine

**Entrée** : `data/*.json`
**Sortie** : `data/*.json` validés

L'onglet **Import** de l'appli permet de visualiser, corriger et
compléter les ressources. Un corrigé du manuel prime toujours sur
un contenu généré par IA (marqué « à vérifier »).

**Statut** : ✅ l'UI existe (`adder()`, `addRes()`).

---

## 4. Historique des tentatives de reconstruction des colonnes

Le problème central : **reconstruire les colonnes** d'une page PDF
à partir des items `pdf.js` (qui sont dans l'ordre de lecture du PDF,
pas dans l'ordre visuel).

| # | Fonction | Méthode | Résultat |
|---|---|---|---|
| 1 | `seg` | tri y puis concat x | ✅ fidèle, ❌ mélange colonnes |
| 2 | `seg2` | gaps > h*3, clusters 20px | ❌ sur-détecte (2 walls au lieu de 1) |
| 3 | `seg3` | gaps > h*5, clusters 60px, count ≥ 30% | ❌ trop strict p.12 (0 walls) |
| 4 | `seg4` | projection verticale, seuil 10% | ❌ rate p.12 (0 walls), faux positif p.222 (548) |
| 5 | `seg5` | clustering xRef (< 30px) | ❌ explose en 13-14 clusters |
| 6 | `seg6` | blocs par x0 + lastY (< 3 lignes) | ❌ 8-13 blocs |
| 7 | `seg7` | blocs par x0 + x1 (< 50/80px) | ❌ 8-12 blocs |

### Leçons apprises

- **`seg`** est fiable (aucun item perdu) mais insuffisant seul.
- Les heuristiques de **gap** sont fragiles : dépendent de la
  justification, des encarts, des tailles de police.
- Les heuristiques de **clustering** sur `x0` sont fragiles :
  chaque paragraphe crée un nouveau cluster.
- La **projection verticale** est prometteuse mais le seuil est
  difficile à calibrer (10% rate p.12, 5% sur-détecte p.222).

### Conclusion

La reconstruction automatique des colonnes est un **problème
difficile**, connu dans la littérature (`pdfplumber`, `pdfminer`,
`Camelot` en Python le résolvent mieux que `pdf.js`). Deux options :

- **Option B** : passer à `pdfplumber` (Python) pour l'extraction
  par blocs. C'est la **recommandation actuelle**.
- **Option C** : construire `tools/atelier.html`, un atelier
  d'étiquetage manuel assisté. Plus fiable, mais plus de travail.

---

## 5. Option B — `pdfplumber` (recommandé)

### Installation

```bash
pip install pdfplumber
