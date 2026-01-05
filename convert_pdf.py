"""Script to convert Markdown files to PDF format."""

import argparse
from pathlib import Path

try:
    import markdown
    from weasyprint import HTML
    from weasyprint.text.fonts import FontConfiguration
except ImportError:
    print("Error: Required packages not installed.")
    print("Please install: uv sync")
    print("Or manually: pip install markdown weasyprint")
    exit(1)


def find_markdown_files(markdown_dir: Path) -> dict:
    """Find all Markdown files organized by course.
    
    Args:
        markdown_dir: Directory containing course subdirectories with Markdown files
        
    Returns:
        Dictionary mapping course names to lists of markdown files
    """
    courses_data = {}
    
    if not markdown_dir.exists():
        print(f"Markdown directory not found: {markdown_dir}")
        print("  Please run convert_markdown.py first to generate Markdown files")
        return courses_data
    
    # Iterate through course directories
    for course_dir in markdown_dir.iterdir():
        if not course_dir.is_dir():
            continue
        
        course_name = course_dir.name
        markdown_files = []
        
        # Find all Markdown files
        for md_file in course_dir.glob("*.md"):
            markdown_files.append(md_file)
        
        if markdown_files:
            courses_data[course_name] = markdown_files
    
    return courses_data


def convert_markdown_to_pdf(md_file: Path, pdf_file: Path):
    """Convert a single Markdown file to PDF.
    
    Args:
        md_file: Path to Markdown file
        pdf_file: Path to output PDF file
    """
    # Read Markdown content
    with open(md_file, "r", encoding="utf-8") as f:
        md_content = f.read()
    
    # Convert Markdown to HTML
    md = markdown.Markdown(extensions=['extra', 'codehilite'])
    html_content = md.convert(md_content)
    
    # Add basic CSS styling
    css_style = """
    @page {
        size: A4;
        margin: 2cm;
    }
    body {
        font-family: "DejaVu Sans", "SimSun", "Microsoft YaHei", sans-serif;
        font-size: 12pt;
        line-height: 1.6;
        color: #333;
    }
    h1 {
        font-size: 24pt;
        margin-top: 1em;
        margin-bottom: 0.5em;
        border-bottom: 2px solid #333;
        padding-bottom: 0.3em;
    }
    h2 {
        font-size: 18pt;
        margin-top: 0.8em;
        margin-bottom: 0.4em;
        border-bottom: 1px solid #666;
        padding-bottom: 0.2em;
    }
    h3 {
        font-size: 14pt;
        margin-top: 0.6em;
        margin-bottom: 0.3em;
    }
    code {
        font-family: "DejaVu Sans Mono", "Consolas", monospace;
        background-color: #f5f5f5;
        padding: 2px 4px;
        border-radius: 3px;
    }
    pre {
        background-color: #f5f5f5;
        padding: 10px;
        border-radius: 5px;
        overflow-x: auto;
    }
    pre code {
        background-color: transparent;
        padding: 0;
    }
    ul, ol {
        margin-left: 1.5em;
    }
    li {
        margin-bottom: 0.3em;
    }
    strong {
        font-weight: bold;
    }
    """
    
    # Wrap HTML content
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>{css_style}</style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Convert HTML to PDF
    font_config = FontConfiguration()
    html_doc = HTML(string=full_html)
    html_doc.write_pdf(pdf_file, font_config=font_config)


def main():
    """Main function to convert Markdown files to PDF."""
    parser = argparse.ArgumentParser(
        description="Convert Markdown files to PDF format"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="output/markdown",
        help="Input directory containing Markdown files (default: output/markdown)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output/pdf",
        help="Output directory for PDF files (default: output/pdf)",
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
        import json
        courses_file = Path(args.courses_file)
        if courses_file.exists():
            try:
                with open(courses_file, "r", encoding="utf-8") as f:
                    selected_courses = json.load(f)
            except Exception as e:
                print(f"Failed to load courses file: {str(e)}")
                selected_courses = None
    
    markdown_dir = Path(args.input)
    pdf_dir = Path(args.output)
    
    if not markdown_dir.exists():
        print(f"Input directory not found: {markdown_dir}")
        print("  Please run convert_markdown.py first to generate Markdown files")
        return
    
    try:
        # Find all Markdown files
        print("Scanning for Markdown files...")
        courses_data = find_markdown_files(markdown_dir)
        
        if not courses_data:
            print("No Markdown files found")
            return
        
        total_courses = len(courses_data)
        total_files = sum(len(files) for files in courses_data.values())
        print(f"Found {total_courses} courses with {total_files} Markdown files")
        
        # Filter by selected courses if specified
        if selected_courses:
            filtered_courses_data = {
                name: files for name, files in courses_data.items()
                if name in selected_courses
            }
            if filtered_courses_data:
                print(f"Processing {len(filtered_courses_data)} selected course(s): {', '.join(filtered_courses_data.keys())}")
                courses_data = filtered_courses_data
            else:
                print("No matching courses found in selected list")
                return
        
        print()
        
        # Convert to PDF
        print("=" * 60)
        print("Converting to PDF...")
        print("=" * 60)
        
        total_exported = 0
        total_errors = 0
        
        for course_name, markdown_files in courses_data.items():
            # Create course directory in PDF output
            safe_course_name = course_name.replace("/", "_").replace("\\", "_")
            course_pdf_dir = pdf_dir / safe_course_name
            course_pdf_dir.mkdir(parents=True, exist_ok=True)
            
            for md_file in markdown_files:
                try:
                    # Generate PDF filename
                    pdf_filename = md_file.stem + ".pdf"
                    pdf_file = course_pdf_dir / pdf_filename
                    
                    # Convert to PDF
                    convert_markdown_to_pdf(md_file, pdf_file)
                    total_exported += 1
                except Exception as e:
                    total_errors += 1
                    print(f"  Failed to convert {md_file.name}: {str(e)}")
            
            print(f"  {course_name}: {len(markdown_files)} PDF files exported")
        
        print()
        print("=" * 60)
        print(f"   Total PDF files exported: {total_exported}")
        if total_errors > 0:
            print(f"   Errors: {total_errors}")
        print(f"   PDF files saved to: {pdf_dir}")
        print("=" * 60)
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
