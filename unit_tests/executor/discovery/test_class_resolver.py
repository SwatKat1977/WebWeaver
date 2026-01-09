import unittest
from webweaver.executor.discovery.class_resolver import resolve_class, ClassResolutionError


class DummyClass:
    pass


class TestClassResolver(unittest.TestCase):

    def test_resolve_existing_class(self):
        module_path = __name__
        cls = resolve_class(f"{module_path}.DummyClass")
        self.assertIs(cls, DummyClass)

    def test_invalid_format(self):
        with self.assertRaises(ClassResolutionError):
            resolve_class("NotAValidPath")

    def test_missing_module(self):
        with self.assertRaises(ClassResolutionError):
            resolve_class("test.module.does.not.exist.Class")

    def test_missing_class(self):
        with self.assertRaises(ClassResolutionError):
            resolve_class("unit_tests.executor.discovery.test_class_resolver.NoSuchClass")
