# Vendored wheelhouse

The CI pipeline expects this directory to contain pre-downloaded wheels that match `requirements/dev.lock`.

Populate it locally with:

```bash
python scripts/fetch_wheels.py
```

The wheels are optional for day-to-day development, but committing them ensures completely offline installs in production environments.
