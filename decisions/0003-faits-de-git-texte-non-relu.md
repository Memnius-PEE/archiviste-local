# 0003 — Les faits viennent de Git, le texte du modèle est marqué « non relu »

- Date : 2026-09-26
- Origine : [choix] principe proposé par un agent dans l'étude initiale, retenu par Romain
- Décidé par : @Pwouette
- Options écartées : laisser le modèle rédiger toute la fiche, faits compris
- Source : `docs/architecture.md` §1 et §6 ; décisions de Romain du 2026-09-26 dans le projet Claude « Memnius »
- Remplace : —

Dates, auteurs, nombre de commits, fichiers et empreintes sont calculés par Git. Le modèle ne rédige que
les champs de langue (résumé, mots-clés, chronologie commentée), identifiés par `genere_par` et affichés
« rédigé par l'archiviste, non relu » tant que `relu_par` est vide. Une relecture humaine est obligatoire
avant de sceller un sujet.
