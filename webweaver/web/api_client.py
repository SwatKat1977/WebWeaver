"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025 SwatKat1977

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
    """ Class for keeping track of api return data. """
    status_code: int
    body: dict | str
    content_type : str
    exception_msg : str

    def __init__(self,
                 status_code: int = 0,
                 body: dict | str = None,
                 content_type : str = None,
                 exception_msg : str = None):
        self.status_code = status_code
        self.body = body
        self.content_type = content_type
        self.exception_msg = exception_msg


class ApiClient:
    CONTENT_TYPE_JSON: str = "application/json"

    # Convenience wrappers for specific HTTP methods
    async def call_api_post(self,
                            url: str,
                            json_data: dict = None,
                            timeout: int = 2):
        return await self._call_api("post", url, json_data, timeout)

    async def call_api_get(self,
                           url: str,
                           json_data: dict = None,
                           timeout: int = 2):
        return await self._call_api("get", url, json_data, timeout)

    async def call_api_delete(self,
                              url: str,
                              json_data: dict = None,
                              timeout: int = 2):
        return await self._call_api("delete", url, json_data, timeout)

    async def call_api_patch(self,
                             url: str,
                             json_data: dict = None,
                             timeout: int = 2):
        return await self._call_api("patch", url, json_data, timeout)

    async def _call_api(self, method: str, url: str,
                        json_data: dict = None,
                        timeout: int = 2) -> "ApiResponse":
        """
        Generic internal method to make an API call with the specified HTTP method.
        """
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as session:
                # Dynamically get the aiohttp method (get, post, delete, etc.)
                http_method = getattr(session, method.lower())
                async with http_method(url, json=json_data, allow_redirects=False) as resp:
                    print("Final URL:", resp.url)
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
