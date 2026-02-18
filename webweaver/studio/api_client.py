"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025-2026 Webweaver Development Team

This program is free software : you can redistribute it and /or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.If not, see < https://www.gnu.org/licenses/>.
"""
import asyncio
from dataclasses import dataclass
import aiohttp


@dataclass()
class ApiResponse:
    """
    Represents the result of an API request.

    This object is used as a unified return type for all API calls made by
    :class:`ApiClient`, whether the request succeeds or fails.

    Attributes:
        status_code (int):
            HTTP status code returned by the server.
            Will typically be 0 when a request fails before receiving a response.

        body (dict | str):
            Parsed response body.
            - JSON responses are returned as a dict.
            - Non-JSON responses are returned as raw text.
            May be ``None`` if the request failed.

        content_type (str):
            The response content type (e.g. ``"application/json"``).
            May be ``None`` if no response was received.

        exception_msg (str):
            Error message populated when an exception occurs
            (connection failure, timeout, etc.). ``None`` on success.
    """

    status_code: int
    body: dict | str
    content_type : str
    exception_msg : str

    def __init__(self,
                 status_code: int = 0,
                 body: dict | str = None,
                 content_type : str = None,
                 exception_msg : str = None):
        """
        Initialise an ApiResponse instance.

        Args:
            status_code:
                HTTP status code returned by the server.
            body:
                Parsed response payload (JSON dict or raw text).
            content_type:
                MIME type returned in the response headers.
            exception_msg:
                Error message if the request failed.
        """
        self.status_code = status_code
        self.body = body
        self.content_type = content_type
        self.exception_msg = exception_msg


class ApiClient:
    """
    Lightweight asynchronous HTTP client wrapper around aiohttp.

    Provides convenience methods for common HTTP verbs and returns
    results as :class:`ApiResponse` objects for consistent handling.

    Notes:
        - Each request creates a new ``aiohttp.ClientSession``.
        - JSON responses are automatically deserialized.
        - Network and timeout errors are captured and returned inside
          an ``ApiResponse`` instead of raising exceptions.
    """

    CONTENT_TYPE_JSON: str = "application/json"

    # Convenience wrappers for specific HTTP methods
    async def call_api_post(self,
                            url: str,
                            json_data: dict = None,
                            timeout: int = 2):
        """
        Perform an asynchronous HTTP POST request.

        Args:
            url: Target endpoint URL.
            json_data: Optional JSON payload sent in the request body.
            timeout: Total request timeout in seconds.

        Returns:
            ApiResponse containing the result or error information.
        """
        return await self._call_api("post", url, json_data, timeout)

    async def call_api_get(self,
                           url: str,
                           json_data: dict = None,
                           timeout: int = 2):
        """
        Perform an asynchronous HTTP GET request.

        Args:
            url: Target endpoint URL.
            json_data: Optional JSON payload (rare for GET but supported).
            timeout: Total request timeout in seconds.

        Returns:
            ApiResponse containing the result or error information.
        """
        return await self._call_api("get", url, json_data, timeout)

    async def call_api_delete(self,
                              url: str,
                              json_data: dict = None,
                              timeout: int = 2):
        """
        Perform an asynchronous HTTP DELETE request.

        Args:
            url: Target endpoint URL.
            json_data: Optional JSON payload.
            timeout: Total request timeout in seconds.

        Returns:
            ApiResponse containing the result or error information.
        """
        return await self._call_api("delete", url, json_data, timeout)

    async def call_api_patch(self,
                             url: str,
                             json_data: dict = None,
                             timeout: int = 2):
        """
        Perform an asynchronous HTTP PATCH request.

        Args:
            url: Target endpoint URL.
            json_data: Optional JSON payload.
            timeout: Total request timeout in seconds.

        Returns:
            ApiResponse containing the result or error information.
        """
        return await self._call_api("patch", url, json_data, timeout)

    async def _call_api(self, method: str, url: str,
                        json_data: dict = None,
                        timeout: int = 2) -> "ApiResponse":
        """
        Internal generic API caller used by all HTTP verb wrappers.

        This method dynamically resolves the HTTP method on an
        ``aiohttp.ClientSession`` and executes the request.

        Behaviour:
            - JSON responses are parsed to ``dict``.
            - Non-JSON responses are returned as text.
            - Connection and timeout errors are caught and returned
              as an ``ApiResponse`` with ``exception_msg`` populated.

        Args:
            method:
                HTTP method name (e.g. ``"get"``, ``"post"``, ``"delete"``).
            url:
                Target endpoint URL.
            json_data:
                Optional JSON request payload.
            timeout:
                Total request timeout in seconds.

        Returns:
            ApiResponse representing either a successful response
            or an error condition.
        """
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as session:
                # Dynamically get the aiohttp method (get, post, delete, etc.)
                http_method = getattr(session, method.lower())
                async with http_method(url, json=json_data) as resp:
                    if resp.content_type == self.CONTENT_TYPE_JSON:
                        body = await resp.json()
                    else:
                        body = await resp.text()

                    return ApiResponse(
                        status_code=resp.status,
                        body=body,
                        content_type=resp.content_type
                    )

        except (aiohttp.ClientConnectionError,
                aiohttp.ClientError,
                asyncio.TimeoutError) as ex:
            return ApiResponse(exception_msg=str(ex))
