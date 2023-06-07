import warnings
from typing import Any, ClassVar, Dict, List, Tuple

from jinja2 import nodes
from jinja2.ext import Extension
from jinja2.lexer import describe_token
from jinja2.parser import Parser
from jinja2.runtime import Context

__all__ = ["StandaloneTag", "ContainerTag"]
__version__ = "0.5.0"


class BaseTemplateTag(Extension):
    def __init__(self, environment):
        super().__init__(environment)
        self.context = None
        self.template = None
        self.lineno = None
        self.tag_name = None

    def parse(self, parser: Parser) -> nodes.Node:
        lineno = parser.stream.current.lineno
        tag_name = parser.stream.current.value
        additional_params = [
            nodes.Keyword("_context", nodes.ContextReference()),
            nodes.Keyword("_template", nodes.Const(parser.name)),
            nodes.Keyword("_lineno", nodes.Const(lineno)),
            nodes.Keyword("_tag_name", nodes.Const(tag_name)),
        ]

        self.init_parser(parser)
        args, kwargs, options = self.parse_args(parser)
        kwargs.extend(additional_params)
        options.setdefault("tag_name", tag_name)

        if hasattr(self, "output") and callable(self.output):
            warnings.warn(
                "The \"output\" method of the \"BaseTemplateTag\" class is deprecated "
                "and will be removed in a future version. Please use the \"create_node\" "
                "method instead.",
                DeprecationWarning
            )
            call_node = self.call_method("render_wrapper", args, kwargs, lineno=lineno)
            return self.output(parser, call_node, lineno=lineno, **options)

        return self.create_node(
            parser,
            args,
            kwargs,
            lineno=lineno,
            **options
        )

    def init_parser(self, parser: Parser):
        parser.stream.skip(1)  # skip tag name

    def parse_args(
        self,
        parser: Parser
    ) -> Tuple[List[nodes.Expr], List[nodes.Keyword], Dict[str, Any]]:
        args = []
        kwargs = []
        options = {
            "target": None
        }
        require_comma = False
        arguments_finished = False

        while parser.stream.current.type != "block_end":
            if parser.stream.current.test("name:as"):
                parser.stream.skip(1)
                options["target"] = parser.stream.expect("name").value
                arguments_finished = True

            if arguments_finished:
                if not parser.stream.current.test("block_end"):
                    parser.fail(
                        "expected token 'block_end', got {!r}".format(
                            describe_token(parser.stream.current)
                        ),
                        parser.stream.current.lineno
                    )
                break

            if require_comma:
                parser.stream.expect("comma")

                # support for trailing comma
                if parser.stream.current.type == "block_end":
                    break

            if (
                parser.stream.current.type == "name"
                and parser.stream.look().type == "assign"
            ):
                key = parser.stream.current.value
                parser.stream.skip(2)
                value = parser.parse_expression()
                kwargs.append(nodes.Keyword(key, value, lineno=value.lineno))
            else:
                if kwargs:
                    parser.fail("Invalid argument syntax", parser.stream.current.lineno)
                args.append(parser.parse_expression())

            require_comma = True

        return args, kwargs, options

    def create_node(
        self,
        parser: Parser,
        args: List[nodes.Expr],
        kwargs: List[nodes.Keyword],
        *,
        lineno: int,
        **options
    ) -> nodes.Node:
        raise NotImplementedError


class StandaloneTag(BaseTemplateTag):
    safe_output: ClassVar[bool] = False

    def create_node(
        self,
        parser: Parser,
        args: List[nodes.Expr],
        kwargs: List[nodes.Keyword],
        *,
        lineno: int,
        **options
    ) -> nodes.Node:
        call_node = self.call_method("render_wrapper", args, kwargs, lineno=lineno)
        if self.safe_output:
            call_node = nodes.MarkSafeIfAutoescape(call_node, lineno=lineno)

        if options["target"]:
            target_node = nodes.Name(options["target"], "store", lineno=lineno)
            return nodes.Assign(target_node, call_node, lineno=lineno)

        return nodes.Output([call_node], lineno=lineno)

    def render_wrapper(self, *args, **kwargs):
        self.context: Context = kwargs.pop("_context")
        self.template: str = kwargs.pop("_template")
        self.lineno: int = kwargs.pop("_lineno")
        self.tag_name: str = kwargs.pop("_tag_name")
        return self.render(*args, **kwargs)

    def render(self, *args, **kwargs):
        raise NotImplementedError


class ContainerTag(BaseTemplateTag):
    def create_node(
        self,
        parser: Parser,
        args: List[nodes.Expr],
        kwargs: List[nodes.Keyword],
        *,
        lineno: int,
        **options
    ) -> nodes.Node:
        call_node = self.call_method("render_wrapper", args, kwargs, lineno=lineno)
        body = parser.parse_statements(("name:end%s" % options["tag_name"],), drop_needle=True)
        call_block = nodes.CallBlock(call_node, [], [], body).set_lineno(lineno)
        if options["target"]:
            target_node = nodes.Name(options["target"], "store", lineno=lineno)
            return nodes.AssignBlock(target_node, None, [call_block], lineno=lineno)
        return call_block

    def render_wrapper(self, *args, **kwargs):
        self.context: Context = kwargs.pop("_context")
        self.template: str = kwargs.pop("_template")
        self.lineno: int = kwargs.pop("_lineno")
        self.tag_name: str = kwargs.pop("_tag_name")
        return self.render(*args, **kwargs)

    def render(self, *args, **kwargs):
        raise NotImplementedError
