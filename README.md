# jinja2-simple-tags
Base classes for quick-and-easy template tag development

[![PyPI](https://img.shields.io/pypi/v/jinja2-simple-tags.svg)](https://pypi.org/project/jinja2-simple-tags/)
[![Build Status](https://travis-ci.com/dldevinc/jinja2-simple-tags.svg?branch=master)](https://travis-ci.org/dldevinc/jinja2-simple-tags)

## Compatibility
* `python` >= 3.5
* `Jinja2` >= 2.10

## Installation
`pip install jinja2-simple-tags`

## Examples

### `StandaloneTag`
```python
from django.utils.timezone import now
from django.utils.formats import date_format
from jinja2_simple_tags import StandaloneTag


class NowExtension(StandaloneTag):
    tags = {"now"}

    def render(self, format_string='DATETIME_FORMAT'):
        return date_format(now(), format_string)
```

Usage:
```jinja2
{% now %}           {# 7th July 2020, 10:07 a.m. #}
{% now "Y-m-d" %}   {# 2020-07-07 #}
```


### `ContainerTag`
```python
from django.core.cache import cache
from django.utils.encoding import force_str
from django.core.cache.utils import make_template_fragment_key
from jinja2_simple_tags import ContainerTag


class CacheExtension(ContainerTag):
    tags = {"cache"}

    def render(self, fragment_name, *vary_on, timeout=None, caller=None):
        cache_key = make_template_fragment_key(fragment_name, vary_on)

        value = cache.get(cache_key)
        if value is None:
            value = caller()
            cache.set(cache_key, force_str(value), timeout)
        else:
            value = force_str(value)

        return value
```

Usage:
```jinja2
{% cache "footer", request.path, timeout=3600 %}
  <footer>
    ...
  </footer>
{% endcache %}
```

### Context
Current context is available through the `self.context`.

```python
from django.urls import reverse
from jinja2_simple_tags import StandaloneTag


class AbsoluteURITag(StandaloneTag):
    tags = {'absolute_uri'}

    def render(self, name):
        request = self.context['request']
        url = reverse(name)
        return request.build_absolute_uri(url)
```

### Assignment
Both `StandaloneTag` and `ContainerTag` comes with out-of-the-box
support for assignment.

Usage:
```jinja2
{% now "Y-m-d" as today %}
...
{{ today }}       {# 2020-07-07 #}
```

```jinja2
{% cache "footer", request.path, timeout=3600 as footer %}
  <footer>
    ...
  </footer>
{% endcache %}
...
{{ footer }}
```
