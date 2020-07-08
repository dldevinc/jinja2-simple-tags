from jinja2 import Environment
from jinja2_simple_tags import StandaloneTag


class VariableTag(StandaloneTag):
    tags = {'variable'}

    def render(self, name):
        return self.context.get(name)


class TestContext:
    def setup(self):
        self.env = Environment(extensions=[VariableTag])

    def test_existing_variable(self):
        template = self.env.from_string('{% variable "name" %}')
        assert template.render({
            'name': 'John'
        }) == 'John'

    def test_missing_variable(self):
        template = self.env.from_string('{% variable "nothing" %}')
        assert template.render({
            'name': 'John'
        }) == 'None'
