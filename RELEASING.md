# Releasing Pixel Lab

## Prepare a release

Update the version in `pyproject.toml` and relevant documentation in a pull
request. CI tests Python 3.10 through 3.13, validates the release artifacts,
and checks installation in a clean environment.

## Stage on TestPyPI

Push a `v<package-version>` tag to start the `Stage` workflow. It validates
the tag, runs CI, and stages the release artifacts on GitHub with SHA-256
checksums. It then publishes to TestPyPI using the `test-pypi` environment
and trusted publishing, and verifies installation from TestPyPI in a clean
environment.

## Promote to PyPI

After staging succeeds, manually dispatch the `Release` workflow from the
staged tag itself. It requires a successful `Stage` workflow for the same
commit, including TestPyPI verification. It validates the tag and version,
downloads the staged GitHub Release assets, verifies their checksums, and
publishes those same artifacts to PyPI using the `pypi` environment and
trusted publishing.
