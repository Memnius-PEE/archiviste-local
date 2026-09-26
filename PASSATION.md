# Passation — 2026-09-26 — rédigée par un agent (Claude), vérifiée par : —

<!-- Réécrite à chaque fin de session (règle C9) ; l'historique Git garde les précédentes. -->

## 0. En une phrase *
Sujet créé à partir du gabarit ; l'étude initiale de l'archiviste y est versée et alignée sur le kit v1, rien n'a tourné sur l'essaim.

## 1. État mesuré *
```
$ python3 gardes.py --registre registre .     (regles v1 avec le correctif A4 du kit, registre v1)
[ ok ] A2 Secrets — 29 fichiers parcourus
[ ok ] A3 Structure — archiviste-local : conforme
[ ok ] A4 Journal en ajout seul — 4 entrées, comparé à 994857965d   (base = commit du gabarit, cas « Use this template »)
[ ok ] A5 Renvois aux règles — 32 renvois vérifiés
[ ok ] A6 Gros fichiers — 29 fichiers sous 10 Mo
Bilan : 5/5 gardes vertes
```
```
$ python3 travaux/archiviste.py fiche <copie locale de ce dépôt> --sans-ia -o /tmp/fiches/
code=0 ; extrait de l'en-tête produit :
titre: "archiviste-local"
nb_commits: 1
nb_fichiers: 29
instructions_agents: ["AGENTS.md", "CLAUDE.md"]
licence: null
```

## 2. Ce qui est entré, et qui l'a vérifié
- `docs/architecture.md` : étude initiale de l'archiviste, reprise de l'étude du projet Claude « Memnius » et alignée sur
  GitHub, le dépôt `Memnius-PEE/archives` et `etat.json` ; exemples de fiche passés sur `optique-ondulatoire`. Pas encore relue par une personne.
- `travaux/archiviste.py` : prototype de l'étape 1, repris tel quel. Testé autrefois contre un faux serveur OpenAI-compatible ;
  ici seulement en mode `--sans-ia` (sortie ci-dessus).
- `notes/questions-ouvertes.md` : six questions à trancher avant de sortir de la phase prospective.

## 3. Décisions prises (numéros du journal)
- 0001 : socle v1, niveau recommandé.
- 0002 : essaim LocalAI en mode fédéré, modèles désignés par rôle.
- 0003 : faits calculés par Git, texte du modèle marqué « non relu ».
- 0004 : phase prospective, aucun test réel sur l'essaim.

## 4. Manquements aux règles (R8)
- Aucun.

## 5. Ce qui reste dû ou en cours *
1. Relire `docs/architecture.md` (bon premier ticket).
2. Répondre aux questions de `notes/questions-ouvertes.md`, une décision par réponse.
3. Étape 2 sur le papier : cache par empreinte, map-reduce, gitleaks avant envoi (`docs/architecture.md` §10).
4. `travaux/archiviste.py` prend le titre dans le nom du dossier et cherche un fichier LICENSE : lire plutôt `titre` et `licence`
   dans `memnius.yaml` (sortie ci-dessus : `licence: null` alors que la fiche déclare CC-BY-4.0).
5. Faire produire à `travaux/archiviste.py` un `etat.json` au format du README de `Memnius-PEE/archives`, à la place de son registre provisoire.

## 6. Pièges rencontrés
- `archiviste.py fiche` lit l'historique du dépôt Git qui contient le dossier donné : sur un sous-dossier d'un autre dépôt,
  les faits sont ceux du dépôt englobant.
- Ne pas commiter ici les fiches produites : elles appartiennent au futur dépôt `Memnius-PEE/archives`.

## 7. Ce qui n'a PAS été vérifié *
- Aucun appel à un vrai modèle LocalAI ni à l'essaim (décision 0004).
- Les modèles et tailles mémoire de `docs/architecture.md` §4 sont des ordres de grandeur `[non vérifié]` sur le matériel des membres.
- Les noms de commandes du mode fédéré de LocalAI varient selon la version `[non vérifié]`.
