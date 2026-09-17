# Contributing to Putty-ES

Thank you for your interest in making Putty-ES even better!

## How to Contribute

1. **Fork** the repository
2. Create a feature branch (`git checkout -b feature/amazing-module`)
3. Make your changes
4. Add tests if possible
5. Commit with a clear message
6. Push and open a Pull Request

## Creating a New Smart Module

1. Create a new file under `src/putty_es/modules/your_module.py`
2. Subclass `BaseModule`
3. Set `name` and `description`
4. Implement the `apply` method

Example:

```python
from putty_es.modules.base import BaseModule

class MyModule(BaseModule):
    name = "mymodule"
    description = "Does something awesome"

    def apply(self, host, config, executor):
        executor.run(host, "echo 'Hello from my module'")
        return True
```

User modules can also be placed in `~/.putty-es/modules/`.

## Code Style

- Python 3.10+
- Use type hints
- Format with `black`
- Lint with `ruff`

## License

By contributing you agree that your contributions will be licensed under the MIT License.
