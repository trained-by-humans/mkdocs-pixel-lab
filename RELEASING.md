# Releasing `mkdocs-pixel-lab`

## Prepare a release

Update the version in `pyproject.toml` and relevant documentation in a pull
request. CI tests Python 3.10 through 3.13, builds and validates distribution
artifacts, and installs the built wheel in a clean environment. Import checks
run in isolated Python mode (`-I`) and verify that the package is loaded from
that environment. A strict MkDocs fixture build checks the installed theme.

## Stage on TestPyPI

Push a `v<package-version>` tag to start the `Stage` workflow. It validates
the tag, runs CI, builds the wheel and source distribution, and uploads them
to a GitHub Release with SHA-256 checksums. It then verifies and publishes
those artifacts to TestPyPI using the `test-pypi` environment and trusted
publishing, and checks installation with an isolated import and strict
MkDocs fixture build. The target wheel is downloaded exclusively from
TestPyPI, then installed locally with runtime dependencies resolved from
PyPI. A missing TestPyPI artifact cannot fall back to a PyPI copy.

## Promote to PyPI

After staging succeeds, manually dispatch the `Release` workflow from the
staged tag itself. It requires a successful `Stage` workflow for the same
commit, including TestPyPI verification. It validates the tag and version,
downloads the staged GitHub Release assets, verifies their checksums, and
publishes those same artifacts to PyPI using the `pypi` environment and
trusted publishing.
