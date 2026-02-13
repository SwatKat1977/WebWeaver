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
import typing
from webweaver.studio.recording.recording_event_type import RecordingEventType
from webweaver.studio.persistence.recording_document import RecordingDocument


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

    def __init__(self):
        self._lines: list[str] = []
        self._recording_document: typing.Optional[dict] = None
        self._settings = None
        # Indent level 0 is at column 1, after then it's level * 4
        self._indent_level = 0

    def generate(self, recording_document: RecordingDocument, settings) -> str:
        """
        Generate source code from a RecordingDocument.

        :param recording_document: The RecordingDocument to generate code from
        :param settings: Settings specific to the recording file

        :return: Generated source code as a string
        """
        self._recording_document = recording_document
        self._settings = settings

        self._begin_file()

        recording_data = recording_document.data["recording"]

        for event in recording_data["events"]:
            self._handle_event(event)

        self._end_file()

        return "\n".join(self._lines)

    @abstractmethod
    def _begin_file(self):
        raise NotImplementedError

    @abstractmethod
    def _end_file(self):
        raise NotImplementedError

    def _handle_event(self, event: dict):
        event_type = RecordingEventType(event["type"])
        payload = event["payload"]

        method_name = f"_on_{event_type.name.lower()}"

        handler = getattr(self, method_name, self._on_unknown)

        handler(payload)

    @abstractmethod
    def _on_unknown(self, payload):
        raise NotImplementedError

    @abstractmethod
    def _on_dom_click(self, payload):
        raise NotImplementedError

    @abstractmethod
    def _on_dom_type(self, payload):
        raise NotImplementedError

    @abstractmethod
    def _on_dom_check(self, payload):
        raise NotImplementedError

    @abstractmethod
    def _on_dom_select(self, payload):
        raise NotImplementedError

    @abstractmethod
    def _on_nav_goto(self, payload):
        raise NotImplementedError

    @abstractmethod
    def _on_wait(self, payload):
        raise NotImplementedError
