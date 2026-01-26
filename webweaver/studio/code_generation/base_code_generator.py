"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025-2026 Webweaver Development Team

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from abc import ABC, abstractmethod


class BaseCodeGenerator(ABC):
    """
    Base class for all code generation backends.

    Code generators are discovered dynamically by WebWeaver Studio and used
    to generate source code from a RecordingDocument.

    Implementations should be pure code emitters: they must not touch UI.
    """
    # pylint: disable=too-few-public-methods

    #: Stable unique identifier (e.g. "webweaver-core", "playwright-python")
    id: str

    #: Human-readable name shown in the UI menu
    name: str

    #: Short description (for tooltips / future dialogs)
    description: str

    @abstractmethod
    def generate(self, recording_document) -> str:
        """
        Generate source code from a RecordingDocument.

        :param recording_document: The RecordingDocument to generate code from
        :return: Generated source code as a string
        """
        raise NotImplementedError
