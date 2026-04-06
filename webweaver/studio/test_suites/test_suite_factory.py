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
from webweaver.studio.persistence.test_suite_document import TestSuiteDocument
# from webweaver.studio.recording.recording import Recording
from webweaver.studio.studio_solution import StudioSolution
from webweaver.studio.test_suites.test_suite import TestSuite


class TestSuiteFactory:
    """Factory class for creating TestSuite instances from persisted documents.

    This class provides utility methods to construct TestSuite objects from
    serialized or stored representations, such as TestSuiteDocument instances.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def from_document(suite_document: TestSuiteDocument,
                      _solution: StudioSolution) -> TestSuite:
        """Create a TestSuite instance from a TestSuiteDocument.

        This method extracts relevant data from the provided document and
        constructs a corresponding TestSuite object. It resolves associated
        recordings using identifiers stored in the document.

        Args:
            suite_document (TestSuiteDocument): The document containing the
                serialized test suite data.
            solution (StudioSolution): The solution context used to locate and
                load associated recordings.

        Returns:
            TestSuite: A constructed TestSuite instance populated with the
                name and associated recordings.

        Notes:
            Recording loading is currently not implemented. The method iterates
            through recording identifiers and is expected to resolve them into
            Recording instances in a future implementation.
        """
        data = suite_document.data

        name = data.get("name", "Untitled Suite")
        recording_ids = data.get("recordings", [])

        recordings = []

        for recording_id in recording_ids:
            print(f"REC: {recording_id}")
            # however you currently load recordings
            #recording = Recording.load(path)
            #recordings.append(recording)

        return TestSuite(name, recordings)
