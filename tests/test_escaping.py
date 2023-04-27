from jinja2 import Environment

from jinja2_simple_tags import ContainerTag, StandaloneTag


class SafeStringTag(StandaloneTag):
    safe_output = True
    tags = {"safe_string"}

    def render(self):
        return "Rick & Morty"


class UnsafeStringTag(StandaloneTag):
    safe_output = False
    tags = {"unsafe_string"}

    def render(self):
        return "Rick & Morty"


class TrimContainer(ContainerTag):
    tags = {"trim"}

    def render(self, caller=None):
        content = caller()
        return str(content).strip()


class TestNoEscape:
    def setup_method(self):
        self.env = Environment(
            extensions=[SafeStringTag, UnsafeStringTag, TrimContainer],
            autoescape=False
        )

    def test_safe_standalone(self):
        template = self.env.from_string("{% safe_string %}")
        assert template.render({}) == "Rick & Morty"

    def test_unsafe_standalone(self):
        template = self.env.from_string("{% unsafe_string %}")
        assert template.render({}) == "Rick & Morty"

    def test_container(self):
        template = self.env.from_string("{% trim %}  \t Rick & Morty\n {% endtrim %}")
        assert template.render({}) == "Rick & Morty"

    def test_safe_standalone_assignment(self):
        template = self.env.from_string("{% safe_string as data %}{{ data }}")
        assert template.render({}) == "Rick & Morty"

    def test_unsafe_standalone_assignment(self):
        template = self.env.from_string("{% unsafe_string as data %}{{ data }}")
        assert template.render({}) == "Rick & Morty"

    def test_container_assignment(self):
        template = self.env.from_string("{% trim as data %}  \t Rick & Morty\n {% endtrim %}{{ data }}")
        assert template.render({}) == "Rick & Morty"


class TestAutoEscape:
    def setup_method(self):
        self.env = Environment(
            extensions=[SafeStringTag, UnsafeStringTag, TrimContainer],
            autoescape=True
        )

    def test_safe_standalone(self):
        template = self.env.from_string("{% safe_string %}")
        assert template.render({}) == "Rick & Morty"

    def test_unsafe_standalone(self):
        template = self.env.from_string("{% unsafe_string %}")
        assert template.render({}) == "Rick &amp; Morty"

    def test_container(self):
        template = self.env.from_string("{% trim %}  \t Rick & Morty\n {% endtrim %}")
        assert template.render({}) == "Rick & Morty"

    def test_safe_standalone_assignment(self):
        template = self.env.from_string("{% safe_string as data %}{{ data }}")
        assert template.render({}) == "Rick & Morty"

    def test_unsafe_standalone_assignment(self):
        template = self.env.from_string("{% unsafe_string as data %}{{ data }}")
        assert template.render({}) == "Rick &amp; Morty"

    def test_container_assignment(self):
        template = self.env.from_string("{% trim as data %}  \t Rick & Morty\n {% endtrim %}{{ data }}")
        assert template.render({}) == "Rick & Morty"
