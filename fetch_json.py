"""Script to fetch all courses, quizzes, exams and save as JSON files."""

import argparse
from pathlib import Path
from typing import List, Dict, Any

from moocscript import APIConfig, MOOCClient
from moocscript.fetcher import CourseFetcher


def select_courses_interactively(courses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Interactive course selection.
    
    Args:
        courses: List of course dictionaries
        
    Returns:
        List of selected course dictionaries
    """
    print("=" * 60)
    print("课程列表")
    print("=" * 60)
    
    # Display all courses
    for i, course in enumerate(courses, 1):
        course_name = course.get("name", "Unknown")
        print(f"{i:3d}. {course_name}")
    
    print("=" * 60)
    print("\n请选择要下载的课程（输入序号，多个用逗号分隔，如：1,3,5 或输入 all 下载全部）：")
    
    while True:
        try:
            user_input = input("> ").strip()
            
            if not user_input:
                print("未选择任何课程")
                return []
            
            if user_input.lower() == "all":
                print(f"\n已选择全部 {len(courses)} 门课程")
                return courses
            
            # Parse selections
            selections = [s.strip() for s in user_input.split(",")]
            selected_indices = []
            
            for sel in selections:
                if "-" in sel:
                    # Range selection (e.g., "1-5")
                    try:
                        start, end = map(int, sel.split("-"))
                        selected_indices.extend(range(start, end + 1))
                    except ValueError:
                        print(f"无效的范围格式: {sel}")
                        continue
                else:
                    try:
                        idx = int(sel)
                        if 1 <= idx <= len(courses):
                            selected_indices.append(idx)
                        else:
                            print(f"无效的序号: {idx} (范围: 1-{len(courses)})")
                            continue
                    except ValueError:
                        print(f"无效的输入: {sel}")
                        continue
            
            if not selected_indices:
                print("未选择任何有效课程，请重新输入")
                continue
            
            # Remove duplicates and sort
            selected_indices = sorted(set(selected_indices))
            selected_courses = [courses[i - 1] for i in selected_indices]
            
            print(f"\n已选择 {len(selected_courses)} 门课程：")
            for idx, course in zip(selected_indices, selected_courses):
                print(f"  {idx}. {course.get('name', 'Unknown')}")
            
            return selected_courses
            
        except KeyboardInterrupt:
            print("\n\n已取消选择")
            return []
        except Exception as e:
            print(f"输入错误: {str(e)}，请重新输入")


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
    parser.add_argument(
        "--all",
        action="store_true",
        help="Download all courses without interactive selection",
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
        
        # Fetch course list first
        print("Fetching course list...\n")
        courses = fetcher.fetch_all_courses()
        
        if not courses:
            print("No courses found")
            return
        
        # Interactive course selection (unless --all flag is set)
        if args.all:
            selected_courses = courses
            print(f"\n已选择全部 {len(courses)} 门课程（--all 模式）")
        else:
            selected_courses = select_courses_interactively(courses)
            
            if not selected_courses:
                print("No courses selected. Exiting.")
                return
        
        # Fetch data for selected courses only
        print(f"\nStarting to fetch papers for {len(selected_courses)} selected course(s)...\n")
        all_data = fetcher.fetch_selected_courses(selected_courses)
        
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
