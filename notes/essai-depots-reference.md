# Essai de Ministral 3 8B sur les trois dépôts de référence — 2026-09-27

Conditions : `travaux/archiviste.py` (consigne `fiche-v1`) contre LocalAI 4.9 en conteneur
(`travaux/local/`), rôle `archiviste-moyen` = Ministral 3 8B Instruct Q4_K_M, 16 k de contexte,
température 0,2, RTX 5070 12 Go. Deux passes par dépôt, sur des clones frais de `main`.
Les fiches produites ne sont pas versionnées ici (elles iront dans `Memnius-PEE/archives`).

| Dépôt | Commit | Commits / fichiers | Durée passe 1 / 2 | Erreurs dans le texte généré |
|---|---|---|---|---|
| `optique-ondulatoire` | `d6ba134` | 3 / 27 | 13,6 s / 6,5 s | 2 mineures |
| `regles` | `619ca26` | 3 / 22 | 7,3 s / 7,2 s | 0 |
| `archiviste-local` | `3557e63` | 7 / 38 | 6,9 s / 8,2 s | 4 |

La première requête de la série inclut le chargement du modèle. VRAM occupée pendant l'essai :
10 513 Mio sur 12 227 (`nvidia-smi`). Aucune relance pour JSON invalide, aucun repli en fiche factuelle.

## Ce qui a été vérifié

Chaque affirmation du résumé, de la chronologie et de « Pour reprendre » a été comparée à `git log` et
aux fichiers du dépôt. Les champs factuels (commits, dates, auteurs, fichiers) sont calculés par Git et
sont exacts partout.

**`regles`** : juste de bout en bout, y compris des détails précis : familles de règles C, A, R et O1–O8
(`REGLES.md`), workflow `gardes.yml@v1` (`README.md` l. 15), comité réduit à Romain (décision 0004),
auteur « Claude » du correctif A4.

**`optique-ondulatoire`** : juste sur le fond (14 fichiers `.md`, un script Python, une bibliographie,
`donnees/` et `livrables/` vides). Deux libertés :
- la chronologie parle d'une « validation des fichiers structurants » qui n'apparaît dans aucun commit ;
- « contribution facile via GitHub sans installation locale » : le `README.md` dit « sur GitHub … ou en local ».

**`archiviste-local`** : le plus faible, et pour une raison identifiable.
- Au moment du clone, le `README.md` disait encore « testé seulement contre un faux serveur ». Le modèle
  l'a repris (« testé uniquement en simulation », « limité aux tests locaux sans interaction avec LocalAI »),
  alors que les commits disent l'inverse. Ce README est corrigé dans la même pull request que cette note.
- Les deux passes disent que « le prototype » a migré en conteneur ; c'est LocalAI qui y tourne.
- La passe 1 conseille « d'étendre le prototype pour intégrer LocalAI », ce qui est déjà fait.
- « Llama-CPP » est présenté comme un modèle alors que c'est le moteur d'inférence.

Stabilité : entre les deux passes, les faits cités et les erreurs sont les mêmes ; seule la formulation change.

## Ce que l'essai apprend

1. Ministral 3 8B suffit pour l'étape 1 : un texte en bon français, JSON valide du premier coup,
   environ 7 s par dépôt de cette taille.
2. Le modèle croit le `README.md` plus que les commits. Un README en retard donne une fiche fausse.
   Piste pour la consigne `fiche-v2` : fournir aussi `PASSATION.md`, et demander de signaler les
   contradictions entre README et commits au lieu de trancher.
3. Il reformule les messages de commit avec des sujets approximatifs (« le prototype » pour « LocalAI »).
   La relecture humaine (`relu_par`) reste nécessaire avant tout scellé.

## Non vérifié

- Le comportement sur un dépôt volumineux, qui dépasserait les 16 k de contexte (étape 2, map-reduce).
- La comparaison avec un autre modèle sur ces mêmes dépôts.
