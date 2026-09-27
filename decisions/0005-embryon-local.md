# 0005 — Un embryon d'archiviste sur la carte graphique d'un seul poste

- Date : 2026-09-27
- Origine : [humain] « pour l'instant je veux crée un "embryon" de modele locale qui utilise les ressource de ma crate graphique, donc pas encore de "swarm". L'idée et que a l'avenir il muisse tourner soit en swarm soit sur un serveur dedier liée au depot git »
- Décidé par : @Pwouette
- Options écartées : attendre l'essaim pour tout premier test réel
- Source : projet Claude « Memnius », fil de l'embryon local ; `travaux/local/`
- Remplace : 0004, en partie : les tests réels sont permis sur le poste d'un membre ; l'essaim reste hors de portée

L'archiviste tourne d'abord sur un seul poste, avec un modèle servi localement. L'interface reste l'API
compatible OpenAI et le nom de rôle de la décision 0002, pour passer ensuite à l'essaim ou à un serveur
dédié sans toucher au code.
