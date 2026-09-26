# Archiviste sur modèles locaux

> Concevoir l'agent qui archive les dépôts du groupe avec des modèles d'IA locaux.

| | |
|---|---|
| **Statut** | actif |
| **Mainteneur·ices** | @Pwouette |
| **Niveau d'entrée** | moyen |
| **Où en est-on ?** | voir [`PASSATION.md`](PASSATION.md) |

## De quoi s'agit-il ?

Le groupe accumule des dépôts dont beaucoup finiront par s'endormir. L'archiviste doit tenir, pour chacun,
une fiche d'archive : ce que contient le dépôt, qui y a contribué, ce qui s'y est passé, et comment reprendre
le sujet. Il alimente le registre commun et scelle les sujets endormis. Il tourne sur des modèles d'IA locaux,
répartis sur l'essaim LocalAI des membres, pour que rien ne sorte du groupe.

Déjà acquis : une architecture (`docs/architecture.md`) et un prototype de la première étape
(`travaux/archiviste.py`), testé seulement contre un faux serveur. Les faits viennent de Git, jamais du
modèle, et le texte rédigé par un modèle reste marqué « non relu » tant qu'une personne ne l'a pas vérifié.

L'étude est en **phase prospective** : on conçoit et on compare, on ne lance rien sur l'essaim pour l'instant
(décision 0004). L'archiviste en fonctionnement écrira plus tard dans `Memnius-PEE/archives`, pas ici.

## Contribuer en 5 minutes

1. Lire [`PASSATION.md`](PASSATION.md) : l'état du travail et les prochaines étapes.
2. Choisir un ticket étiqueté « bon premier ticket » ou ouvrir un ticket pour proposer une idée.
3. Modifier directement sur GitHub (bouton « crayon », ou touche `.` pour l'éditeur web) ou en local,
   puis ouvrir une pull request. Aucune installation n'est nécessaire pour les notes et la documentation.

Les règles communes à tous les sujets sont dans [CONTRIBUTING.md](CONTRIBUTING.md).

## Organisation du dépôt

| Dossier | Contenu |
|---|---|
| `PASSATION.md` | état courant, prochaines étapes, pièges |
| `decisions/` | une fiche par décision structurante |
| `docs/` | architecture de l'archiviste (`architecture.md`) |
| `notes/` | questions ouvertes (`questions-ouvertes.md`) |
| `sources/` | liens vers LocalAI, llama.cpp, SQLite FTS5, gitleaks (`liens.md`) |
| `travaux/` | prototype de l'étape 1 (`archiviste.py`, bibliothèque standard seulement) |
| `donnees/`, `livrables/` | vides pour l'instant |

Les métadonnées lues par le registre commun sont dans [`memnius.yaml`](memnius.yaml).
Les consignes pour les agents IA sont dans [`AGENTS.md`](AGENTS.md).

## Licence

CC-BY-4.0 (voir `memnius.yaml`).
