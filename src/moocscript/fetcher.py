"""Data fetcher for retrieving all course papers."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from moocscript.client import MOOCClient


class CourseFetcher:
    """Fetcher for retrieving all course data including quizzes and exams."""

    def __init__(self, client: MOOCClient, output_dir: Path):
        """Initialize fetcher.

        Args:
            client: MOOC API client
            output_dir: Directory to save JSON files
        """
        self.client = client
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Statistics
        self.stats = {
            "courses": 0,
            "quizzes": 0,
            "exams_objective": 0,
            "exams_subjective": 0,
            "homeworks": 0,
            "errors": 0,
        }

    def fetch_all_courses(self, page_size: int = 20) -> List[Dict[str, Any]]:
        """Fetch all courses from all pages.

        Args:
            page_size: Number of courses per page

        Returns:
            List of all courses
        """
        all_courses = []
        page = 1

        print("Fetching course list...")

        while True:
            result = self.client.get_course_list(page=page, page_size=page_size)

            if result.status.code != 0:
                print(f"Failed to get course list: {result.status.message}")
                break

            results = result.results
            if not results or "result" not in results:
                break

            courses = results.get("result", [])
            if not courses:
                break

            all_courses.extend(courses)
            pagination = results.get("pagination", {})
            total_pages = pagination.get("totlePageCount", 1)

            print(f"  Page {page}/{total_pages}: Found {len(courses)} courses")

            if page >= total_pages:
                break

            page += 1

        print(f"Total courses: {len(all_courses)}")
        return all_courses

    def fetch_course_info(self, course: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Fetch detailed information for a course.

        Args:
            course: Course dictionary

        Returns:
            Course info result or None if failed
        """
        course_id = course.get("id")
        term_id = course.get("termPanel", {}).get("id")
        course_name = course.get("name", "Unknown")

        if not course_id or not term_id:
            return None

        result = self.client.get_course_info(course_id, term_id)

        if result.status.code != 0:
            print(
                f"  Failed to get course info for {course_name}: {result.status.message}"
            )
            return None

        return result.results

    def fetch_paper(
        self,
        test_id: int,
        paper_name: str,
        paper_type: str = "quiz",
    ) -> Optional[Dict[str, Any]]:
        """Fetch a paper (quiz/exam) by test ID.

        Args:
            test_id: Test/paper ID
            paper_name: Name of the paper
            paper_type: Type of paper (quiz, exam, homework)

        Returns:
            Paper data or None if failed
        """
        try:
            result = self.client.get_test_detail(test_id)

            if result.status.code != 0:
                print(f"    Failed to fetch {paper_name}: {result.status.message}")
                self.stats["errors"] += 1
                return None

            return {
                "status": {
                    "code": result.status.code,
                    "message": result.status.message,
                },
                "results": result.results,
            }
        except Exception as e:
            print(f"    Error fetching {paper_name}: {str(e)}")
            self.stats["errors"] += 1
            return None

    def save_paper_json(
        self,
        paper_data: Dict[str, Any],
        course_name: str,
        paper_name: str,
        paper_type: str,
    ) -> Path:
        """Save paper data to JSON file.

        Args:
            paper_data: Paper data dictionary
            course_name: Name of the course
            paper_name: Name of the paper
            paper_type: Type of paper

        Returns:
            Path to saved file
        """
        # Create course directory
        safe_course_name = course_name.replace("/", "_").replace("\\", "_")
        course_dir = self.output_dir / "json" / safe_course_name
        course_dir.mkdir(parents=True, exist_ok=True)

        # Sanitize filename
        safe_paper_name = paper_name.replace("/", "_").replace("\\", "_")
        # Get testId if available, otherwise omit it
        test_id = paper_data.get('results', {}).get('mocPaperDto', {}).get('testId')
        if test_id:
            filename = f"{paper_type}_{safe_paper_name}_{test_id}.json"
        else:
            filename = f"{paper_type}_{safe_paper_name}.json"

        filepath = course_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(paper_data, f, ensure_ascii=False, indent=2)

        return filepath

    def fetch_all_papers_for_course(
        self,
        course: Dict[str, Any],
        course_info: Dict[str, Any],
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Fetch all papers (quizzes, exams, homeworks) for a course.

        Args:
            course: Course dictionary
            course_info: Course info results

        Returns:
            Dictionary with lists of paper info
        """
        course_name = course.get("name", "Unknown")
        term_dto = course_info.get("termDto") or {}
        if not isinstance(term_dto, dict):
            term_dto = {}
        chapters = term_dto.get("chapters") or []
        if not isinstance(chapters, list):
            chapters = []

        papers = {
            "quiz": [],
            "exam_objective": [],
            "exam_subjective": [],
            "homework": [],
        }

        print(f"\nProcessing course: {course_name}")
        print(f"  Chapters: {len(chapters)}")

        for chapter in chapters:
            if not isinstance(chapter, dict):
                continue
            chapter_name = chapter.get("name", "Unknown")

            # Fetch quizzes
            quizs = chapter.get("quizs") or []
            if not isinstance(quizs, list):
                quizs = []
            for quiz in quizs:
                if not isinstance(quiz, dict):
                    continue
                quiz_name = quiz.get("name", "Unknown")
                content_id = quiz.get("contentId")

                if not content_id:
                    continue

                print(f"  Fetching quiz: {quiz_name} (ID: {content_id})")
                paper_data = self.fetch_paper(content_id, quiz_name, "quiz")

                if paper_data:
                    filepath = self.save_paper_json(
                        paper_data, course_name, quiz_name, "quiz"
                    )
                    papers["quiz"].append(
                        {
                            "name": quiz_name,
                            "chapter_name": chapter_name,
                            "content_id": content_id,
                            "file": filepath,
                            "data": paper_data,
                        }
                    )
                    self.stats["quizzes"] += 1

            # Fetch exams
            exam = chapter.get("exam")
            if exam and isinstance(exam, dict):
                # Objective exam
                object_test = exam.get("objectTestVo")
                if object_test and isinstance(object_test, dict):
                    exam_id = object_test.get("id")
                    exam_name = object_test.get("name", "客观题考试")

                    if exam_id:
                        print(
                            f"  Fetching objective exam: {exam_name} (ID: {exam_id})"
                        )
                        paper_data = self.fetch_paper(
                            exam_id, exam_name, "exam_objective"
                        )

                        if paper_data:
                            filepath = self.save_paper_json(
                                paper_data, course_name, exam_name, "exam_objective"
                            )
                            papers["exam_objective"].append(
                                {
                                    "name": exam_name,
                                    "chapter_name": chapter_name,
                                    "test_id": exam_id,
                                    "file": filepath,
                                    "data": paper_data,
                                }
                            )
                            self.stats["exams_objective"] += 1

                # Subjective exam
                subject_test = exam.get("subjectTestVo")
                if subject_test and isinstance(subject_test, dict):
                    exam_id = subject_test.get("id")
                    exam_name = subject_test.get("name", "主观题考试")

                    if exam_id:
                        print(
                            f"  Fetching subjective exam: {exam_name} (ID: {exam_id})"
                        )
                        paper_data = self.fetch_paper(
                            exam_id, exam_name, "exam_subjective"
                        )

                        if paper_data:
                            filepath = self.save_paper_json(
                                paper_data, course_name, exam_name, "exam_subjective"
                            )
                            papers["exam_subjective"].append(
                                {
                                    "name": exam_name,
                                    "chapter_name": chapter_name,
                                    "test_id": exam_id,
                                    "file": filepath,
                                    "data": paper_data,
                                }
                            )
                            self.stats["exams_subjective"] += 1

            # Fetch homeworks
            homeworks = chapter.get("homeworks") or []
            if not isinstance(homeworks, list):
                homeworks = []
            for homework in homeworks:
                if not isinstance(homework, dict):
                    continue
                homework_name = homework.get("name", "Unknown")
                content_id = homework.get("contentId")

                if not content_id:
                    continue

                print(f"  Fetching homework: {homework_name} (ID: {content_id})")
                paper_data = self.fetch_paper(content_id, homework_name, "homework")

                if paper_data:
                    filepath = self.save_paper_json(
                        paper_data, course_name, homework_name, "homework"
                    )
                    papers["homework"].append(
                        {
                            "name": homework_name,
                            "chapter_name": chapter_name,
                            "content_id": content_id,
                            "file": filepath,
                            "data": paper_data,
                        }
                    )
                    self.stats["homeworks"] += 1

        return papers

    def fetch_all(self) -> Dict[str, Any]:
        """Fetch all courses and their papers.

        Returns:
            Dictionary containing all fetched data
        """
        # Fetch all courses
        courses = self.fetch_all_courses()

        if not courses:
            print("No courses found")
            return {}

        return self.fetch_selected_courses(courses)

    def fetch_selected_courses(self, courses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fetch papers for selected courses.

        Args:
            courses: List of course dictionaries to fetch

        Returns:
            Dictionary containing all fetched data
        """
        if not courses:
            return {}

        all_data = {}

        # Process each course
        for i, course in enumerate(courses, 1):
            course_name = course.get("name", "Unknown")
            print(f"\n{'=' * 60}")
            print(f"Course {i}/{len(courses)}: {course_name}")
            print(f"{'=' * 60}")

            # Fetch course info
            course_info = self.fetch_course_info(course)
            if not course_info:
                continue

            # Fetch all papers
            papers = self.fetch_all_papers_for_course(course, course_info)

            all_data[course_name] = {
                "course": course,
                "course_info": course_info,
                "papers": papers,
            }

            self.stats["courses"] += 1

        return all_data

    def print_stats(self):
        """Print fetching statistics."""
        print("\n" + "=" * 60)
        print("Fetching Statistics")
        print("=" * 60)
        print(f"  Courses processed: {self.stats['courses']}")
        print(f"  Quizzes fetched: {self.stats['quizzes']}")
        print(f"  Objective exams fetched: {self.stats['exams_objective']}")
        print(f"  Subjective exams fetched: {self.stats['exams_subjective']}")
        print(f"  Homeworks fetched: {self.stats['homeworks']}")
        print(f"  Errors: {self.stats['errors']}")
        print("=" * 60)
