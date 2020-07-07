import hashlib
from django.utils.encoding import force_bytes
from jinja2 import Environment
from jinja2_simple_tags import ContainerTag


class HashTag(ContainerTag):
    tags = {'hash'}

    def render(self, algorithm, caller=None):
        if algorithm not in hashlib.algorithms_available:
            raise ValueError('unknown algorithm: {}'.format(algorithm))

        content = force_bytes(caller())
        hasher = getattr(hashlib, algorithm)()
        hasher.update(content)
        return hasher.hexdigest()


class TestStringOutput:
    def setup(self):
        self.env = Environment(extensions=[HashTag], autoescape=True)

    def test_container(self):
        template = self.env.from_string('{% hash "sha1" %}test content{% endhash %}')
        assert template.render({}) == '1eebdf4fdc9fc7bf283031b93f9aef3338de9052'

    def test_assignment(self):
        template = self.env.from_string('{% hash "md5" as checksum %}test content{% endhash %}')
        assert template.render({}) == ''

        template = self.env.from_string(
            '{% hash "md5" as checksum %}some text data{% endhash %}'
            'Checksum: {{ checksum }}'
        )
        assert template.render({}) == 'Checksum: ae52b7b49419cd2a689e876abc0af73c'
