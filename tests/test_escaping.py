from django.utils.encoding import force_str
from jinja2 import Environment
from jinja2_simple_tags import StandaloneTag, ContainerTag


class StringTag(StandaloneTag):
    tags = {'string'}

    def render(self):
        return 'Rick & Morty'


class TrimContainer(ContainerTag):
    tags = {'trim'}

    def render(self, caller=None):
        content = caller()
        return force_str(content).strip()


class TestNoEscape:
    def setup(self):
        self.env = Environment(extensions=[StringTag, TrimContainer], autoescape=False)

    def test_standalone(self):
        template = self.env.from_string('{% string %}')
        assert template.render({}) == 'Rick & Morty'

    def test_container(self):
        template = self.env.from_string('{% trim %}  \t Rick & Morty\n {% endtrim %}')
        assert template.render({}) == 'Rick & Morty'


class TestAutoEscape:
    def setup(self):
        self.env = Environment(extensions=[StringTag, TrimContainer], autoescape=True)

    def test_standalone(self):
        template = self.env.from_string('{% string %}')
        assert template.render({}) == 'Rick & Morty'

    def test_container(self):
        template = self.env.from_string('{% trim %}  \t Rick & Morty\n {% endtrim %}')
        assert template.render({}) == 'Rick & Morty'

    def test_standalone_assignment(self):
        template = self.env.from_string('{% string as var %}{{ var }}')
        assert template.render({}) == 'Rick &amp; Morty'

    def test_container_assignment(self):
        template = self.env.from_string('{% trim as data %}  \t Rick & Morty\n {% endtrim %}{{ data }}')
        assert template.render({}) == 'Rick & Morty'
