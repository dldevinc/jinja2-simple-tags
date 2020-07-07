import datetime
from jinja2 import Environment
from jinja2_simple_tags import StandaloneTag


class DateTag(StandaloneTag):
    tags = {'now'}

    def render(self, format_string='%d-%m-%Y', *, year=2020, month=7, day=8):
        date = datetime.datetime(year, month, day, 12, 0, 0)
        return date.strftime(format_string)


class TestArguments:
    def setup(self):
        self.env = Environment(extensions=[DateTag], autoescape=True)

    def test_default_arguments(self):
        template = self.env.from_string('{% now %}')
        assert template.render({}) == '08-07-2020'

    def test_explicit_args(self):
        template = self.env.from_string('{% now "%d %B %Y" %}')
        assert template.render({}) == '08 July 2020'

    def test_explicit_kwargs(self):
        template = self.env.from_string('{% now "%d %B %Y", year=2008, month=4 %}')
        assert template.render({}) == '08 April 2008'
