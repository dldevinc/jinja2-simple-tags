# Contribution

## Development

#### Setup

1. Clone the repository
    ```shell
    git clone https://github.com/dldevinc/jinja2-simple-tags
    ```
1. Create a virtualenv
    ```shell
    cd jinja2-simple-tags
    virtualenv env
    ```
1. Activate virtualenv
    ```shell
    source env/bin/activate
    ```
1. Install dependencies as well as a local editable copy of the library
    ```shell
    pip install -r ./requirements.txt
    pip install -e .
    ```

#### Pre-Commit Hooks

We use [`pre-commit`](https://pre-commit.com/) hooks to simplify linting
and ensure consistent formatting among contributors. Use of `pre-commit`
is not a requirement, but is highly recommended.

```shell
pip install pre-commit
pre-commit install
```

Commiting will now automatically run the local hooks and ensure that
your commit passes all lint checks.

## Testing

To run unit tests:

```shell
pytest
```
