"""Local job precomputation: python backend/build_job_index.py."""
import argparse
import asyncio

from semantic_matching import AnalysisError, SemanticMatcher


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rebuild", action="store_true", help="Replace incompatible cache with real embeddings.")
    args = parser.parse_args()
    try:
        service = SemanticMatcher()
        asyncio.run(service.ensure_index(force=args.rebuild))
    except (AnalysisError, ValueError, OSError) as exc:
        # Controlled local errors only; never expose the key.
        parser.exit(1, f"{exc}\n")
    print(f"Validated {len(service.jobs)} jobs, {service.status()['model']}, {service.status()['dimensions']} dimensions, local CPU.")


if __name__ == "__main__":
    main()
