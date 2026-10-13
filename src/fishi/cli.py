"""CLI entry point. Sample mode requires no network or credentials."""
import argparse
import json
import os
from pathlib import Path
from .export import transform, write_csv
from .reddit import get_app_token, get_user_submissions


def main():
    parser = argparse.ArgumentParser(description="FISHI read-only Reddit importer")
    parser.add_argument("--sample", action="store_true", help="Use fictional data without API access")
    parser.add_argument("--reddit-user", default="FISHI_WORKS")
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    if args.sample:
        posts = json.loads((Path(__file__).resolve().parents[2] / "sample_posts.json").read_text(encoding="utf-8"))
        origin = "sample"
    else:
        required = ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USER_AGENT"]
        missing = [key for key in required if not os.getenv(key)]
        if missing:
            parser.error("Missing environment variables: " + ", ".join(missing))
        token = get_app_token(*(os.environ[key] for key in required))
        posts = get_user_submissions(args.reddit_user, token, os.environ["REDDIT_USER_AGENT"])
        origin = "reddit_api"
    publications, metrics = transform(posts, args.reddit_user)
    if origin == "sample":
        for row in publications:
            row["record_origin"] = "sample"
        for row in metrics:
            row["data_source"] = "sample"
    write_csv(args.output_dir, publications, metrics)
    print(f"Exported {len(publications)} publications and {len(metrics)} metric snapshots to {args.output_dir}")


if __name__ == "__main__":
    main()
