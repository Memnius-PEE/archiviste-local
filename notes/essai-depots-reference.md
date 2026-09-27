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

---

# Consigne `fiche-v2` sur les mêmes dépôts — 2026-09-27

Mêmes clones et mêmes commits que ci-dessus. Changements de `fiche-v2` dans `travaux/archiviste.py` :
- le modèle reçoit aussi `PASSATION.md` (6 000 caractères au plus), le dépôt distant et les étiquettes Git ;
- la consigne dit quelles sources font foi et demande une liste `incoherences` ;
- la consigne demande de garder l'objet nommé par un commit et de ne pas confondre outil et modèle ;
- la réponse est contrainte par un schéma JSON (`response_format`), et `max_tokens` vaut 1500.

## Mise au point (ce qui a cassé avant la version retenue)

| Essai | Résultat |
|---|---|
| consigne seule, sans schéma | 5 fiches sur 6 en repli factuel : `resume` rendu en liste, `incoherences` en objets |
| + schéma JSON | forme correcte, mais chronologie parfois vide (la grammaire de LocalAI n'applique pas `minItems`) → rejet ajouté dans `valider` |
| + rejet des chronologies vides | 3 échecs sur 6 : retours à la ligne bruts dans les chaînes → `json.loads(..., strict=False)` |
| + `strict=False` | 5 sur 6 ; une génération a bouclé 207 s puis HTTP 500 → `max_tokens: 1500` |
| version retenue | **6 sur 6 sur deux passes**, 5,7 à 14 s par fiche |

## Comparaison avec `fiche-v1`

| Dépôt | `fiche-v1` | `fiche-v2` |
|---|---|---|
| `archiviste-local` (README périmé) | répète « testé seulement contre un faux serveur » ; « le prototype a migré en conteneur » | le README périmé est signalé comme incohérence au lieu d'être cru ; « LocalAI en conteneur » correctement nommé |
| `optique-ondulatoire` | juste mais pauvre, deux libertés | plus riche et juste : interfrange λD/a = 6,50 mm pour 650 nm, 0,2 mm, 2 m (conforme à `travaux/interfrange.py` l. 10) |
| `regles` | aucune erreur | **régresse** : suit sa `PASSATION.md` périmée (« pas encore publié », « étiquette v1 non posée ») alors que les faits donnés au modèle montrent l'étiquette `v1` et le dépôt GitHub |

Liste `incoherences` : 0 à 3 par fiche. Environ la moitié sont réelles : README et passation de `regles` en
désaccord sur l'étiquette, README périmé ici. Les autres sont fausses : « @Pwouette » et « Romain Caldani »
pris pour deux personnes, une absence d'information prise pour une contradiction. C'est une aide à la
relecture, pas un verdict.

## Ce que l'essai apprend

1. Donner la passation enrichit nettement les fiches, à condition qu'elle soit à jour. Le point faible
   passe du README à la passation : **la `PASSATION.md` de `regles` est en retard** (elle dit le dépôt non
   publié et sans étiquette).
2. Même quand les faits calculés contredisent un document, Ministral 3 8B suit souvent le document.
   Un modèle plus grand (rôle `archiviste-grand`) ou une vérification déterministe des affirmations
   (publication, étiquettes) seraient les suites possibles.
3. Le schéma JSON rend la sortie fiable ; les trois garde-fous ajoutés (chronologie non vide,
   `strict=False`, `max_tokens`) viennent chacun d'un échec observé.
