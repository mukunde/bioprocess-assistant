"""Load Neo4j schema and seed from graph/*.cypher into AuraDB. Idempotent."""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j.exceptions import AuthError, ServiceUnavailable

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_FILE = PROJECT_ROOT / "graph" / "schema.cypher"
SEED_FILE = PROJECT_ROOT / "graph" / "seed.cypher"


def read_statements(file_path: Path) -> list[str]:
    # Strip // line comments (Cypher syntax) then split on `;` *outside* string
    # literals — sources may contain `;` between citations and break a naive split.
    text = file_path.read_text(encoding="utf-8")
    lines = [line for line in text.splitlines() if not line.strip().startswith("//")]
    cleaned = "\n".join(lines)
    statements: list[str] = []
    buf: list[str] = []
    in_string = False
    for c in cleaned:
        if c == '"':
            in_string = not in_string
            buf.append(c)
        elif c == ";" and not in_string:
            stmt = "".join(buf).strip()
            if stmt:
                statements.append(stmt)
            buf = []
        else:
            buf.append(c)
    stmt = "".join(buf).strip()
    if stmt:
        statements.append(stmt)
    return statements


def execute(driver, database: str, statements: list[str]) -> None:
    with driver.session(database=database) as session:
        for stmt in statements:
            session.run(stmt)


def main() -> int:
    load_dotenv(PROJECT_ROOT / ".env")

    required = ("NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD", "NEO4J_DATABASE")
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        print(f"[ERR] Variables manquantes dans .env : {', '.join(missing)}")
        return 1

    uri = os.environ["NEO4J_URI"]
    user = os.environ["NEO4J_USERNAME"]
    password = os.environ["NEO4J_PASSWORD"]
    database = os.environ["NEO4J_DATABASE"]

    print(f"[1/4] Connexion a {uri} ...")
    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        driver.verify_connectivity()
    except AuthError:
        print("[ERR] Authentification refusee. Verifie NEO4J_USERNAME / NEO4J_PASSWORD dans .env.")
        return 1
    except ServiceUnavailable:
        print("[ERR] Instance injoignable. Si elle est en pause AuraDB, reveille-la depuis la console.")
        return 1

    schema_stmts = read_statements(SCHEMA_FILE)
    print(f"[2/4] Schema : {len(schema_stmts)} contrainte(s) ...")
    execute(driver, database, schema_stmts)

    seed_stmts = read_statements(SEED_FILE)
    print(f"[3/4] Seed   : {len(seed_stmts)} instruction(s) ...")
    execute(driver, database, seed_stmts)

    print("[4/4] Validation du graphe :")
    with driver.session(database=database) as session:
        counts = session.run(
            """
            MATCH (n)
            WHERE n:Symptom OR n:Cause OR n:Action
            RETURN labels(n)[0] AS label, count(*) AS n
            ORDER BY label
            """
        )
        for r in counts:
            print(f"      - {r['label']:<10} {r['n']} noeud(s)")

        print()
        print("      Chemins symptome -> cause -> action :")
        paths = session.run(
            """
            MATCH (s:Symptom)-[:INDICATES]->(c:Cause)-[:RESOLVED_BY]->(a:Action)
            RETURN s.name AS symptom, c.name AS cause, a.name AS action
            ORDER BY symptom, cause
            """
        )
        for r in paths:
            print(f"        - {r['symptom']}")
            print(f"            -> {r['cause']}")
            print(f"                -> {r['action']}")

    driver.close()
    print()
    print("[OK] Graphe charge. Walking skeleton etape 1 validee.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
