"""MoocForge - Python implementation of mooc-helper core API client."""

from moocscript.client import MOOCClient
from moocscript.config import APIConfig
from moocscript.fetcher import CourseFetcher
from moocscript.markdown_exporter import (
    export_course_to_markdown,
    export_paper_to_markdown,
)

__version__ = "0.1.0"
__all__ = [
    "MOOCClient",
    "APIConfig",
    "CourseFetcher",
    "export_course_to_markdown",
    "export_paper_to_markdown",
]
