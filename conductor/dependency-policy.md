# Dependency Policy

## Baseline Install

The baseline PyBibX 6.0 development and CI install is:

```bash
uv sync --group dev
```

This installs the maintained package surface plus development tools. GitHub Actions must continue to use this baseline command.

## Optional Extras

`uv sync --all-extras --group dev` is intentionally not a baseline-safe command on Python 3.14. The legacy optional dependency set currently includes `gensim`, and the `gensim==4.4.0` resolution path failed to build in the Python 3.14 quality workflow during the packaging/tooling foundation work.

Keep all-extras as an explicit local compatibility/probing task only:

```bash
pixi run sync-all-extras
```

Do not promote all-extras into CI until the legacy NLP dependency stack has a verified Python 3.14-compatible resolution.

## Guardrails

- Baseline CI uses `uv sync --group dev`.
- Optional extras remain individually scoped by feature area.
- Legacy NLP extras can fail independently of maintained 6.0 baseline checks.
- Any change that makes all-extras mandatory must include evidence that `gensim` and the rest of the legacy stack build on Python 3.14.
