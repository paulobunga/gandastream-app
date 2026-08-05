import argparse
import json
import logging
import sys
from pathlib import Path

from models import ProjectState
from config import settings
from pipeline import Pipeline

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def list_runs() -> None:
    runs_dir = Path(settings.run_output_dir)
    if not runs_dir.exists():
        print("No runs found.")
        return
    for run_dir in sorted(runs_dir.iterdir()):
        state_path = run_dir / "_project_state_final.json"
        if state_path.exists():
            data = json.loads(state_path.read_text())
            print(f"{run_dir.name}: title={data.get('screenplay', {}).get('title', 'N/A')} "
                  f"duration={data.get('screenplay', {}).get('total_estimated_duration', 'N/A')}s "
                  f"created={data.get('created_at', 'N/A')}")
        else:
            print(f"{run_dir.name}: partial")


def inspect_stage(run_id: str, stage: str) -> None:
    run_dir = Path(settings.run_output_dir) / run_id
    path = run_dir / f"{stage}.json"
    if not path.exists():
        print(f"Stage file not found: {path}")
        sys.exit(1)
    print(path.read_text())


def main():
    parser = argparse.ArgumentParser(description="AfriDrama Pipeline CLI")
    sub = parser.add_subparsers(dest="command")

    run = sub.add_parser("run", help="Run full pipeline")
    run.add_argument("--region", default=settings.default_region)
    run.add_argument("--genre", default=settings.default_genre)
    run.add_argument("--accent", default=settings.accent)

    resume = sub.add_parser("resume", help="Resume pipeline from a stage")
    resume.add_argument("--run-id", required=True)
    resume.add_argument("--from-stage", required=True)

    sub.add_parser("list-runs", help="List previous runs")

    inspect = sub.add_parser("inspect", help="Inspect a stage file from a run")
    inspect.add_argument("--run-id", required=True)
    inspect.add_argument("--stage", required=True)

    args = parser.parse_args()

    if args.command == "run":
        state = ProjectState(region=args.region, genre=args.genre, accent=args.accent, language=settings.language)
        pipeline = Pipeline()
        result = pipeline.run_all(state)
        print(f"\nPipeline complete. Run ID: {result.run_id}")
        print(f"Output dir: {result.get_output_dir()}")
        if result.screenplay:
            print(f"Screenplay: {result.screenplay.title}")
            print(f"Duration: {result.screenplay.total_estimated_duration:.0f}s")
        if result.posts:
            print(f"Posts generated for {len(result.posts)} platforms")

    elif args.command == "resume":
        state = ProjectState(run_id=args.run_id)
        pipeline = Pipeline()
        result = pipeline.run_from(state, args.from_stage)
        print(f"Resumed from {args.from_stage}. Run ID: {result.run_id}")

    elif args.command == "list-runs":
        list_runs()

    elif args.command == "inspect":
        inspect_stage(args.run_id, args.stage)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
