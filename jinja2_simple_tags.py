from jinja2 import nodes
from jinja2.ext import Extension

__all__ = ['StandaloneTag', 'ContainerTag']
__version__ = '0.3.1'


class BaseTemplateTag(Extension):
    def __init__(self, environment):
        super().__init__(environment)
        self.template = None
        self.lineno = None
        self.tag_name = None

    def parse(self, parser):
        lineno = parser.stream.current.lineno
        tag_name = parser.stream.current.value
        additional_params = [
            nodes.Keyword('_context', nodes.ContextReference()),
            nodes.Keyword('_template', nodes.Const(parser.name)),
            nodes.Keyword('_lineno', nodes.Const(lineno)),
            nodes.Keyword('_tag_name', nodes.Const(tag_name)),
        ]
        self.init_parser(parser)
        args, kwargs, target = self.parse_args(parser)
        kwargs.extend(additional_params)
        block_call = self.call_method('render_wrapper', args, kwargs)
        return self.output(parser, block_call, target, tag_name=tag_name, lineno=lineno)

    def init_parser(self, parser):
        parser.stream.skip(1)  # skip tag name

    def parse_args(self, parser):
        args = []
        kwargs = []
        require_comma = False
        target = None

        while parser.stream.current.type != 'block_end':
            if parser.stream.current.test('name:as'):
                parser.stream.skip(1)
                target = parser.stream.expect('name').value
                if parser.stream.current.type != 'block_end':
                    parser.fail(
                        'Invalid assignment target', parser.stream.current.lineno
                    )
                break

            if require_comma:
                parser.stream.expect('comma')

            if (
                parser.stream.current.type == 'name'
                and parser.stream.look().type == 'assign'
            ):
                key = parser.stream.current.value
                parser.stream.skip(2)
                value = parser.parse_expression()
                kwargs.append(nodes.Keyword(key, value, lineno=value.lineno))
            else:
                if kwargs:
                    parser.fail('Invalid argument syntax', parser.stream.current.lineno)
                args.append(parser.parse_expression())

            require_comma = True

        return args, kwargs, target

    def output(self, parser, block_call, target, tag_name, lineno):
        raise NotImplementedError

    def render_wrapper(self, *args, **kwargs):
        self.context = kwargs.pop('_context', None)
        self.template = kwargs.pop('_template', None)
        self.lineno = kwargs.pop('_lineno', None)
        self.tag_name = kwargs.pop('_tag_name', None)
        return self.render(*args, **kwargs)

    def render(self, *args, **kwargs):
        raise NotImplementedError


class StandaloneTag(BaseTemplateTag):
    def output(self, parser, block_call, target, tag_name, lineno):
        if target:
            target_node = nodes.Name(target, 'store', lineno=lineno)
            return nodes.Assign(target_node, block_call, lineno=lineno)
        call = nodes.MarkSafe(block_call, lineno=lineno)
        return nodes.Output([call], lineno=lineno)


class ContainerTag(BaseTemplateTag):
    def output(self, parser, block_call, target, tag_name, lineno):
        body = parser.parse_statements(['name:end%s' % tag_name], drop_needle=True)
        call_block = nodes.CallBlock(block_call, [], [], body).set_lineno(lineno)
        if target:
            target_node = nodes.Name(target, 'store', lineno=lineno)
            return nodes.AssignBlock(target_node, None, [call_block], lineno=lineno)
        return call_block
