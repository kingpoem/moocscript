"""Markdown exporter for converting JSON data to Markdown format."""

import html
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple


def clean_unicode_control_chars(text: str) -> str:
    """Remove Unicode control characters and invisible characters.
    
    Args:
        text: Input text string
        
    Returns:
        Cleaned text string
    """
    if not text:
        return ""
    
    # Remove common Unicode control characters
    # U+200E: Left-to-Right Mark (LRM)
    # U+200F: Right-to-Left Mark (RLM)
    # U+200B: Zero Width Space
    # U+200C: Zero Width Non-Joiner
    # U+200D: Zero Width Joiner
    # U+FEFF: Zero Width No-Break Space (BOM)
    # U+202A-U+202E: Directional formatting characters
    # U+2060-U+206F: Word joiner and invisible characters
    control_chars = [
        '\u200E',  # LRM
        '\u200F',  # RLM
        '\u200B',  # Zero Width Space
        '\u200C',  # Zero Width Non-Joiner
        '\u200D',  # Zero Width Joiner
        '\uFEFF',  # Zero Width No-Break Space
        '\u202A',  # Left-to-Right Embedding
        '\u202B',  # Right-to-Left Embedding
        '\u202C',  # Pop Directional Formatting
        '\u202D',  # Left-to-Right Override
        '\u202E',  # Right-to-Left Override
        '\u2060',  # Word Joiner
        '\u2061',  # Function Application
        '\u2062',  # Invisible Times
        '\u2063',  # Invisible Separator
        '\u2064',  # Invisible Plus
        '\u2066',  # Left-to-Right Isolate
        '\u2067',  # Right-to-Left Isolate
        '\u2068',  # First Strong Isolate
        '\u2069',  # Pop Directional Isolate
    ]
    
    for char in control_chars:
        text = text.replace(char, '')
    
    return text


def html_to_text(html_content: str) -> str:
    """Convert HTML content to plain text, handling common tags."""
    if not html_content:
        return ""
    
    # Remove HTML tags but preserve content
    text = re.sub(r'<[^>]+>', '', html_content)
    
    # Decode HTML entities
    text = html.unescape(text)
    
    # Remove Unicode control characters
    text = clean_unicode_control_chars(text)
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text


def format_question_title(title: str) -> str:
    """Format question title, converting HTML to plain text."""
    return html_to_text(title)


def format_option(option: Dict[str, Any], index: int) -> str:
    """Format a single option for multiple choice questions."""
    content = html_to_text(option.get("content", ""))
    is_correct = option.get("answer", False)
    
    # Use checkbox or letter prefix
    prefix = f"- [{'x' if is_correct else ' '}] " if is_correct else "- [ ] "
    
    return f"{prefix}{content}"


def format_objective_question(question: Dict[str, Any], q_num: int) -> str:
    """Format an objective question (multiple choice, single choice, etc.)."""
    question_type = question.get("type", 1)
    title = format_question_title(question.get("title", ""))
    options = question.get("optionDtos") or []
    if not isinstance(options, list):
        options = []
    std_answer = question.get("stdAnswer", "")
    analyse = question.get("analyse", "")
    
    # Question type labels
    type_labels = {
        1: "单选题",
        2: "多选题",
        3: "判断题",
        4: "填空题",
        5: "简答题",
    }
    type_label = type_labels.get(question_type, f"题型{question_type}")
    
    lines = [f"### {q_num}. {type_label}"]
    lines.append("")
    lines.append(f"**题目：** {title}")
    lines.append("")
    
    # Format options
    if options:
        lines.append("**选项：**")
        lines.append("")
        for i, option in enumerate(options, 1):
            if isinstance(option, dict):
                lines.append(format_option(option, i))
        lines.append("")
    
    # Standard answer
    if std_answer:
        lines.append(f"**标准答案：** {std_answer}")
        lines.append("")
    
    # Analysis
    if analyse:
        analyse_text = html_to_text(analyse)
        lines.append(f"**解析：** {analyse_text}")
        lines.append("")
    
    # Mark correct options
    if options:
        correct_options = [
            opt for opt in options 
            if isinstance(opt, dict) and opt.get("answer", False)
        ]
        if correct_options:
            correct_texts = [
                html_to_text(opt.get("content", "")) 
                for opt in correct_options 
                if isinstance(opt, dict)
            ]
            if correct_texts:
                lines.append(f"**正确答案：** {', '.join(correct_texts)}")
                lines.append("")
    
    lines.append("---")
    lines.append("")
    
    return "\n".join(lines)


def format_subjective_question(question: Dict[str, Any], q_num: int) -> str:
    """Format a subjective question."""
    title = format_question_title(question.get("title", ""))
    judge_dtos = question.get("judgeDtos") or []
    if not isinstance(judge_dtos, list):
        judge_dtos = []
    sample_answers = question.get("sampleAnswers", "")
    
    lines = [f"### {q_num}. 主观题"]
    lines.append("")
    lines.append(f"**题目：** {title}")
    lines.append("")
    
    # Sample answers
    if sample_answers:
        if isinstance(sample_answers, str):
            answer_text = html_to_text(sample_answers)
        else:
            answer_text = str(sample_answers)
        lines.append("**参考答案：**")
        lines.append("")
        lines.append(answer_text)
        lines.append("")
    
    # Judge criteria
    if judge_dtos:
        lines.append("**评分标准：**")
        lines.append("")
        for judge in judge_dtos:
            if isinstance(judge, dict):
                msg = html_to_text(judge.get("msg", ""))
                if msg:
                    lines.append(f"- {msg}")
        lines.append("")
    
    lines.append("---")
    lines.append("")
    
    return "\n".join(lines)


def export_paper_to_markdown(
    paper_data: Dict[str, Any],
    course_name: str = "",
    chapter_name: str = "",
    paper_name: str = "",
    paper_type: str = "quiz",
) -> str:
    """Export a paper (quiz/exam) to Markdown format.
    
    Args:
        paper_data: Paper data from API response
        course_name: Name of the course
        chapter_name: Name of the chapter
        paper_name: Name of the paper/quiz/exam
        paper_type: Type of paper (quiz, exam, homework)
        
    Returns:
        Markdown formatted string
    """
    lines = []
    
    # Header
    lines.append(f"# {paper_name}")
    lines.append("")
    if course_name:
        lines.append(f"**课程：** {course_name}")
    if chapter_name:
        lines.append(f"**章节：** {chapter_name}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Extract paper data
    moc_paper_dto = paper_data.get("results", {}).get("mocPaperDto", {})
    if not moc_paper_dto:
        lines.append("*无法获取题目数据*")
        return "\n".join(lines)
    
    objective_questions = moc_paper_dto.get("objectiveQList") or []
    if not isinstance(objective_questions, list):
        objective_questions = []
    subjective_questions = moc_paper_dto.get("subjectiveQList") or []
    if not isinstance(subjective_questions, list):
        subjective_questions = []
    
    total_questions = len(objective_questions) + len(subjective_questions)
    
    lines.append(f"**题目总数：** {total_questions} (选择题: {len(objective_questions)}, 主观题: {len(subjective_questions)})")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Objective questions
    if objective_questions:
        lines.append("## 选择题")
        lines.append("")
        for i, question in enumerate(objective_questions, 1):
            lines.append(format_objective_question(question, i))
    
    # Subjective questions
    if subjective_questions:
        lines.append("## 主观题")
        lines.append("")
        start_num = len(objective_questions) + 1
        for i, question in enumerate(subjective_questions, start_num):
            lines.append(format_subjective_question(question, i))
    
    return "\n".join(lines)


def export_course_to_markdown(
    papers: Dict[str, List[Dict[str, Any]]],
    output_dir: Path,
    course_name: str,
) -> Tuple[int, int]:
    """Export all papers from a course to Markdown files.
    
    Args:
        papers: Dictionary with paper types as keys and lists of paper info as values
        output_dir: Output directory for Markdown files
        course_name: Name of the course
        
    Returns:
        Tuple of (exported_count, skipped_count)
    """
    import json
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create course directory
    safe_course_name = sanitize_filename(course_name)
    course_dir = output_dir / safe_course_name
    course_dir.mkdir(parents=True, exist_ok=True)
    
    exported_count = 0
    skipped_count = 0
    markdown_files_created = []
    
    # Process each paper type
    for paper_type, paper_list in papers.items():
        for paper_info in paper_list:
            paper_name = paper_info.get("name", "Unknown")
            chapter_name = paper_info.get("chapter_name", "")
            paper_file = paper_info.get("file")
            
            # Use paper data directly if available, otherwise read from file
            paper_json = paper_info.get("data")
            
            if not paper_json and paper_file:
                if not paper_file.exists():
                    continue
                try:
                    with open(paper_file, "r", encoding="utf-8") as f:
                        paper_json = json.load(f)
                except Exception as e:
                    print(f"  Failed to read {paper_name}: {str(e)}")
                    continue
            
            if not paper_json:
                continue
            
            try:
                # Generate Markdown
                markdown_content = export_paper_to_markdown(
                    paper_json,
                    course_name=course_name,
                    chapter_name=chapter_name,
                    paper_name=paper_name,
                    paper_type=paper_type,
                )
                
                # Save Markdown file
                safe_name = sanitize_filename(paper_name)
                # Add prefix to avoid filename conflicts
                prefix_map = {
                    "quiz": "测验",
                    "exam_objective": "客观题考试",
                    "exam_subjective": "主观题考试",
                    "homework": "作业",
                }
                prefix = prefix_map.get(paper_type, paper_type)
                markdown_file = course_dir / f"{prefix}_{safe_name}.md"
                
                # Skip if file already exists
                if markdown_file.exists():
                    skipped_count += 1
                    markdown_files_created.append(markdown_file)
                    continue
                
                with open(markdown_file, "w", encoding="utf-8") as f:
                    f.write(markdown_content)
                
                exported_count += 1
                markdown_files_created.append(markdown_file)
            except Exception as e:
                print(f"  Failed to export {paper_name}: {str(e)}")
                import traceback
                traceback.print_exc()
    
    # Merge all Markdown files for this course
    if markdown_files_created:
        merged_md_name = f"{safe_course_name}_完整版.md"
        merged_md_file = course_dir / merged_md_name
        
        # Skip if merged file already exists
        if not merged_md_file.exists():
            try:
                # Sort files by name for consistent ordering
                markdown_files_created = sorted(markdown_files_created)
                
                merged_content = []
                merged_content.append(f"# {course_name} - 完整版\n")
                merged_content.append("---\n")
                
                for md_file in markdown_files_created:
                    try:
                        with open(md_file, "r", encoding="utf-8") as f:
                            content = f.read()
                            # Clean Unicode control characters from merged content
                            content = clean_unicode_control_chars(content)
                            merged_content.append(content)
                            merged_content.append("\n\n---\n\n")
                    except Exception as e:
                        print(f"  Warning: Failed to read {md_file.name} for merging: {str(e)}")
                        continue
                
                with open(merged_md_file, "w", encoding="utf-8") as f:
                    f.write("\n".join(merged_content))
            except Exception as e:
                print(f"  Warning: Failed to create merged Markdown: {str(e)}")
    
    return exported_count, skipped_count


def sanitize_filename(name: str) -> str:
    """Sanitize a string to be used as a filename."""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, "_")
    
    # Limit length
    if len(name) > 200:
        name = name[:200]
    
    return name.strip()
