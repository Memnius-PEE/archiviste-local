# 0002 — L'archiviste tourne sur l'essaim LocalAI en mode fédéré

- Date : 2026-09-26
- Origine : [choix] option proposée par un agent dans l'étude initiale, retenue par Romain
- Décidé par : @Pwouette
- Options écartées : un modèle découpé entre machines (workers llama.cpp RPC), trop lent hors réseau local ; un service d'IA externe, exclu pour que rien ne sorte du groupe
- Source : `docs/architecture.md` §3 ; projet Claude « Memnius », fil « Concevoir l'archiviste sur l'essaim LocalAI »
- Remplace : —

Chaque machine de l'essaim charge un modèle entier ; un proxy répartit les requêtes. Le code ne connaît que
des rôles (`archiviste-petit`, `archiviste-moyen`, `archiviste-grand`, `archiviste-embed`), chaque machine
choisit le fichier de modèle qui correspond à son matériel.
