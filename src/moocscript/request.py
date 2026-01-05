"""Core request handling for MOOC API."""

import json
from typing import Any, Dict, Optional

import requests

from moocscript.config import APIConfig
from moocscript.models import Result, Status


class RequestError(Exception):
    """Base exception for request errors."""
    pass


class APIRequestError(RequestError):
    """Exception raised when API request fails."""
    pass


class RequestClient:
    """Core HTTP client for MOOC API requests."""
    
    def __init__(self, config: APIConfig):
        """Initialize request client.
        
        Args:
            config: API configuration
        """
        self.config = config
        self.session = requests.Session()
        self.session.headers.update(self.config.headers)
    
    def request(
        self,
        endpoint: str,
        method: str = "POST",
        query: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
    ) -> Result:
        """Make API request.
        
        Args:
            endpoint: API endpoint path (relative to base_url)
            method: HTTP method (default: POST)
            query: Query parameters
            body: Request body (for POST requests)
            
        Returns:
            Result object containing status and results
            
        Raises:
            APIRequestError: If request fails
        """
        url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        # Prepare query parameters
        params = query.copy() if query else {}
        params["mob-token"] = self.config.mob_token
        
        # Convert all query values to strings (matching original behavior)
        params = {k: str(v) for k, v in params.items()}
        
        try:
            # Make request
            if method.upper() == "POST":
                response = self.session.post(
                    url,
                    params=params,
                    json=body,
                    timeout=self.config.timeout,
                )
            else:
                response = self.session.get(
                    url,
                    params=params,
                    timeout=self.config.timeout,
                )
            
            response.raise_for_status()
            data = response.json()
            
            # Wrap response in Result structure
            return Result.from_dict(data)
            
        except requests.exceptions.RequestException as e:
            # Return error result matching original structure
            return Result(
                status=Status(
                    code=-1,
                    message=f"Request failed: {str(e)}"
                ),
                results=None
            )
        except json.JSONDecodeError as e:
            raise APIRequestError(f"Failed to parse JSON response: {str(e)}")
        except Exception as e:
            raise APIRequestError(f"Unexpected error: {str(e)}")
    
    def close(self):
        """Close the session."""
        self.session.close()
