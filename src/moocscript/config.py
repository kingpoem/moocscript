"""Configuration management for MoocForge API client."""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class APIConfig:
    """Configuration for MOOC API client.
    
    Attributes:
        base_url: Base URL for the MOOC API
        mob_token: Authentication token (can be empty, set via environment or later)
        headers: HTTP headers to include in requests
        timeout: Request timeout in seconds
    """
    
    base_url: str = "https://www.icourse163.org/"
    mob_token: str = ""
    timeout: int = 30
    headers: Dict[str, str] = field(default_factory=lambda: {
        "edu-app-type": "android",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://www.icourse163.org/",
        "Content-Type": "application/json",
    })
    
    @classmethod
    def from_env(cls) -> "APIConfig":
        """Create configuration from environment variables.
        
        Reads MOOC_MOB_TOKEN from environment if available.
        """
        import os
        mob_token = os.getenv("MOOC_MOB_TOKEN", "")
        return cls(mob_token=mob_token)
