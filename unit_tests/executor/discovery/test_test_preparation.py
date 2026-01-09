import unittest
from unittest.mock import patch

from webweaver.executor.discovery.test_preparation import inject_listeners_into_suite

# Dummy classes to act as resolved test classes


class DummyTestClassA:
    pass


class DummyTestClassB:
    pass


# Dummy listener types

class ListenerOne:
    pass


class ListenerTwo:
    pass


class TestTestPreparation(unittest.TestCase):

    def setUp(self):
        # Clean up any leaked __listeners__ from previous tests
        for cls in (DummyTestClassA, DummyTestClassB):
            if hasattr(cls, "__listeners__"):
                delattr(cls, "__listeners__")

    @patch("webweaver.executor.discovery.test_preparation.resolve_class")
    def test_injects_listeners_into_class(self, mock_resolve_class):
        mock_resolve_class.return_value = DummyTestClassA

        suite = {
            "tests": [
                {
                    "classes": [
                        {"name": "some.module.DummyTestClassA"}
                    ]
                }
            ]
        }

        listeners = [ListenerOne(), ListenerTwo()]

        inject_listeners_into_suite(suite, listeners)

        self.assertTrue(hasattr(DummyTestClassA, "__listeners__"))
        self.assertEqual(len(DummyTestClassA.__listeners__), 2)
        self.assertIsInstance(DummyTestClassA.__listeners__[0], ListenerOne)
        self.assertIsInstance(DummyTestClassA.__listeners__[1], ListenerTwo)

    @patch("webweaver.executor.discovery.test_preparation.resolve_class")
    def test_does_not_duplicate_listener_types(self, mock_resolve_class):
        mock_resolve_class.return_value = DummyTestClassA

        # Pre-seed with one listener
        DummyTestClassA.__listeners__ = [ListenerOne()]

        suite = {
            "tests": [
                {
                    "classes": [
                        {"name": "some.module.DummyTestClassA"}
                    ]
                }
            ]
        }

        listeners = [ListenerOne(), ListenerTwo()]

        inject_listeners_into_suite(suite, listeners)

        # Should only have one ListenerOne and one ListenerTwo
        self.assertEqual(len(DummyTestClassA.__listeners__), 2)

        types = {type(l) for l in DummyTestClassA.__listeners__}
        self.assertEqual(types, {ListenerOne, ListenerTwo})

    @patch("webweaver.executor.discovery.test_preparation.resolve_class")
    def test_multiple_classes(self, mock_resolve_class):
        def resolver(name):
            if "A" in name:
                return DummyTestClassA
            return DummyTestClassB

        mock_resolve_class.side_effect = resolver

        suite = {
            "tests": [
                {
                    "classes": [
                        {"name": "some.module.DummyTestClassA"},
                        {"name": "some.module.DummyTestClassB"},
                    ]
                }
            ]
        }

        listeners = [ListenerOne()]

        inject_listeners_into_suite(suite, listeners)

        self.assertEqual(len(DummyTestClassA.__listeners__), 1)
        self.assertEqual(len(DummyTestClassB.__listeners__), 1)
        self.assertIsInstance(DummyTestClassA.__listeners__[0], ListenerOne)
        self.assertIsInstance(DummyTestClassB.__listeners__[0], ListenerOne)

    @patch("webweaver.executor.discovery.test_preparation.resolve_class")
    def test_resolve_class_called_with_correct_names(self, mock_resolve_class):
        mock_resolve_class.return_value = DummyTestClassA

        suite = {
            "tests": [
                {
                    "classes": [
                        {"name": "a.b.C"},
                        {"name": "d.e.F"},
                    ]
                }
            ]
        }

        inject_listeners_into_suite(suite, [])

        calls = [call.args[0] for call in mock_resolve_class.call_args_list]
        self.assertEqual(calls, ["a.b.C", "d.e.F"])
