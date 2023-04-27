from jinja2 import Environment, FileSystemLoader

from jinja2_simple_tags import ContainerTag, StandaloneTag


class InfoTag(StandaloneTag):
    tags = {"info", "stats"}

    def render(self):
        return "{}:{} - {}".format(
            self.template,
            self.lineno,
            self.tag_name
        )


class InfoContainerTag(ContainerTag):
    tags = {"info_container", "stats_container"}

    def render(self, caller=None):
        return "{}:{} - {}".format(
            self.template,
            self.lineno,
            self.tag_name
        )


class TestTagProperties:
    def setup_method(self):
        self.env = Environment(
            loader=FileSystemLoader("tests/templates"),
            extensions=[InfoTag, InfoContainerTag]
        )

    def test_standalone_properties(self):
        template = self.env.from_string(
            "\n"
            "{% info %} \n"
            " \n"
            "{% stats %}"
        )
        assert template.render({}) == (
            "\n"
            "None:2 - info \n"
            " \n"
            "None:4 - stats"
        )

    def test_container_properties(self):
        template = self.env.from_string(
            "\n"
            "{% stats_container %}\n"
            "Hello, world!\n"
            "{% endstats_container %}\n"
            "\n"
            "{% info_container %}\n"
            "Goodbye\n"
            "{% endinfo_container %}"
        )
        assert template.render({}) == (
            "\n"
            "None:2 - stats_container\n"
            "\n"
            "None:6 - info_container"
        )

    def test_file_template(self):
        template = self.env.get_template("test_properties.html")
        assert template.render({}) == (
            "<ul>\n"
            "  <li>test_properties.html:2 - info</li>\n"
            "  <li>test_properties.html:3 - info</li>\n"
            "</ul>"
        )
