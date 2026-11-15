# Contributing to pybibx

Contributions improve PyBibX bibliometric and scientometric workflows, including provider contracts, graph analysis, quality checks, and reproducible research outputs.

## Before you start

Read the [README](README.md), [project configuration](pyproject.toml), and [quality workflow](.github/workflows/quality.yml). Identify the affected package component and any optional dependency group rather than assuming every integration is installed.

Search existing issues and pull requests to avoid duplicating work. Describe substantial proposals before implementation, and use repository issue or pull request templates when available. Small corrections can go directly into a focused pull request.

For bug reports, include the affected version or commit, environment, minimal reproduction, expected and actual behavior, and sanitized diagnostics. For feature requests, explain the use case and intended outcome.

## Development and validation

Use the Python version declared in `pyproject.toml`. The quality workflow currently uses Python 3.14 and these commands:

```sh
uv sync --group dev
uv run pyright
uv run ty check pybibx/__init__.py
uv run pytest
```

It also runs Ruff checking and formatting with the arguments recorded in the workflow. Preserve those checks and the existing configuration. Record any optional-provider or visualization checks that need additional dependencies.

Use small synthetic or redistributable bibliographic fixtures. Document identifier normalization, missing metadata, deduplication, graph construction, and numerical assumptions. Keep source retrieval, inferred relationships, and verified bibliographic evidence separate. Avoid redistributing licensed database exports or embedding API credentials in notebooks or examples. Explain expected output changes with independently checked examples.

Update affected documentation and examples alongside behavior changes. Add a focused regression case for a bug fix where executable tests are appropriate. Record checks that were not run and the reason.

## Submitting a pull request

Create a focused branch from the current `main` branch and open a pull request back to it. Keep unrelated formatting, refactoring, and dependency changes separate.

Include:

- The problem, proposed change, and resulting behavior.
- Related issues or existing track references.
- Exact validation commands or inspection steps, results, and limitations.
- Compatibility implications and any data or dependency provenance.

Inspect the complete diff before submission. Required automated checks must pass before merge. Follow the existing repository and account policies; this guide does not introduce a second-person approval requirement or relax existing checks.

## Security and sensitive information

Follow the [account security policy](https://github.com/edithatogo/.github/blob/main/SECURITY.md). Report vulnerabilities privately through GitHub's **Report a vulnerability** option if available. Otherwise request a private reporting contact without disclosing the vulnerability publicly. Keep credentials, personal data, and unredacted logs out of commits, issues, and examples.

## Licensing and conduct

Respect the [existing license](LICENSE) and preserve third-party notices. Submit only material you are entitled to contribute, and document unclear permissions before adding third-party content. Follow the [account code of conduct](https://github.com/edithatogo/.github/blob/main/CODE_OF_CONDUCT.md). This guide adds no CLA, mandatory sign-off, or relicensing condition.

## Reference guidance

- [GitHub contributor guidelines](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors)
- [OpenSSF Best Practices criteria](https://www.bestpractices.dev/en/criteria)
