import unittest
from test_suite.normalisation import normalise_classes


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
