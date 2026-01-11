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
from enum import Enum


class SolutionCreationPage(Enum):
    """
    Enumeration of pages in the Solution Creation wizard workflow.

    This enum represents the different steps/pages the user navigates through
    when creating a new solution. The numeric values define the order in which
    the pages appear in the wizard.
    """

    #: Page where the user enters basic information about the solution
    PAGE_NO_BASIC_INFO_PAGE = 0

    #: Page where the user selects the browser to use
    PAGE_NO_SELECT_BROWSER_PAGE = 1

    #: Page where the user configures behaviour/settings
    PAGE_NO_BEHAVIOUR_PAGE = 2

    #: Final page of the wizard (summary / finish)
    PAGE_NO_FINISH_PAGE = 3
