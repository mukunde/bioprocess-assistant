"""python -m ingestion extract|review|decide|export|publish"""
import argparse
import os
from pathlib import Path

from ingestion.pipeline import Settings, extract_pdf, revise_run
from ingestion.publish import export_snapshot, publish_snapshot
from ingestion.store import decide, write_json


def main():
    parser = argparse.ArgumentParser(description="PDF extraction with mandatory manual evidence review")
    commands = parser.add_subparsers(dest="command", required=True)
    extract = commands.add_parser("extract")
    extract.add_argument("pdf", type=Path)
    extract.add_argument("--output", type=Path, default=Path("data/ingestion"))
    extract.add_argument("--settings", type=Path, help="JSON Settings; local inference by default")
    extract.add_argument("--title")
    for name in ("review", "decide", "revise", "export", "publish"):
        sub = commands.add_parser(name)
        sub.add_argument("run", type=Path)
        if name == "review":
            sub.add_argument("--port", type=int, default=8765)
        if name == "decide":
            sub.add_argument("record_id")
            sub.add_argument("action", choices=["approve", "reject"])
            sub.add_argument("--reviewer", required=True)
            sub.add_argument("--note", required=True)
            sub.add_argument("--source-checked", action="store_true")
        if name == "export":
            sub.add_argument("--output", type=Path, required=True)
        if name == "revise":
            sub.add_argument("--extraction", type=Path, required=True)
            sub.add_argument("--output", type=Path, default=Path("data/ingestion"))
    args = parser.parse_args()
    try:
        if args.command == "extract":
            settings = Settings.model_validate_json(args.settings.read_text(encoding="utf-8")) if args.settings else Settings()
            print(extract_pdf(args.pdf, args.output, settings, args.title))
        elif args.command == "review":
            from ingestion.review import serve
            serve(args.run.resolve(), args.port)
        elif args.command == "decide":
            decide(args.run.resolve(), args.record_id, args.action, args.reviewer, args.note, args.source_checked)
            print("Decision recorded")
        elif args.command == "revise":
            print(revise_run(args.run.resolve(), args.extraction, args.output))
        else:
            snapshot = export_snapshot(args.run.resolve())
            if args.command == "export":
                destination = args.output.resolve()
                if destination.exists() or destination.is_relative_to(args.run.resolve()):
                    raise ValueError("Export to a new file outside the immutable run directory")
                write_json(destination, snapshot)
                print(f"Approved snapshot: {snapshot['snapshot_id']}")
            else:
                from dotenv import load_dotenv
                from neo4j import GraphDatabase
                load_dotenv()
                with GraphDatabase.driver(os.environ["NEO4J_URI"], auth=(os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"])) as driver:
                    publish_snapshot(driver, os.environ["NEO4J_DATABASE"], snapshot)
                print(f"Published evidence snapshot: {snapshot['snapshot_id']}")
    except (ValueError, OSError, RuntimeError) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
