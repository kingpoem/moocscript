"""一次性获取所有课程数据并转换为 Markdown 和 DOCX 格式。

该脚本依次执行 fetch_json.py、convert_markdown.py 和 convert_docx.py，提供便捷的一键运行方式。
"""

import argparse
import json
import subprocess
import sys
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


def save_selected_courses(courses: List[Dict[str, Any]], output_dir: Path):
    """Save selected course names to a file for later use.
    
    Args:
        courses: List of selected course dictionaries
        output_dir: Output directory
    """
    course_names = [course.get("name", "Unknown") for course in courses]
    courses_file = output_dir / "json" / "selected_courses.json"
    courses_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(courses_file, "w", encoding="utf-8") as f:
        json.dump(course_names, f, ensure_ascii=False, indent=2)


def load_selected_courses(output_dir: Path) -> List[str]:
    """Load selected course names from file.
    
    Args:
        output_dir: Output directory
        
    Returns:
        List of selected course names, or empty list if file doesn't exist
    """
    courses_file = output_dir / "json" / "selected_courses.json"
    if courses_file.exists():
        try:
            with open(courses_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def main():
    """主函数 - 依次执行 fetch_json、convert_markdown 和 convert_pdf。"""
    parser = argparse.ArgumentParser(
        description="获取所有 MOOC 课程、测验、考试并转换为 Markdown 和 DOCX 格式"
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
        "--skip-markdown",
        action="store_true",
        help="Skip Markdown conversion (only fetch JSON)",
    )
    parser.add_argument(
        "--skip-docx",
        action="store_true",
        help="Skip DOCX conversion (only fetch JSON and convert to Markdown)",
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
        print("Step 1: Fetching course list...\n")
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
        
        # Save selected courses for later steps
        save_selected_courses(selected_courses, output_dir)
        
        # Fetch data for selected courses only
        print(f"\nStep 2: Fetching JSON data for {len(selected_courses)} selected course(s)...\n")
        all_data = fetcher.fetch_selected_courses(selected_courses)
        
        if not all_data:
            print("\nNo data fetched")
            return
        
        # Print statistics
        fetcher.print_stats()
        
        # Save summary
        summary_file = output_dir / "json" / "summary.json"
        summary_file.parent.mkdir(parents=True, exist_ok=True)
        
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
        
        print(f"\nJSON files saved to: {output_dir / 'json'}")
        print(f"Summary saved to: {summary_file}")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    finally:
        client.close()
    
    # Convert to Markdown if requested
    if not args.skip_markdown:
        print("\nStep 3: Converting to Markdown...")
        cmd = [
            sys.executable,
            "convert_markdown.py",
            "--input", str(output_dir / "json"),
            "--output", str(output_dir / "markdown"),
        ]
        # Pass selected courses file if available
        courses_file = output_dir / "json" / "selected_courses.json"
        if courses_file.exists():
            cmd.extend(["--courses-file", str(courses_file)])
        
        result = subprocess.run(cmd)
        
        if result.returncode != 0:
            print("Failed to convert to Markdown")
            return
        
        # Convert to DOCX if requested
        if not args.skip_docx:
            print("\nStep 4: Converting to DOCX...")
            cmd = [
                sys.executable,
                "convert_docx.py",
                "--input", str(output_dir / "markdown"),
                "--output", str(output_dir / "docx"),
            ]
            # Pass selected courses file if available
            courses_file = output_dir / "json" / "selected_courses.json"
            if courses_file.exists():
                cmd.extend(["--courses-file", str(courses_file)])
            
            result = subprocess.run(cmd)
            
            if result.returncode != 0:
                print("Failed to convert to DOCX")
                return
    
    print("\nAll done!")


if __name__ == "__main__":
    main()
