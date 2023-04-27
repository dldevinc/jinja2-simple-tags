import hashlib

from jinja2 import Environment

from jinja2_simple_tags import ContainerTag


class HashTag(ContainerTag):
    tags = {"hash"}

    def render(self, algorithm, caller=None):
        content = str(caller()).encode()
        hasher = hashlib.new(algorithm, content)
        return hasher.hexdigest()


class TestContainerTag:
    def setup_method(self):
        self.env = Environment(extensions=[HashTag])

    def test_output(self):
        template = self.env.from_string("{% hash 'sha1' %}test content{% endhash %}")
        assert template.render({}) == "1eebdf4fdc9fc7bf283031b93f9aef3338de9052"

    def test_assignment(self):
        template = self.env.from_string("{% hash 'md5' as checksum %}test content{% endhash %}")
        assert template.render({}) == ""

        template = self.env.from_string(
            "{% hash 'md5' as checksum %}some text data{% endhash %}"
            "Checksum: {{ checksum }}"
        )
        assert template.render({}) == "Checksum: ae52b7b49419cd2a689e876abc0af73c"
