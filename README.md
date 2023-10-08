# jinja2-simple-tags

`jinja2-simple-tags` is a library that provides a simple way to create custom template 
tags in Jinja2 templates.

[![PyPI](https://img.shields.io/pypi/v/jinja2-simple-tags.svg)](https://pypi.org/project/jinja2-simple-tags/)
[![Build Status](https://travis-ci.com/dldevinc/jinja2-simple-tags.svg?branch=master)](https://travis-ci.org/dldevinc/jinja2-simple-tags)

## Compatibility

-   `python` >= 3.6
-   `Jinja2` >= 2.10

## Installation

`pip install jinja2-simple-tags`

## Usage

To use `jinja2-simple-tags`, you need to create a subclass of one of the provided 
tag types and implement the `render` method.

### `StandaloneTag`

`StandaloneTag` is a tag that doesn't require a closing tag. It can be used like this:

```python
from datetime import datetime
from jinja2_simple_tags import StandaloneTag


class NowExtension(StandaloneTag):
    tags = {"now"}

    def render(self, format="%Y-%m-%d %H:%I:%S"):
        return datetime.now().strftime(format)
```

```jinja2
{% now %}               {# 2023-04-27 20:08:03 #}
{% now '%m/%d/%Y' %}    {# 04/27/2023 #}
```

#### Escaping

By default, the output of `StandaloneTag` will be escaped. To disable escaping,
set the `safe_output` property of your tag to `True`:

```python
from jinja2_simple_tags import StandaloneTag


class AlertExtension(StandaloneTag):
    safe_output = True
    tags = {"alert"}

    def render(self, message):
        return "<script>alert('{}')</script>".format(message)
```

You can also return a `jinja2.Markup` object from the `render()` method to explicitly 
mark the output as safe.

### `ContainerTag`

`ContainerTag` is a tag that requires a closing tag and can contain arbitrary content.
It can be used like this:

```python
import hmac
from jinja2_simple_tags import ContainerTag


class HMACExtension(ContainerTag):
    tags = {"hmac"}

    def render(self, secret, digest="sha256", caller=None):
        content = str(caller()).encode()

        if isinstance(secret, str):
            secret = secret.encode()

        signing = hmac.new(secret, content, digestmod=digest)
        return signing.hexdigest()
```

```jinja2
{% hmac 'SECRET', digest='sha1' %}Hello world!{% endhmac %}

{# e29371e24dc99c5641681728855a92e26829e288 #}
```

### `InclusionTag`

`InclusionTag` is a tag that can be used for including other templates. 
It allows you to specify a template name or implement the `get_template_names()` 
method for dynamic template selection. Here's an example:

```python
from jinja2_simple_tags import InclusionTag

class IncludeHeader(InclusionTag):
    tags = {"include_header"}
    template_name = "header.html"

    def get_context(self, logo):
        return {
            "logo": logo
        }
```

```jinja2
{% include_header logo="/static/logo.png" %}
```

#### Context Inheritance

`InclusionTag` inherits the current context from the parent template, which allows you 
to access and use variables from the parent context within the included template. 
Any additional context variables returned by the `get_context()` method are merged with 
the inherited context.

### Context

Current context can be accessed using `self.context` attribute of the tag class:

```python
from jinja2_simple_tags import StandaloneTag


class UserNameExtension(StandaloneTag):
    tags = {"username"}

    def render(self):
        return self.context["user"].username
```

### Assignment

In addition to returning the rendered value,  `ContainerTag`, `StandaloneTag` and 
`InclusionTag` also supports assigning the output to a variable in the context. 
This can be done using the `as` keyword:

```jinja2
{% now '%m/%d/%Y' as today %}    
...
{{ today }}         {# 04/27/2023 #}
```

```jinja2
{% hmac 'SECRET', digest='sha1' as signature %}Hello world!{% endhmac %}
...
{{ signature }}     {# e29371e24dc99c5641681728855a92e26829e288 #}
```
