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
import wx
from webweaver.studio.recording.recording_event_type import RecordingEventType
from webweaver.studio.ui.step_editors.assert_step_editor import \
    AssertionStepEditor
from webweaver.studio.ui.step_editors.check_step_editor import \
    CheckStepEditor
from webweaver.studio.ui.step_editors.click_step_editor import \
    ClickStepEditor
from webweaver.studio.ui.step_editors.dom_get_step_editor import \
    DomGetStepEditor
from webweaver.studio.ui.step_editors.navgoto_step_editor import \
    NavGotoStepEditor
from webweaver.studio.ui.step_editors.rest_api_step_editor import \
    RestApiStepEditor
from webweaver.studio.ui.step_editors.scroll_step_editor import \
    ScrollType
from webweaver.studio.ui.step_editors.select_step_editor import \
    SelectStepEditor
from webweaver.studio.ui.step_editors.sendkeys_step_editor import \
    SendkeysStepEditor
from webweaver.studio.ui.step_editors.type_step_editor import \
    TypeStepEditor
from webweaver.studio.ui.step_editors.wait_step_editor import \
    WaitStepEditor


class RecordingStepEditorRegistry:
    """
    Registry for mapping recording step types to their corresponding editor
    dialogs.

    This registry allows different step types in a recording to be associated
    with specific wx.Dialog editor classes. Editors can be registered at
    runtime and later instantiated dynamically based on the step type.
    """

    _registry = {}

    @classmethod
    def register(cls, step_type: RecordingEventType, editor_class: wx.Dialog):
        """
        Register an editor dialog class for a specific recording step type.

        Args:
            step_type (str):
                The identifier of the recording step type.
            editor_class (wx.Dialog):
                The wxPython dialog class used to edit the step payload.

        Returns:
            None
        """
        cls._registry[step_type] = editor_class

    @classmethod
    def create_editor(cls, step_type: RecordingEventType):
        """Return the editor dialog class registered for a step type.

        Args:
            step_type (RecordingEventType):
                The identifier of the recording step type.

        Returns:
            Type[wx.Dialog]:
                The editor dialog class registered for the step type.

        Raises:
            ValueError:
                If no editor has been registered for the specified step type.
        """
        editor_class = cls._registry.get(step_type)

        if not editor_class:
            raise ValueError(f"No editor registered for '{step_type}'")

        return editor_class


def register_step_editors():
    """
    Register all built-in recording step editor dialogs.

    This function imports and registers the editor dialogs associated with
    supported recording step types. Imports are performed inside the function
    to avoid circular import issues and to delay loading editor classes until
    registration is explicitly performed.

    Registered step editors:
        - "dom_click" -> ClickStepEditor
        - "wait" -> WaitStepEditor

    Returns:
        None
    """
    RecordingStepEditorRegistry.register(RecordingEventType.ASSERT,
                                         AssertionStepEditor)
    RecordingStepEditorRegistry.register(RecordingEventType.DOM_CHECK,
                                         CheckStepEditor)
    RecordingStepEditorRegistry.register(RecordingEventType.DOM_CLICK,
                                         ClickStepEditor)
    RecordingStepEditorRegistry.register(RecordingEventType.DOM_GET,
                                         DomGetStepEditor)
    RecordingStepEditorRegistry.register(RecordingEventType.DOM_SELECT,
                                         SelectStepEditor)
    RecordingStepEditorRegistry.register(RecordingEventType.DOM_TYPE,
                                         TypeStepEditor)
    RecordingStepEditorRegistry.register(RecordingEventType.NAV_GOTO,
                                         NavGotoStepEditor)
    RecordingStepEditorRegistry.register(RecordingEventType.REST_API,
                                         RestApiStepEditor)
    RecordingStepEditorRegistry.register(RecordingEventType.SCROLL,
                                         ScrollType)
    RecordingStepEditorRegistry.register(RecordingEventType.SENDKEYS,
                                         SendkeysStepEditor)
    RecordingStepEditorRegistry.register(RecordingEventType.WAIT,
                                         WaitStepEditor)
