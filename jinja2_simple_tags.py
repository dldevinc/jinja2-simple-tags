from jinja2 import nodes
from jinja2.ext import Extension

__all__ = ['ContainerTag', 'StandaloneTag']


class BaseTemplateTag(Extension):
    def __init__(self, environment):
        super().__init__(environment)
        self.template = None
        self.lineno = None
        self.tag_name = None

    def parse(self, parser):
        self.init_parser(parser)
        args, kwargs, target = self.parse_args(parser)
        block_call = self.call_method('render', args, kwargs)
        return self.output(parser, block_call, target)

    def init_parser(self, parser):
        self.template = parser.name
        self.lineno = parser.stream.current.lineno
        self.tag_name = parser.stream.current.value
        parser.stream.skip(1)     # skip tag name

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
                        'Invalid assignment target',
                        parser.stream.current.lineno
                    )
                break

            if require_comma:
                parser.stream.expect('comma')

            if parser.stream.current.type == 'name' and parser.stream.look().type == 'assign':
                key = parser.stream.current.value
                parser.stream.skip(2)
                value = parser.parse_expression()
                kwargs.append(nodes.Keyword(key, value, lineno=value.lineno))
            else:
                if kwargs:
                    parser.fail(
                        'Invalid argument syntax',
                        parser.stream.current.lineno
                    )
                args.append(parser.parse_expression())

            require_comma = True

        return args, kwargs, target

    def output(self, parser, block_call, target):
        raise NotImplementedError

    def render(self, *args, **kwargs):
        raise NotImplementedError


class StandaloneTag(BaseTemplateTag):
    def output(self, parser, block_call, target):
        if target:
            target_node = nodes.Name(target, 'store', lineno=self.lineno)
            return nodes.Assign(target_node, block_call, lineno=self.lineno)
        call = nodes.MarkSafe(block_call, lineno=self.lineno)
        return nodes.Output([call], lineno=self.lineno)


class ContainerTag(BaseTemplateTag):
    def output(self, parser, block_call, target):
        body = parser.parse_statements(['name:end%s' % self.tag_name], drop_needle=True)
        call_block = nodes.CallBlock(block_call, [], [], body).set_lineno(self.lineno)
        if target:
            filter_node = parser.parse_filter(None)
            target_node = nodes.Name(target, 'store', lineno=self.lineno)
            return nodes.AssignBlock(target_node, filter_node, [call_block], lineno=self.lineno)
        return call_block
