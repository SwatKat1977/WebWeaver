import unittest
from test_suite.normalisation import normalise_classes, normalise_suite


class TestNormaliseClasses(unittest.TestCase):

    def test_empty_input(self):
        self.assertEqual(normalise_classes([]), [])

    def test_single_string_class(self):
        result = normalise_classes(["MyClass"])
        self.assertEqual(result, [
            {
                "name": "MyClass",
                "methods": {"include": [], "exclude": []}
            }
        ])

    def test_single_dict_class_no_methods(self):
        result = normalise_classes([
            {"name": "MyClass"}
        ])
        self.assertEqual(result, [
            {
                "name": "MyClass",
                "methods": {"include": [], "exclude": []}
            }
        ])

    def test_single_dict_class_with_methods_lists(self):
        result = normalise_classes([
            {
                "name": "MyClass",
                "methods": {
                    "include": ["a", "b"],
                    "exclude": ["c"]
                }
            }
        ])
        self.assertEqual(result, [
            {
                "name": "MyClass",
                "methods": {
                    "include": ["a", "b"],
                    "exclude": ["c"]
                }
            }
        ])

    def test_single_dict_class_with_methods_strings(self):
        result = normalise_classes([
            {
                "name": "MyClass",
                "methods": {
                    "include": "a",
                    "exclude": "b"
                }
            }
        ])
        self.assertEqual(result, [
            {
                "name": "MyClass",
                "methods": {
                    "include": ["a"],
                    "exclude": ["b"]
                }
            }
        ])

    def test_merge_same_class_from_string_and_dict(self):
        result = normalise_classes([
            "MyClass",
            {
                "name": "MyClass",
                "methods": {
                    "include": ["a"],
                    "exclude": ["b"]
                }
            }
        ])
        self.assertEqual(result, [
            {
                "name": "MyClass",
                "methods": {
                    "include": ["a"],
                    "exclude": ["b"]
                }
            }
        ])

    def test_merge_multiple_entries_preserve_order(self):
        result = normalise_classes([
            {"name": "A", "methods": {"include": ["a1"], "exclude": []}},
            {"name": "B", "methods": {"include": ["b1"], "exclude": []}},
            {"name": "A", "methods": {"include": ["a2"], "exclude": []}},
        ])

        self.assertEqual(result, [
            {
                "name": "A",
                "methods": {"include": ["a1", "a2"], "exclude": []}
            },
            {
                "name": "B",
                "methods": {"include": ["b1"], "exclude": []}
            },
        ])

    def test_merge_removes_duplicates_preserves_order(self):
        result = normalise_classes([
            {"name": "A", "methods": {"include": ["x", "y"], "exclude": []}},
            {"name": "A", "methods": {"include": ["y", "z"], "exclude": []}},
        ])

        self.assertEqual(result, [
            {
                "name": "A",
                "methods": {"include": ["x", "y", "z"], "exclude": []}
            }
        ])

    def test_include_and_exclude_merge_independently(self):
        result = normalise_classes([
            {"name": "A", "methods": {"include": ["a"], "exclude": ["x"]}},
            {"name": "A", "methods": {"include": ["b"], "exclude": ["y"]}},
        ])

        self.assertEqual(result, [
            {
                "name": "A",
                "methods": {
                    "include": ["a", "b"],
                    "exclude": ["x", "y"]
                }
            }
        ])

    def test_mixed_input_multiple_classes(self):
        result = normalise_classes([
            "A",
            {"name": "B", "methods": {"include": "b1"}},
            {"name": "A", "methods": {"exclude": "a1"}},
            {"name": "B", "methods": {"include": ["b2"], "exclude": ["b3"]}},
        ])

        self.assertEqual(result, [
            {
                "name": "A",
                "methods": {
                    "include": [],
                    "exclude": ["a1"]
                }
            },
            {
                "name": "B",
                "methods": {
                    "include": ["b1", "b2"],
                    "exclude": ["b3"]
                }
            },
        ])


class TestNormaliseSuite(unittest.TestCase):

    def _base_suite(self):
        """
        Returns a minimal valid suite dict structure.
        """
        return {
            "suite": {},
            "tests": [
                {
                    "classes": ["A"],
                }
            ]
        }

    def test_suite_defaults_applied(self):
        data = self._base_suite()

        result = normalise_suite(data, default_suite_threads=10, default_test_threads=5)

        self.assertEqual(result["suite"]["parallel"], "none")
        self.assertEqual(result["suite"]["thread_count"], 10)

    def test_test_inherits_parallel_from_suite(self):
        data = self._base_suite()
        data["suite"]["parallel"] = "methods"

        result = normalise_suite(data, default_suite_threads=10, default_test_threads=5)

        test = result["tests"][0]
        self.assertEqual(test["parallel"], "methods")

    def test_parallel_none_forces_thread_count_to_one(self):
        data = self._base_suite()
        data["suite"]["parallel"] = "none"

        result = normalise_suite(data, default_suite_threads=10, default_test_threads=5)

        test = result["tests"][0]
        self.assertEqual(test["thread_count"], 1)

    def test_parallel_non_none_inherits_suite_thread_count(self):
        data = self._base_suite()
        data["suite"]["parallel"] = "methods"
        data["suite"]["thread_count"] = 7

        result = normalise_suite(data, default_suite_threads=10, default_test_threads=5)

        test = result["tests"][0]
        self.assertEqual(test["thread_count"], 7)

    def test_parallel_non_none_inherits_defaulted_suite_thread_count(self):
        data = self._base_suite()
        data["suite"]["parallel"] = "methods"
        # Note: no suite["thread_count"]

        result = normalise_suite(data, default_suite_threads=10, default_test_threads=5)

        test = result["tests"][0]
        self.assertEqual(test["thread_count"], 10)

    def test_explicit_test_thread_count_is_preserved(self):
        data = self._base_suite()
        data["suite"]["parallel"] = "methods"
        data["tests"][0]["thread_count"] = 42

        result = normalise_suite(data, default_suite_threads=10, default_test_threads=5)

        test = result["tests"][0]
        self.assertEqual(test["thread_count"], 42)

    def test_classes_are_normalised(self):
        data = {
            "suite": {},
            "tests": [
                {
                    "classes": [
                        "A",
                        {"name": "A", "methods": {"include": ["x"]}},
                    ]
                }
            ]
        }

        result = normalise_suite(data, default_suite_threads=10, default_test_threads=5)

        classes = result["tests"][0]["classes"]

        self.assertEqual(classes, [
            {
                "name": "A",
                "methods": {
                    "include": ["x"],
                    "exclude": [],
                }
            }
        ])