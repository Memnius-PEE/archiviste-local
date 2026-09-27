# 0007 — Ministral 3 8B validé ; trois dépôts de référence

- Date : 2026-09-27
- Origine : [humain] « decisions 0006 validé et lancons l'essai sur les trois depot de ref » ; [agent] choix de `regles` comme troisième dépôt de référence
- Décidé par : @Pwouette
- Options écartées : `gabarit` et `registre` comme dépôts de référence (le premier est vide de contenu propre, le second recoupe `regles`)
- Source : `notes/essai-depots-reference.md`
- Remplace : 0006, pour lever la mention « en attente de validation »

Le rôle `archiviste-moyen` est tenu par Ministral 3 8B Instruct Q4_K_M servi par LocalAI en conteneur,
comme décrit en 0006. Les dépôts de référence, qui servent à comparer deux modèles ou deux versions de
consigne avant tout changement (`docs/architecture.md` §7), sont `optique-ondulatoire` (sujet d'étude),
`regles` (code et règles) et `archiviste-local` (ce sujet). Cela répond à la question 3 de
`notes/questions-ouvertes.md`.
