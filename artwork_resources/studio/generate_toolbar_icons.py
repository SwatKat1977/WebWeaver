"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025-2026 SwatKat1977

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
from png_to_header import png_to_header

png_to_header("toolbar/inspect-button.png",
              "toolbar/toolbar_inspect.py",
              "inspect_icon")

png_to_header("toolbar/new-project-button.png",
              "toolbar/toolbar_new_project.py",
              "new_project_icon")

png_to_header("toolbar/open-button.png",
              "toolbar/toolbar_open_project.py",
              "open_project_icon")

png_to_header("toolbar/pause-button.png",
              "toolbar/toolbar_pause_record.py",
              "pause_record_icon")

png_to_header("toolbar/rec-button.png",
              "toolbar/toolbar_start_record.py",
              "start_record_icon")

png_to_header("toolbar/save-button.png",
              "toolbar/toolbar_save_project.py",
              "save_project_icon")

png_to_header("toolbar/stop-button.png",
              "toolbar/toolbar_stop_record.py",
              "stop_record_icon")

png_to_header("toolbar/resume-button.png",
              "toolbar/toolbar_resume_record.py",
              "resume_record_icon")

png_to_header("toolbar/close-button.png",
              "toolbar/toolbar_close_solution.py",
              "close_solution_icon")

png_to_header("toolbar/browser-button.png",
              "toolbar/toolbar_browser_button.py",
              "browser_button_icon")

png_to_header("toolbar/play-button.png",
              "toolbar/toolbar_play_button.py",
              "play_button_icon")
