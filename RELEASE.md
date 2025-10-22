# Release Checklist for v1.1.0

This document provides the step-by-step process to release version 1.1.0 of sphinx-exercise.

## Pre-Release Checklist

- [ ] All tests pass locally
- [ ] All tests pass on CI
- [ ] Documentation builds successfully
- [ ] CHANGELOG.md is up to date with release date
- [ ] Version number updated in `sphinx_exercise/__init__.py`
- [ ] Release notes finalized in `docs/source/releases/v1.1.0.md`
- [ ] All PRs for this release are merged

## Version Update

Update the version number in:

1. **`sphinx_exercise/__init__.py`**:
   ```python
   __version__ = "1.1.0"
   ```

2. **`CHANGELOG.md`**:
   - Replace `(TBD)` with the actual release date
   - Change link to point to the release tag

## Release Steps

### 1. Create Release Commit

```bash
# Ensure you're on main branch and up to date
git checkout main
git pull origin main

# Update version in __init__.py
# Update CHANGELOG.md with release date
# Commit changes
git add sphinx_exercise/__init__.py CHANGELOG.md docs/source/releases/v1.1.0.md
git commit -m "Release v1.1.0"
```

### 2. Create Git Tag

```bash
git tag -a v1.1.0 -m "Release version 1.1.0 - Internationalization support"
```

### 3. Push to GitHub

```bash
git push origin main
git push origin v1.1.0
```

### 4. Automated PyPI Publication

After pushing the tag, the GitHub Actions workflow will automatically:
- Run all tests (pre-commit, pytest, docs)
- Build the distribution packages
- Publish to PyPI using the `PYPI_KEY` secret

You can monitor the progress at:
https://github.com/executablebooks/sphinx-exercise/actions

### 5. Create GitHub Release

Once the workflow completes successfully:

1. Go to https://github.com/executablebooks/sphinx-exercise/releases/new
2. Select tag: `v1.1.0`
3. Release title: `v1.1.0 - Internationalization Support`
4. Description: Copy content from `docs/source/releases/v1.1.0.md`
5. Click "Publish release"

### 6. Update Documentation

The documentation should automatically build from the new tag on ReadTheDocs. Verify at:
https://ebp-sphinx-exercise.readthedocs.io/en/latest/

### 7. Post-Release

1. Verify the package is available on PyPI: https://pypi.org/project/sphinx-exercise/
2. Update `docs/source/releases/index.md` to include v1.1.0
3. Create new "Unreleased" section in CHANGELOG.md for future changes
4. Announce release on relevant channels

## Automated Release Process

This project uses GitHub Actions to automatically publish to PyPI when a version tag is pushed:

1. **Triggering**: The workflow is triggered when a tag matching `v*` is pushed
2. **Testing**: All tests (pre-commit, pytest, documentation) must pass
3. **Building**: The workflow builds the distribution packages using `python -m build`
4. **Publishing**: Packages are automatically published to PyPI using the `PYPI_KEY` secret

**Important**: Ensure the `PYPI_KEY` secret is configured in the repository settings with a valid PyPI API token.

The workflow definition can be found in `.github/workflows/ci.yml` under the `publish` job.

## Version Numbering

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality in a backward compatible manner (this release)
- **PATCH** version for backward compatible bug fixes

## Release Highlights for Announcement

**sphinx-exercise v1.1.0** is now available! 🎉

This release adds comprehensive internationalization support:
- ✨ Support for 27 languages including Chinese, Japanese, Korean, Arabic, and Hindi
- 🌍 Automatic language detection from Sphinx configuration
- 📚 Enhanced documentation with i18n examples and contribution guides
- 🛠️ JSON-based translation system for easy community contributions

Install or upgrade: `pip install --upgrade sphinx-exercise`

Full release notes: https://github.com/executablebooks/sphinx-exercise/releases/tag/v1.1.0
