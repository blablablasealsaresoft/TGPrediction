# Dependency management

This project now ships a locked dependency set so CI and production hosts install the exact same wheels every time.

## Files

- `base.in` – runtime dependencies used by the bot.
- `dev.in` – developer tooling layered on top of `base.in`.
- `dev.lock` – the fully pinned set that CI installs. The first line points pip at the checked-in `vendor/` wheelhouse so builds remain reproducible even without internet access.

## Installing locally

```bash
./scripts/install_requirements.sh
```

The helper script automatically prefers the vendored wheels under `vendor/` and falls back to PyPI if the directory is empty.

## Updating the lockfile

```bash
pip install pip-tools
pip-compile requirements/dev.in --output-file requirements/dev.lock
python scripts/fetch_wheels.py
```

After compiling, re-run the fetch script so the wheelhouse matches the new pins before committing.
