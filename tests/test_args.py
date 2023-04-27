import datetime

import pytest
from jinja2 import Environment, TemplateSyntaxError

from jinja2_simple_tags import StandaloneTag


class DateTag(StandaloneTag):
    tags = {"now"}

    def render(self, format_string="%d-%m-%Y", year=2020, month=7, day=8):
        date = datetime.datetime(year, month, day, 12, 0, 0)
        return date.strftime(format_string)


class TestArguments:
    def setup_method(self):
        self.env = Environment(extensions=[DateTag], autoescape=True)

    def test_default_arguments(self):
        template = self.env.from_string("{% now %}")
        assert template.render({}) == "08-07-2020"

    def test_passing_positional_arguments(self):
        template = self.env.from_string("{% now '%d %B %Y', 2008, 4 %}")
        assert template.render({}) == "08 April 2008"

    def test_passing_keyword_arguments(self):
        template = self.env.from_string("{% now format_string='%d %B %Y', year=2008, month=4 %}")
        assert template.render({}) == "08 April 2008"

    def test_passing_mixed_arguments(self):
        template = self.env.from_string("{% now '%d %B %Y', 2012, month=8, day=17 %}")
        assert template.render({}) == "17 August 2012"

    def test_args_after_kwargs(self):
        with pytest.raises(TemplateSyntaxError, match="Invalid argument syntax"):
            template = self.env.from_string("{% now '%d %B %Y', year=2012, 8, 17 %}")
            template.render({})

    def test_missing_comma(self):
        with pytest.raises(TemplateSyntaxError, match="expected token ',', got 'year'"):
            template = self.env.from_string("{% now '%d %B %Y' year=2012 %}")
            template.render({})

    def test_trailing_comma(self):
        template = self.env.from_string("{% now '%d %B %Y', year=2008, month=4, %}")
        assert template.render({}) == "08 April 2008"

    def test_trailing_comma_assignment(self):
        # TODO: it shouldn't throw an exception, probabaly...
        with pytest.raises(TemplateSyntaxError, match="Invalid argument syntax"):
            template = self.env.from_string("{% now '%d %B %Y', year=2008, month=4, as x %}")
            template.render({})
