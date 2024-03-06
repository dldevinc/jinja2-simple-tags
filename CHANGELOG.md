# Change Log

## [0.6.0](https://github.com/dldevinc/jinja2-simple-tags/tree/v0.6.0) - 2024-03-06

-   Added `InclusionTag` (https://github.com/dldevinc/jinja2-simple-tags/issues/6).
-   Added CI testing against python 3.12.

## [0.5.0](https://github.com/dldevinc/jinja2-simple-tags/tree/v0.5.0) - 2023-04-27

### ⚠ BREAKING CHANGES

-   The output of `StandaloneTag` is now escaped by default when the `autoescape` 
    environment option is set to `True`. This behavior can be changed using the new 
    `safe_output` [property](README.md#Escaping). When `safe_output` is set to `True`, 
    the output will not be escaped.
-   The `BaseTemplateTag.output()` method has been deprecated and is no longer available.
    Use the `BaseTemplateTag.create_node()` method instead.

## [0.4.1](https://github.com/dldevinc/jinja2-simple-tags/tree/v0.4.1) - 2022-11-28

-   Add Python 3.11 support (no code changes were needed, but now we test this release).
-   Support for trailing comma in tag arguments.

## [0.4.0](https://github.com/dldevinc/jinja2-simple-tags/tree/v0.4.0) - 2022-05-28

### ⚠ BREAKING CHANGES

-   Dropped support for Python 3.5

## [0.3.1](https://github.com/dldevinc/jinja2-simple-tags/tree/v0.3.1) - 2021-03-15

-   Add Python 3.5 and Python 3.9 support

## [0.3.0](https://github.com/dldevinc/jinja2-simple-tags/tree/v0.3.0) - 2020-07-14

-   Thread safety issues have been fixed
