# Neo4j local dans Docker

La base de travail remplace la connexion Aura introuvable. Elle reconstruit le
graphe à partir de `graph/schema.cypher` et `graph/seed.cypher` ; ce n'est pas une
récupération des éventuels ajouts présents dans l'ancienne instance.

## Configuration

Le fichier `.env`, ignoré par Git, contient les quatre paramètres locaux :

```dotenv
NEO4J_URI=bolt://127.0.0.1:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=<mot-de-passe-local>
NEO4J_DATABASE=neo4j
```

Le mot de passe initial a été généré localement. Pour une nouvelle installation,
choisir un mot de passe avant le premier démarrage. Modifier simplement `.env`
après création du volume ne change pas le mot de passe enregistré dans Neo4j.

La base est accessible uniquement depuis ce PC. Le volume Docker nommé
`bioprocess-assistant-local_neo4j_data` conserve les données quand le conteneur
est arrêté ou recréé. Ce volume appartient au stockage Docker Desktop/WSL,
pas au dossier OneDrive du projet ; il faut le sauvegarder séparément.

## Utilisation depuis la racine du dépôt

```powershell
docker compose -f compose.neo4j.yaml up -d --wait
.\.local-tools\integration-venv\Scripts\python.exe scripts/load_graph.py
.\.local-tools\integration-venv\Scripts\python.exe eval/run_eval.py
docker compose -f compose.neo4j.yaml stop
```

L'environnement `integration-venv` est local et non versionné. Sur une autre
machine, installer `requirements.txt` et `eval/requirements.txt` dans un
environnement Python puis utiliser son interpréteur.

Neo4j Browser : <http://127.0.0.1:7474>. Pour se connecter manuellement, utiliser
`bolt://127.0.0.1:7687`, l'utilisateur `neo4j` et le mot de passe du `.env` local.
La vérification de connexion du driver et l'évaluation lexicale n'appellent aucun
modèle. Ne pas utiliser `--agent` pour un test sans facturation API.

Le `.env` local créé pour Neo4j ne configure pas le modèle ni les identifiants de
la démo Chainlit. Le test d'intégration utilise un modèle simulé ; l'usage normal
du chat conserve sa configuration Anthropic actuelle et peut être facturé si une
clé API est ajoutée.

La limite mémoire du conteneur est de 1,5 Gio, dont 512 Mio maximum de heap Java
et 256 Mio de page cache. Docker Desktop/WSL et l'application utilisent de la
mémoire supplémentaire. Arrêter la base libère les ressources du conteneur.

## Validation du lot 1

Une base temporaire distincte de la base de travail a validé le chargement,
l'index anglais, les contraintes, les sources présentes, l'idempotence, la
préservation d'un nœud indépendant, le rollback réel après une instruction
invalide, les neuf cas de recherche lexicale et un aller-retour Chainlit avec
Neo4j réel et modèle simulé. Elle a ensuite été supprimée.

Ces contrôles ne valident ni la fidélité scientifique du seed au manuel, ni le
choix sémantique d'un modèle réel sur les questions françaises.
