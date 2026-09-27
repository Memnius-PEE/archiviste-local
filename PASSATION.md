# Passation — 2026-09-27 — rédigée par un agent (Claude), vérifiée par : —

<!-- Réécrite à chaque fin de session (règle C9) ; l'historique Git garde les précédentes. -->

## 0. En une phrase *
Un embryon local est prêt dans `travaux/local/` (LocalAI en conteneur + Ministral 3 8B sur la RTX 5070 de Romain) ; les poids ne sont pas encore téléchargés, donc aucun appel réel n'a encore eu lieu.

## 1. État mesuré *
```
$ python3 ../regles/gardes/gardes.py . --base origin/main --registre ../memnius-kit/communs/registre
[ ok ] A2 Secrets — 37 fichiers parcourus
[ ok ] A3 Structure — archiviste-local : conforme
[ ok ] A4 Journal en ajout seul — 6 entrées, comparé à origin/main
[ ok ] A5 Renvois aux règles — 32 renvois vérifiés
[ ok ] A6 Gros fichiers — 37 fichiers sous 10 Mo
Bilan : 5/5 gardes vertes
```
```
$ nvidia-smi ; local-ai --version          (poste de Romain, 2026-09-27)
NVIDIA GeForce RTX 5070, 12227 MiB (≈3 Gio pris par le bureau), pilote 595.84, CUDA 13.2
$ docker version ; dpkg -l nvidia-container-toolkit ; docker images
Docker 29.8.1, toolkit 1.20.1, image localai/localai v4.9.0-gpu-nvidia-cuda-12 présente
```

## 2. Ce qui est entré, et qui l'a vérifié
- `travaux/local/` : `compose.yaml` (LocalAI en conteneur, port 8081), configuration du rôle `archiviste-moyen` et scripts `telecharger.sh`, `lancer.sh`, `verifier.sh`. Syntaxe vérifiée (`bash -n`, `docker compose config`), jamais exécutés.
- `travaux/archiviste.py` : modèle par défaut `archiviste-moyen` (le rôle de 0002) au lieu de `qwen3-8b`.
- `docs/architecture.md` : étude initiale de l'archiviste, reprise de l'étude du projet Claude « Memnius » et alignée sur
  GitHub, le dépôt `Memnius-PEE/archives` et `etat.json` ; exemples de fiche passés sur `optique-ondulatoire`. Pas encore relue par une personne.
- `travaux/archiviste.py` : prototype de l'étape 1, repris tel quel. Testé autrefois contre un faux serveur OpenAI-compatible ;
  ici seulement en mode `--sans-ia` (sortie ci-dessus).
- `notes/questions-ouvertes.md` : six questions à trancher avant de sortir de la phase prospective.

## 3. Décisions prises (numéros du journal)
- 0005 : embryon sur le GPU d'un seul poste ; remplace en partie 0004 (l'essaim reste hors de portée).
- 0006 : LocalAI en conteneur + Ministral 3 8B Instruct Q4_K_M pour `archiviste-moyen` (en attente de validation par Romain).
- 0001 : socle v1, niveau recommandé.
- 0002 : essaim LocalAI en mode fédéré, modèles désignés par rôle.
- 0003 : faits calculés par Git, texte du modèle marqué « non relu ».
- 0004 : phase prospective, aucun test réel sur l'essaim.

## 4. Manquements aux règles (R8)
- Aucun.

## 5. Ce qui reste dû ou en cours *
0. Avec l'accord de Romain : `telecharger.sh`, `lancer.sh`, `verifier.sh`, puis consigner ici le temps d'appel, la VRAM et la qualité de la fiche.
1. Relire `docs/architecture.md` (bon premier ticket).
2. Répondre aux questions de `notes/questions-ouvertes.md`, une décision par réponse.
3. Étape 2 sur le papier : cache par empreinte, map-reduce, gitleaks avant envoi (`docs/architecture.md` §10).
4. `travaux/archiviste.py` prend le titre dans le nom du dossier et cherche un fichier LICENSE : lire plutôt `titre` et `licence`
   dans `memnius.yaml` (sortie ci-dessus : `licence: null` alors que la fiche déclare CC-BY-4.0).
5. Faire produire à `travaux/archiviste.py` un `etat.json` au format du README de `Memnius-PEE/archives`, à la place de son registre provisoire.

## 6. Pièges rencontrés
- Le port 8080 du poste est pris par le conteneur `carnet-localai` (autre projet) : l'embryon écoute sur 8081.
- `archiviste.py fiche` lit l'historique du dépôt Git qui contient le dossier donné : sur un sous-dossier d'un autre dépôt,
  les faits sont ceux du dépôt englobant.
- Ne pas commiter ici les fiches produites : elles appartiennent au futur dépôt `Memnius-PEE/archives`.

## 7. Ce qui n'a PAS été vérifié *
- Aucun appel à un vrai modèle, ni local ni sur l'essaim.
- Que le moteur llama-cpp CUDA de LocalAI 4.9 reconnaisse une carte Blackwell (RTX 50xx) `[non vérifié]`.
- Que `use_jinja` + `use_tokenizer_template` suffisent au gabarit de Ministral 3 `[non vérifié]` (repris des entrées récentes de la galerie LocalAI).
- Les modèles et tailles mémoire de `docs/architecture.md` §4 sont des ordres de grandeur `[non vérifié]` sur le matériel des membres.
- Les noms de commandes du mode fédéré de LocalAI varient selon la version `[non vérifié]`.
