import datetime
from jinja2 import Environment
from jinja2_simple_tags import StandaloneTag


class DateTag(StandaloneTag):
    tags = {'now'}

    def render(self, format_string='%d-%m-%Y'):
        date = datetime.datetime(2020, 7, 8, 11, 59, 59)
        return date.strftime(format_string)


class HeaderTag(StandaloneTag):
    tags = {'header'}

    def render(self, title='', css_class=''):
        return '<h1 class="{}">{}</h1>'.format(css_class, title)


class TestStringOutput:
    def setup(self):
        self.env = Environment(extensions=[DateTag])

    def test_without_params(self):
        template = self.env.from_string('{% now %}')
        assert template.render({}) == '08-07-2020'

    def test_with_params(self):
        template = self.env.from_string('{% now "%d %B %Y" %}')
        assert template.render({}) == '08 July 2020'

    def test_assignment(self):
        template = self.env.from_string('{% now as today %}')
        assert template.render({}) == ''

        template = self.env.from_string(
            '{% now "%d %B %Y" as today %}'
            'Today: {{ today }}'
        )
        assert template.render({}) == 'Today: 08 July 2020'


class TestHTMLOutput:
    def setup(self):
        self.env = Environment(extensions=[HeaderTag])

    def test_without_params(self):
        template = self.env.from_string('{% header %}')
        assert template.render({}) == '<h1 class=""></h1>'

    def test_with_params(self):
        template = self.env.from_string('{% header "My page", css_class="header blue" %}')
        assert template.render({}) == '<h1 class="header blue">My page</h1>'

    def test_assignment(self):
        template = self.env.from_string('{% header "Blog" as header %}')
        assert template.render({}) == ''

        template = self.env.from_string(
            '{% header "Blog" as header %}'
            '<div>{{ header }}</div>'
        )
        assert template.render({}) == '<div><h1 class="">Blog</h1></div>'
