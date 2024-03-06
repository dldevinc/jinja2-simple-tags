import pytest
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from jinja2_simple_tags import InclusionTag


try:
    from markupsafe import Markup
except ImportError:
    from jinja2 import Markup


try:
    # Jinja2 >= 3.0
    from jinja2 import pass_context as contextfilter
except ImportError:
    # Jinja2 < 3.0
    from jinja2 import contextfilter


@contextfilter
def themed(context, value):
    theme = context["theme"]
    return Markup("<div class=\"theme--{}\">{}</div>".format(theme, value))


class UndefinedTemplateTag(InclusionTag):
    tags = {"include_undefined_template"}

    def get_context(self, *args, **kwargs):
        return {}


class MissingTemplateTag(InclusionTag):
    tags = {"include_missing_template"}
    template_name = "form/missing.hrml"


class InputTag(InclusionTag):
    tags = {"input"}
    template_name = "input/default.html"

    def get_context(self, name, type_="text"):
        return {
            "name": name,
            "type": type_
        }


class ButtonTag(InclusionTag):
    tags = {"button"}
    template_name = (
        "button/christmas.html",
        "button/default.html"
    )

    def get_context(self, text="Click me"):
        return {
            "text": text
        }


class HeaderTag(InclusionTag):
    tags = {"header"}
    template_name = "header/default.html"

    def get_context(self, logo):
        return {
            "logo": logo
        }


class FooterTag(InclusionTag):
    tags = {"footer"}
    template_name = "footer/default.html"

    def get_context(self, theme):
        return {
            "theme": theme
        }


class TestInclusionTag:
    def setup_method(self):
        self.env = Environment(
            loader=FileSystemLoader("tests/templates"),
            extensions=[
                UndefinedTemplateTag,
                MissingTemplateTag,
                InputTag,
                ButtonTag,
                HeaderTag,
                FooterTag
            ],
            autoescape=True
        )
        self.env.filters["themed"] = themed

    def test_undefined_template_exception(self):
        # Tests the case where an undefined template name in an inclusion tag raises an exception.
        template = self.env.from_string("{% include_undefined_template %}")
        with pytest.raises(RuntimeError, match="requires either a definition of 'template_name'"):
            template.render()

    def test_missing_template_exception(self):
        # Tests the case where a missing template file raises a TemplateNotFound exception.
        template = self.env.from_string("{% include_missing_template %}")
        with pytest.raises(TemplateNotFound, match="form/missing.hrml"):
            template.render()

    def test_get_template(self):
        # Tests the rendering of an inclusion tag with arguments.
        template = self.env.from_string("{% input 'password', type_='password' %}")
        assert template.render() == "<input type=\"password\" name=\"password\">"

    def test_select_template(self):
        # Tests the selection of templates when multiple templates are defined.
        template = self.env.from_string("{% button %}")
        assert template.render() == "<button>Click me</button>"

    def test_assignment(self):
        # Tests the assignment of the result of an inclusion tag to a variable.
        template = self.env.from_string(
            "{% button 'Buy now' as buy_button %}"
            "Apple: $1.25 {{ buy_button }}\n"
            "Banana: $2.50 {{ buy_button }}"
        )
        assert template.render() == (
            "Apple: $1.25 <button>Buy now</button>\n"
            "Banana: $2.50 <button>Buy now</button>"
        )

    def test_inherited_variables(self):
        # Tests that variables from the parent context are inherited
        # and affect the rendering of the inclusion tag.
        template = self.env.from_string("{% header '/logo.png' %}")
        assert template.render({
            "theme": "dark"
        }) == (
            "<header class=\"header header--dark\">\n"
            "  <img src=\"/logo.png\" alt=\"\">\n"
            "</header>"
        )

    def test_context_pollution(self):
        # Test that variables set within an inclusion tag do not affect
        # the parent context.
        template = self.env.from_string(
            "Theme: {{ theme }}\n"
            "Logo: {{ logo }}\n"
            "{% header '/weekend.png' %}\n"
            "Theme: {{ theme }}\n"
            "Logo: {{ logo }}"
        )
        assert template.render({
            "theme": "weekend",
            "logo": "/original.png"
        }) == (
            "Theme: weekend\n"
            "Logo: /original.png\n"
            "<header class=\"header header--weekend\">\n"
            "  <img src=\"/weekend.png\" alt=\"\">\n"
            "</header>\n"
            "Theme: weekend\n"
            "Logo: /original.png"
        )

    def test_filter_context_pollution(self):
        # In this test, we check whether the InclusionTag
        # does not pollute the active context.
        template = self.env.from_string(
            "{{ \"Before\"|themed }}\n"
            "{% footer 'christmas' %}\n"
            "{{ \"After\"|themed }}"
        )
        assert template.render({
            "theme": "default"
        }) == (
            "<div class=\"theme--default\">Before</div>\n"
            "<footer class=\"footer footer--christmas\"></footer>\n"
            "<div class=\"theme--default\">After</div>"
        )
