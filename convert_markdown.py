"""Script to convert JSON files to Markdown format."""

import argparse
import json
from pathlib import Path

from moocscript.markdown_exporter import export_course_to_markdown


def find_json_files(json_dir: Path) -> dict:
    """Find all JSON files organized by course.
    
    Args:
        json_dir: Directory containing course subdirectories with JSON files
        
    Returns:
        Dictionary mapping course names to lists of paper info
    """
    courses_data = {}
    
    if not json_dir.exists():
        print(f"JSON directory not found: {json_dir}")
        return courses_data
    
    # Iterate through course directories
    for course_dir in json_dir.iterdir():
        if not course_dir.is_dir():
            continue
        
        course_name = course_dir.name
        papers = {
            "quiz": [],
            "exam_objective": [],
            "exam_subjective": [],
            "homework": [],
        }
        
        # Find all JSON files
        for json_file in course_dir.glob("*.json"):
            if json_file.name == "summary.json":
                continue
            
            # Parse filename: {type}_{name}_{id}.json
            name_parts = json_file.stem.split("_", 2)
            if len(name_parts) >= 2:
                paper_type = name_parts[0]
                paper_name = "_".join(name_parts[1:])
            else:
                paper_type = "unknown"
                paper_name = json_file.stem
            
            # Try to extract chapter name from JSON content
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    paper_json = json.load(f)
                
                # Verify JSON structure
                if not isinstance(paper_json, dict):
                    continue
                
                # Try to get chapter name from file path or metadata
                chapter_name = ""
                
                # Only add if paper_type is valid
                if paper_type in papers:
                    papers[paper_type].append({
                        "name": paper_name,
                        "chapter_name": chapter_name,
                        "file": json_file,
                        "data": paper_json,
                    })
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON {json_file.name}: {str(e)}")
            except Exception as e:
                print(f"Failed to read {json_file.name}: {str(e)}")
        
        if any(papers.values()):
            courses_data[course_name] = papers
    
    return courses_data


def load_summary(json_dir: Path) -> dict:
    """Load summary.json if available.
    
    Args:
        json_dir: Directory containing JSON files
        
    Returns:
        Summary dictionary or empty dict
    """
    summary_file = json_dir / "summary.json"
    if summary_file.exists():
        try:
            with open(summary_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def main():
    """Main function to convert JSON files to Markdown."""
    parser = argparse.ArgumentParser(
        description="Convert JSON files to Markdown format"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="output/json",
        help="Input directory containing JSON files (default: output/json)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output/markdown",
        help="Output directory for Markdown files (default: output/markdown)",
    )
    parser.add_argument(
        "--courses",
        nargs="+",
        default=None,
        help="List of course names to process (only process these courses)",
    )
    parser.add_argument(
        "--courses-file",
        type=str,
        default=None,
        help="JSON file containing list of course names to process",
    )
    
    args = parser.parse_args()
    
    # Load courses from file if specified
    selected_courses = args.courses
    if args.courses_file:
        courses_file = Path(args.courses_file)
        if courses_file.exists():
            try:
                with open(courses_file, "r", encoding="utf-8") as f:
                    selected_courses = json.load(f)
            except Exception as e:
                print(f"Failed to load courses file: {str(e)}")
                selected_courses = None
    
    json_dir = Path(args.input)
    markdown_dir = Path(args.output)
    
    if not json_dir.exists():
        print(f"Input directory not found: {json_dir}")
        print("  Please run fetch_json.py first to download data")
        return
    
    try:
        # Load summary if available
        summary = load_summary(json_dir)
        if summary:
            print(f"Found {summary.get('total_courses', 0)} courses")
            print(f"Quizzes: {summary.get('total_quizzes', 0)}")
            print(f"Exams: {summary.get('total_exams_objective', 0)} objective, "
                  f"{summary.get('total_exams_subjective', 0)} subjective")
            print(f"   Homeworks: {summary.get('total_homeworks', 0)}")
            print()
        
        # Find all JSON files
        print("Scanning for JSON files...")
        courses_data = find_json_files(json_dir)
        
        if not courses_data:
            print("No JSON files found")
            return
        
        print(f"Found {len(courses_data)} courses with papers")
        
        # Filter by selected courses if specified
        if selected_courses:
            filtered_courses_data = {
                name: papers for name, papers in courses_data.items()
                if name in selected_courses
            }
            if filtered_courses_data:
                print(f"Processing {len(filtered_courses_data)} selected course(s): {', '.join(filtered_courses_data.keys())}")
                courses_data = filtered_courses_data
            else:
                print("No matching courses found in selected list")
                return
        
        print()
        
        # Convert to Markdown
        print("=" * 60)
        print("Converting to Markdown...")
        print("=" * 60)
        
        total_exported = 0
        total_errors = 0
        
        for course_name, papers in courses_data.items():
            try:
                exported = export_course_to_markdown(
                    papers,
                    markdown_dir,
                    course_name,
                )
                total_exported += exported
                print(f"  {course_name}: {exported} papers exported")
            except Exception as e:
                total_errors += 1
                print(f"  {course_name}: Failed - {str(e)}")
        
        print()
        print("=" * 60)
        print(f"   Total papers exported: {total_exported}")
        if total_errors > 0:
            print(f"   Errors: {total_errors}")
        print(f"   Markdown files saved to: {markdown_dir}")
        print("=" * 60)
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
