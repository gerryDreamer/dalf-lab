# Pipeline d'extraction TXT — DALF Lab

Documentation du pipeline **TXT** (actif). Le pipeline **PDF** est
archivé (voir `tools/extract.py`).

Dernière mise à jour : 2025-11-07.

---

## 1. Objectif

À partir de `text-edito.txt` (contenu intégral du manuel en texte,
avec page breaks), produire :

| Fichier | Contenu |
|---|---|
| `data/edito-c1.manuel.json` | 12 thèmes, conteneurs, sections, questions |
| `data/edito-c1.ressources.json` | 34 transcriptions, 48 corrigés |
| `data/edito-c1.lecons.json` | Squelette prêt pour l'atelier |

**Contraintes** :
- `text-edito.txt` **ne doit jamais** entrer dans le dépôt (gitignored)
- Aucune clé API dans le code
- Le pipeline doit être **reproductible**

---

## 2. Structure du TXT

Le fichier `text-edito.txt` a la structure suivante :
