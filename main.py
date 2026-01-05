"""Example usage of MoocForge API client."""

import json
from pathlib import Path

from moocscript import APIConfig, MOOCClient


def save_to_json(data: dict, filename: str):
    """Save data to JSON file with pretty formatting."""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    filepath = output_dir / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved: {filepath}")


def dict_to_json_serializable(obj):
    """Convert objects to JSON serializable format."""
    if hasattr(obj, "__dict__"):
        return {k: dict_to_json_serializable(v) for k, v in obj.__dict__.items()}
    elif isinstance(obj, dict):
        return {k: dict_to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [dict_to_json_serializable(item) for item in obj]
    else:
        return obj


def main():
    """Main example function."""
    # Initialize client
    # You can set mob_token via environment variable: export MOOC_MOB_TOKEN=your_token
    # Or pass it directly: config = APIConfig(mob_token="your_token")
    config = APIConfig.from_env()
    client = MOOCClient(config)

    try:
        # Example 1: Get course list
        print("Fetching course list...")
        courses_result = client.get_course_list(page=1, page_size=20)

        if courses_result.status.code == 0:
            save_to_json(
                dict_to_json_serializable(courses_result.__dict__), "course_list.json"
            )

            # Extract courses if available
            results = courses_result.results
            if results and "result" in results and results["result"]:
                first_course = results["result"][0]
                course_id = first_course["id"]
                term_id = first_course["termPanel"]["id"]

                print(f"\nFound course: {first_course.get('name', 'Unknown')}")
                print(f"Course ID: {course_id}, Term ID: {term_id}")

                # Example 2: Get course info with chapters
                print("\nFetching course details...")
                course_info_result = client.get_course_info(course_id, term_id)

                if course_info_result.status.code == 0:
                    save_to_json(
                        dict_to_json_serializable(course_info_result.__dict__),
                        "course_info.json",
                    )

                    # Example 3: Check and get homework if available
                    term_dto = course_info_result.results.get("termDto", {})
                    chapters = term_dto.get("chapters", [])

                    # Find first chapter with homeworks
                    homework_content_id = None
                    for chapter in chapters:
                        homeworks = chapter.get("homeworks", [])
                        if homeworks:
                            homework_content_id = homeworks[0].get("contentId")
                            homework_name = homeworks[0].get("name", "Unknown")
                            print(
                                f"\nFound homework: {homework_name} (ID: {homework_content_id})"
                            )
                            break

                    if homework_content_id:
                        print(
                            f"\nFetching homework (contentId: {homework_content_id})..."
                        )
                        # Note: The homework API actually uses term_id, but we check if homework exists first
                        homework_result = client.get_homework(term_id)

                        if homework_result.status.code == 0:
                            save_to_json(
                                dict_to_json_serializable(homework_result.__dict__),
                                "homework.json",
                            )
                        else:
                            print(
                                f"Failed to get homework: {homework_result.status.message}"
                            )
                            print(
                                "Note: This term may not have homework papers, or the API may require different parameters."
                            )
                    else:
                        print("\nNo homeworks found in this course's chapters")

                    # Example 4: Check and get quiz if available
                    quiz_content_id = None
                    for chapter in chapters:
                        quizs = chapter.get("quizs", [])
                        if quizs:
                            quiz_content_id = quizs[0].get("contentId")
                            quiz_name = quizs[0].get("name", "Unknown")
                            print(f"\nFound quiz: {quiz_name} (ID: {quiz_content_id})")
                            break

                    if quiz_content_id:
                        print(
                            f"\nFetching quiz detail (contentId: {quiz_content_id})..."
                        )
                        quiz_result = client.get_test_detail(quiz_content_id)

                        if quiz_result.status.code == 0:
                            save_to_json(
                                dict_to_json_serializable(quiz_result.__dict__),
                                "quiz.json",
                            )
                        else:
                            print(f"Failed to get quiz: {quiz_result.status.message}")
                    else:
                        print("\nNo quizzes found in this course's chapters")
                else:
                    print(
                        f"Failed to get course info: {course_info_result.status.message}"
                    )
            else:
                print("No courses found in response")
        else:
            print(f"Failed to get course list: {courses_result.status.message}")
            print("\nNote: Make sure you have set MOOC_MOB_TOKEN environment variable")
            print("      or passed mob_token to APIConfig")

    except Exception as e:
        print(f"Error: {str(e)}")

    finally:
        client.close()


if __name__ == "__main__":
    main()
