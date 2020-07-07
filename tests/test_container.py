import hashlib
from django.utils.encoding import force_bytes
from jinja2 import Environment
from jinja2_simple_tags import ContainerTag


class HashTag(ContainerTag):
    tags = {'hash'}

    def render(self, algorithm='md5', caller=None):
        if algorithm not in hashlib.algorithms_available:
            raise ValueError('unknown algorithm: {}'.format(algorithm))

        content = force_bytes(caller())
        hasher = getattr(hashlib, algorithm)()
        hasher.update(content)
        return hasher.hexdigest()


class WrapperTag(ContainerTag):
    tags = {'wrap'}

    def render(self, tag_name='div', caller=None):
        content = caller()
        return '<{0}>{1}</{0}>'.format(tag_name.lower(), content)


class TestStringOutput:
    def setup(self):
        self.env = Environment(extensions=[HashTag])

    def test_without_params(self):
        template = self.env.from_string('{% hash %}test content{% endhash %}')
        assert template.render({}) == '9473fdd0d880a43c21b7778d34872157'

    def test_with_params(self):
        template = self.env.from_string('{% hash "sha1" %}test content{% endhash %}')
        assert template.render({}) == '1eebdf4fdc9fc7bf283031b93f9aef3338de9052'

    def test_assignment(self):
        template = self.env.from_string('{% hash as checksum %}test content{% endhash %}')
        assert template.render({}) == ''

        template = self.env.from_string(
            '{% hash as checksum %}some text data{% endhash %}'
            'Checksum: {{ checksum }}'
        )
        assert template.render({}) == 'Checksum: ae52b7b49419cd2a689e876abc0af73c'


class TestHTMLOutput:
    def setup(self):
        self.env = Environment(extensions=[WrapperTag])

    def test_without_params(self):
        template = self.env.from_string('{% wrap %}<img src="blank.jpg">{% endwrap %}')
        assert template.render({}) == '<div><img src="blank.jpg"></div>'

    def test_with_params(self):
        template = self.env.from_string('{% wrap "p" %}Hello{% endwrap %}')
        assert template.render({}) == '<p>Hello</p>'

    def test_assignment(self):
        template = self.env.from_string('{% wrap "h1" as header %}Blog{% endwrap %}')
        assert template.render({}) == ''

        template = self.env.from_string(
            '{% wrap "h1" as header %}Blog{% endwrap %}'
            '<div>{{ header }}</div>'
        )
        assert template.render({}) == '<div><h1>Blog</h1></div>'
