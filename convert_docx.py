"""Script to convert Markdown files to DOCX format."""

import argparse
import re
from pathlib import Path

try:
    from docx import Document
    from docx.shared import Pt, Inches, RGBColor
    from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
    from docx.oxml.ns import qn
except ImportError:
    print("Error: Required packages not installed.")
    print("Please install: uv sync")
    print("Or manually: pip install python-docx")
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


def parse_markdown_to_docx(md_content: str, doc: Document):
    """Parse Markdown content and add it to a DOCX document with compact formatting.
    
    Args:
        md_content: Markdown content string
        doc: python-docx Document object
    """
    lines = md_content.split('\n')
    i = 0
    
    # Set default font for the document
    style = doc.styles['Normal']
    font = style.font
    font.name = '宋体'
    font.size = Pt(10.5)
    style._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    
    # Track if we're in an options section
    in_options_section = False
    option_index = 0
    
    while i < len(lines):
        line = lines[i].strip()
        original_line = lines[i]
        
        # Skip empty lines (we'll add minimal spacing manually)
        if not line:
            in_options_section = False
            option_index = 0
            i += 1
            continue
        
        # H1 - Title
        if line.startswith('# '):
            title = line[2:].strip()
            p = doc.add_paragraph()
            p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            run = p.add_run(title)
            run.font.size = Pt(16)
            run.font.bold = True
            run.font.name = '宋体'
            run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
            in_options_section = False
            option_index = 0
            i += 1
            continue
        
        # H2 - Section
        if line.startswith('## '):
            title = line[3:].strip()
            p = doc.add_paragraph()
            run = p.add_run(title)
            run.font.size = Pt(12)
            run.font.bold = True
            run.font.name = '宋体'
            run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
            in_options_section = False
            option_index = 0
            i += 1
            continue
        
        # H3 - Question number
        if line.startswith('### '):
            title = line[4:].strip()
            p = doc.add_paragraph()
            run = p.add_run(title)
            run.font.size = Pt(11)
            run.font.bold = True
            run.font.name = '宋体'
            run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
            in_options_section = False
            option_index = 0
            i += 1
            continue
        
        # Check for "**选项：**" to start options section
        if '**选项：**' in line:
            in_options_section = True
            option_index = 0
            # Still add the line
            match = re.match(r'\*\*(.+?)\*\*\s*(.*)', line)
            if match:
                bold_text = match.group(1)
                rest_text = match.group(2)
                p = doc.add_paragraph()
                run1 = p.add_run(bold_text)
                run1.font.bold = True
                run1.font.size = Pt(10.5)
                run1.font.name = '宋体'
                run1._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
                if rest_text:
                    run2 = p.add_run(rest_text)
                    run2.font.size = Pt(10.5)
                    run2.font.name = '宋体'
                    run2._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
            i += 1
            continue
        
        # Checkbox options - convert to ABCD format (only in options section)
        if re.match(r'^- \[[ xX]\] ', original_line):
            if in_options_section:
                # Extract option content
                content = re.sub(r'^- \[[ xX]\] ', '', original_line).strip()
                is_correct = '[x]' in original_line.lower() or '[X]' in original_line
                
                # Convert to ABCD (A=0, B=1, C=2, D=3, etc.)
                option_letter = chr(ord('A') + option_index)
                
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.3)
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)
                
                run1 = p.add_run(f"{option_letter}. ")
                run1.font.size = Pt(10.5)
                run1.font.name = '宋体'
                run1._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
                
                run2 = p.add_run(content)
                run2.font.size = Pt(10.5)
                run2.font.name = '宋体'
                run2._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
                
                if is_correct:
                    run1.font.bold = True
                    run2.font.bold = True
                
                option_index += 1
                i += 1
                continue
            else:
                # Not in options section, treat as regular list item
                content = re.sub(r'^- \[[ xX]\] ', '', original_line).strip()
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.2)
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)
                run = p.add_run(f"• {content}")
                run.font.size = Pt(10.5)
                run.font.name = '宋体'
                run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
                i += 1
                continue
        
        # If we hit a non-option line after options, reset
        if in_options_section and not re.match(r'^- \[[ xX]\] ', original_line):
            in_options_section = False
            option_index = 0
        
        # Bold text (like **题目：**, **标准答案：**, etc.)
        if line.startswith('**'):
            # Extract bold text and rest
            match = re.match(r'\*\*(.+?)\*\*\s*(.*)', line)
            if match:
                bold_text = match.group(1)
                rest_text = match.group(2)
                p = doc.add_paragraph()
                run1 = p.add_run(bold_text)
                run1.font.bold = True
                run1.font.size = Pt(10.5)
                run1.font.name = '宋体'
                run1._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
                if rest_text:
                    run2 = p.add_run(rest_text)
                    run2.font.size = Pt(10.5)
                    run2.font.name = '宋体'
                    run2._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
            i += 1
            continue
        
        # List items (starting with -)
        if line.startswith('- ') and not re.match(r'^- \[[ xX]\] ', original_line):
            content = line[2:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.2)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            run = p.add_run(f"• {content}")
            run.font.size = Pt(10.5)
            run.font.name = '宋体'
            run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
            i += 1
            continue
        
        # Horizontal rule
        if line.startswith('---'):
            # Add minimal spacing instead of a line
            in_options_section = False
            option_index = 0
            i += 1
            continue
        
        # Regular text
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(line)
        run.font.size = Pt(10.5)
        run.font.name = '宋体'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
        i += 1


def convert_markdown_to_docx(md_file: Path, docx_file: Path):
    """Convert a single Markdown file to DOCX.
    
    Args:
        md_file: Path to Markdown file
        docx_file: Path to output DOCX file
    """
    # Read Markdown content
    with open(md_file, "r", encoding="utf-8") as f:
        md_content = f.read()
    
    # Create new document
    doc = Document()
    
    # Set page margins (compact)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.5)
        section.bottom_margin = Inches(0.5)
        section.left_margin = Inches(0.6)
        section.right_margin = Inches(0.6)
    
    # Parse and add content
    parse_markdown_to_docx(md_content, doc)
    
    # Save document
    doc.save(docx_file)


def main():
    """Main function to convert Markdown files to DOCX."""
    parser = argparse.ArgumentParser(
        description="Convert Markdown files to DOCX format"
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
        default="output/docx",
        help="Output directory for DOCX files (default: output/docx)",
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
    docx_dir = Path(args.output)
    
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
        
        # Convert to DOCX
        print("=" * 60)
        print("Converting to DOCX...")
        print("=" * 60)
        
        total_exported = 0
        total_skipped = 0
        total_errors = 0
        
        for course_name, markdown_files in courses_data.items():
            # Create course directory in DOCX output
            safe_course_name = course_name.replace("/", "_").replace("\\", "_")
            course_docx_dir = docx_dir / safe_course_name
            course_docx_dir.mkdir(parents=True, exist_ok=True)
            
            course_exported = 0
            course_skipped = 0
            
            for md_file in markdown_files:
                try:
                    # Generate DOCX filename
                    docx_filename = md_file.stem + ".docx"
                    docx_file = course_docx_dir / docx_filename
                    
                    # Skip if DOCX file already exists
                    if docx_file.exists():
                        course_skipped += 1
                        total_skipped += 1
                        continue
                    
                    # Convert to DOCX
                    convert_markdown_to_docx(md_file, docx_file)
                    course_exported += 1
                    total_exported += 1
                except Exception as e:
                    total_errors += 1
                    print(f"  Failed to convert {md_file.name}: {str(e)}")
            
            status = f"{course_exported} exported"
            if course_skipped > 0:
                status += f", {course_skipped} skipped"
            print(f"  {course_name}: {status}")
        
        print()
        print("=" * 60)
        print(f"   Total DOCX files exported: {total_exported}")
        if total_skipped > 0:
            print(f"   Total DOCX files skipped: {total_skipped} (already exist)")
        if total_errors > 0:
            print(f"   Errors: {total_errors}")
        print(f"   DOCX files saved to: {docx_dir}")
        print("=" * 60)
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
