from code_generation.base_code_generator import BaseCodeGenerator


class ExampleDebugGenerator(BaseCodeGenerator):
    id = "example-debug"
    name = "Example Debug Generator"
    description = "Outputs a dummy file for testing the plugin system"

    def generate(self, recording_document) -> str:
        return """\
# This is a test generator
{}
# Recording path: {}
 
def test_dummy():
    assert True
""".format(recording_document, recording_document.path)


GENERATOR = ExampleDebugGenerator()
