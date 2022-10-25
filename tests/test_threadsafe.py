from jinja2 import Environment

from jinja2_simple_tags import StandaloneTag


class LineNoTag(StandaloneTag):
    tags = {'lineno'}

    def render(self):
        return self.lineno


class TestThreadSafe:
    def setup_method(self):
        self.env = Environment(extensions=[LineNoTag], autoescape=True)

    def test_state(self):
        template = self.env.from_string('{% lineno %} \n {% lineno %}')
        assert template.render({}) == '1 \n 2'
