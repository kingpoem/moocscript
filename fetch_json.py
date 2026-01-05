"""Script to fetch all courses, quizzes, exams and save as JSON files."""

import argparse
from pathlib import Path

from moocscript import APIConfig, MOOCClient
from moocscript.fetcher import CourseFetcher


def main():
    """Main function to fetch all data and save as JSON."""
    parser = argparse.ArgumentParser(
        description="Fetch all MOOC courses, quizzes, exams and save as JSON"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output",
        help="Output directory (default: output)",
    )
    parser.add_argument(
        "--token",
        type=str,
        default=None,
        help="MOOC mob token (overrides environment variable)",
    )
    
    args = parser.parse_args()
    
    # Initialize client
    if args.token:
        config = APIConfig(mob_token=args.token)
    else:
        config = APIConfig.from_env()
    
    if not config.mob_token:
        print("Error: MOOC_MOB_TOKEN not set!")
        print("  Please set it via environment variable: export MOOC_MOB_TOKEN=your_token")
        print("  Or use --token argument")
        return
    
    client = MOOCClient(config)
    output_dir = Path(args.output)
    
    try:
        # Initialize fetcher
        fetcher = CourseFetcher(client, output_dir)
        
        # Fetch all data
        print("Starting to fetch all courses and papers...\n")
        all_data = fetcher.fetch_all()
        
        # Print statistics
        fetcher.print_stats()
        
        if not all_data:
            print("\nNo data fetched")
            return
        
        # Save summary
        import json
        summary_file = output_dir / "json" / "summary.json"
        summary_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create summary
        summary = {
            "total_courses": fetcher.stats["courses"],
            "total_quizzes": fetcher.stats["quizzes"],
            "total_exams_objective": fetcher.stats["exams_objective"],
            "total_exams_subjective": fetcher.stats["exams_subjective"],
            "total_homeworks": fetcher.stats["homeworks"],
            "total_errors": fetcher.stats["errors"],
            "courses": [
                {
                    "name": course_name,
                    "course_id": data["course"].get("id"),
                    "papers": {
                        "quiz": len(data["papers"]["quiz"]),
                        "exam_objective": len(data["papers"]["exam_objective"]),
                        "exam_subjective": len(data["papers"]["exam_subjective"]),
                        "homework": len(data["papers"]["homework"]),
                    }
                }
                for course_name, data in all_data.items()
            ]
        }
        
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"\nAll done!")
        print(f"   JSON files saved to: {output_dir / 'json'}")
        print(f"   Summary saved to: {summary_file}")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()


if __name__ == "__main__":
    main()
