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
from dataclasses import dataclass, field
from webweaver.studio.browser_launch_options import BrowserLaunchOptions


@dataclass(slots=True)
class SolutionCreateWizardData:
    """
    Shared data container for the solution creation wizard.

    This dataclass stores all information collected across the wizard pages
    during the solution creation flow. Each wizard page reads from and writes
    to this object to accumulate the final configuration before the solution
    is created.

    The fields are grouped logically by wizard page:

    - Page 1: Basic solution information (name, directory, creation options)
    - Page 2: Browser selection and launch behaviour
    - Page 3: Detailed browser launch and recording behaviour

    This object is created once at the start of the wizard and is passed to
    each page in sequence.
    """

    # -- PAGE 1 [Basic Info] --
    solution_name: str = ""
    solution_directory: str = ""
    create_solution_dir: bool = True

    # -- PAGE 2 [Select Browser] --
    base_url: str = ""
    browser: str = ""
    launch_browser_automatically: bool = True

    # -- PAGE 3 [Behaviour Page] --
    browser_launch_options: BrowserLaunchOptions = \
        field(default_factory=BrowserLaunchOptions)
