"""High-level API client for MOOC platform."""

from typing import Any, Dict, Optional

from moocscript.config import APIConfig
from moocscript.models import Result
from moocscript.request import RequestClient


class MOOCClient:
    """Main client for interacting with MOOC API."""
    
    def __init__(self, config: Optional[APIConfig] = None):
        """Initialize MOOC client.
        
        Args:
            config: API configuration. If None, creates default config.
        """
        self.config = config or APIConfig()
        self._request_client = RequestClient(self.config)
    
    def get_course_list(
        self,
        page: int = 1,
        page_size: int = 20,
        type: int = 30,
    ) -> Result:
        """Get list of courses.
        
        Args:
            page: Page number (starts from 1)
            page_size: Number of courses per page
            type: Course type filter (default: 30)
            
        Returns:
            Result containing pagination and course list
        """
        return self._request_client.request(
            endpoint="mob/course/getAllMyCourseList/v2",
            method="POST",
            query={
                "p": page,
                "psize": page_size,
                "type": type,
            },
        )
    
    def get_course_info(
        self,
        course_id: int,
        term_id: int,
    ) -> Result:
        """Get detailed course information including chapters.
        
        Args:
            course_id: Course ID
            term_id: Term ID
            
        Returns:
            Result containing course details with chapters
        """
        return self._request_client.request(
            endpoint="mob/course/courseLearn/v1",
            method="POST",
            query={
                "cid": course_id,
                "tid": term_id,
            },
        )
    
    def get_homework(
        self,
        term_id: int,
    ) -> Result:
        """Get homework paper for a term.
        
        Args:
            term_id: Term ID
            
        Returns:
            Result containing homework paper data
        """
        return self._request_client.request(
            endpoint="mob/course/homeworkPaperDto/v1",
            method="POST",
            query={
                "tid": term_id,
            },
        )
    
    def get_test_detail(
        self,
        test_id: int,
        is_exercise: bool = True,
        with_std_answer_and_analyse: bool = True,
    ) -> Result:
        """Get test/paper details with answers.
        
        Args:
            test_id: Test ID
            is_exercise: Whether it's an exercise
            with_std_answer_and_analyse: Include standard answers and analysis
            
        Returns:
            Result containing test paper data
        """
        return self._request_client.request(
            endpoint="mob/course/paperDetail/v1",
            method="POST",
            query={
                "testId": test_id,
                "isExercise": "true" if is_exercise else "false",
                "withStdAnswerAndAnalyse": "true" if with_std_answer_and_analyse else "false",
            },
        )
    
    def close(self):
        """Close the client and cleanup resources."""
        self._request_client.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
