"""Legacy API compatibility module - re-exports from client."""

# For backward compatibility, re-export main functions
from moocscript.client import MOOCClient
from moocscript.config import APIConfig

__all__ = ["MOOCClient", "APIConfig"]

# Aliases matching original TypeScript API
def course_list(client: MOOCClient, page: int, page_size: int):
    """Get course list (alias for client method)."""
    return client.get_course_list(page, page_size)


def course_info(client: MOOCClient, course_id: int, term_id: int):
    """Get course info (alias for client method)."""
    return client.get_course_info(course_id, term_id)


def homework(client: MOOCClient, term_id: int):
    """Get homework (alias for client method)."""
    return client.get_homework(term_id)


def test(client: MOOCClient, test_id: int):
    """Get test detail (alias for client method)."""
    return client.get_test_detail(test_id)
