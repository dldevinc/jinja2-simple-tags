import datetime

from jinja2 import Environment

from jinja2_simple_tags import StandaloneTag


class NowTag(StandaloneTag):
    tags = {"now"}

    def render(self, format_string="%d-%m-%Y"):
        date = datetime.datetime(2020, 7, 8, 11, 59, 59)
        return date.strftime(format_string)


class TestStandaloneTag:
    def setup_method(self):
        self.env = Environment(extensions=[NowTag])

    def test_output(self):
        template = self.env.from_string("{% now %}")
        assert template.render({}) == "08-07-2020"

    def test_assignment(self):
        template = self.env.from_string("{% now as today %}")
        assert template.render({}) == ""

        template = self.env.from_string(
            "{% now '%d %B %Y' as today %}"
            "Today: {{ today }}"
        )
        assert template.render({}) == "Today: 08 July 2020"
