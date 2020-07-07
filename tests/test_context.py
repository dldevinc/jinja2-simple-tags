from jinja2 import Environment
from jinja2_simple_tags import StandaloneTag


class NonContextTag(StandaloneTag):
    tags = {'empty_context'}

    def render(self):
        return self.context is None


class ContextTag(StandaloneTag):
    tags = {'variable'}
    takes_context = True

    def render(self, name):
        return self.context.get(name)


class TestContext:
    def setup(self):
        self.env = Environment(extensions=[NonContextTag, ContextTag])

    def test_unacessible_context(self):
        template = self.env.from_string('{% empty_context %}')
        assert template.render({
            'name': 'John'
        }) == 'True'

    def test_acessible_context(self):
        template = self.env.from_string('{% variable "name" %}')
        assert template.render({
            'name': 'John'
        }) == 'John'

    def test_missing_context_variable(self):
        template = self.env.from_string('{% variable "nothing" %}')
        assert template.render({
            'name': 'John'
        }) == 'None'
