# Changelog

## [v1.1.0](https://github.com/executablebooks/sphinx-exercise/tree/v1.1.0) (2025-10-22)

### New ✨

- Added internationalization (i18n) support for 27 languages
- Added translations for Chinese, Japanese, Korean, Arabic, Hindi, Turkish, and expanded existing language support
- Extension now automatically detects Sphinx project language setting and displays appropriate translations

### Improved 👌

- **Updated test suite for Python 3.11-3.13 and Sphinx 6-8 compatibility** ([#79](https://github.com/executablebooks/sphinx-exercise/pull/79))
- **Migrated from os.path to pathlib.Path throughout codebase for modern Python best practices**
- Reorganized and expanded translation files with alphabetical sorting
- Enhanced translation documentation with comprehensive guides
- Updated README and documentation to highlight internationalization features
- Fixed README badges to reference main branch instead of master

### Documentation 📚

- Added internationalization section to syntax documentation
- Updated README with i18n feature highlights
- Improved translation README with detailed contribution guidelines
- Created releases documentation structure in `docs/releases/`
- Added Copilot instructions for project maintenance

### Testing Infrastructure 🧪

- Added support for Python 3.11, 3.12, and 3.13
- Added support for Sphinx 6, 7, and 8
- Full test matrix: 9 combinations (3 Python versions × 3 Sphinx versions)
- All 110 tests passing across all supported versions
- Regenerated test fixtures for Sphinx 6 and 7 compatibility
- Normalized image hashes for cross-platform test stability


## [v1.0.1](https://github.com/executablebooks/sphinx-exercise/tree/v1.0.1) (2024-XX-XX)

_No changelog available for this version._

## [v1.0.1](https://github.com/executablebooks/sphinx-exercise/tree/v1.0.1) (2024-07-01)

### Improved 👌

- Updates to testing infrastructure and minor bug fixes
- Fixed JupyterBuilder handling in test suite

## [v1.0.0](https://github.com/executablebooks/sphinx-exercise/tree/v1.0.0) (2024-01-15)

### Improved 👌

- Added support for Sphinx 7
- Updated build and CI infrastructure
- Fixed deprecation warnings for Sphinx 7 compatibility
- Improved type hints throughout codebase
- Fixed doctree node mutation issues by copying nodes
- Updated codecov to version 3
- Pinned matplotlib to 3.7.* for testing stability

## [v0.4.1](https://github.com/executablebooks/sphinx-exercise/tree/v0.4.1) (2023-1-23)

### Improved 👌

Compatibility with docutils>=0.18 (from support with sphinx>=5). Along with updating
CI and pre-commit files.

## [v0.4.0](https://github.com/executablebooks/sphinx-exercise/tree/v0.4.0) (2022-3-18)

### New ✨

Added gated directive syntax for `exercise` and `solution` directives, which provides
an alternative syntax for building `exercise` and `solution` that may also include
executable code.

**Example:**

You may now use `exercise-start` and `exercise-end` to define the exercise which may
include any type of text, directives and roles between the start and end markers.

````md
```{exercise-start}
:label: ex1
```

```{code-cell}
# Some setup code that needs executing
```

and maybe you wish to add a figure

```{figure} img/example.png
```

```{exercise-end}
```
````

This can also be used with `solution-start` and `solution-end`.

See [docs](https://ebp-sphinx-exercise.readthedocs.io/en/latest/syntax.html#alternative-gated-syntax) for further details


## [v0.3.1](https://github.com/executablebooks/sphinx-exercise/tree/v0.3.1) (2022-2-01)

### Fixes 🐛

- 🐛 FIX: Check for sphinx_exercise_registry in all registered post_tranform
- 🐛 FIX: Update style for solution titles

## [v0.3.0](https://github.com/executablebooks/sphinx-exercise/tree/v0.3.0) (2021-12-07)

### Improved 👌

This is a **major release** as the package was extensively refactored to improve maintainability.
There are very few user facing changes. The styles have been updated when
including a custom title to exercise admonitions.

Further details of the technical changes [can be found here](https://github.com/executablebooks/sphinx-exercise/pull/37#issue-1038116091)


## [v0.2.1](https://github.com/executablebooks/sphinx-exercise/tree/v0.2.1) (2021-10-08)

### New ✨

Added latex support for sphinx-exercise

### Improved 👌

Refactored code to make it modular and robust, fixing some of the bugs mentioned below.

### Fixes 🐛

- Exercise node title now visible for sphinx > 3.2
- Solution directive fix issue#32

## [v0.1.1](https://github.com/executablebooks/sphinx-exercise/tree/v0.1.1) (2020-10-10)

[Full Changelog](https://github.com/executablebooks/sphinx-exercise/compare/v0.1.0...v0.1.1)

### Improved 👌

Made bottom and top padding of directives the same as admonitions in order to fix any other padding issues when the directives use the dropdown class option. We also updated the link of the solution directive title to target only the exercise portion in order to avoid confusion.

### Fixes 🐛

Fixed `doctree-resolve` method in the event the extension is imported but not used.

### Documentation improvements 📚

Introduced documentation on how to hide directives.

**Implemented enhancements:**

- Make bottom/top padding the same as admonitions [\#10](https://github.com/executablebooks/sphinx-exercise/issues/10)

**Closed issues:**

- \[ENH\] Add solution block with linking to an exercise [\#19](https://github.com/executablebooks/sphinx-exercise/issues/19)

**Merged pull requests:**

- 👌 IMPROVE: Link exercise portion of solution title in directive [\#20](https://github.com/executablebooks/sphinx-exercise/pull/20) ([najuzilu](https://github.com/najuzilu))
- 🚀 RELEASE: v0.1.0 [\#17](https://github.com/executablebooks/sphinx-exercise/pull/17) ([najuzilu](https://github.com/najuzilu))
- 🐛 FIX: Check during doctree-resolve if env has attribute [\#16](https://github.com/executablebooks/sphinx-exercise/pull/16) ([najuzilu](https://github.com/najuzilu))
- 👌 IMPROVE: Make padding the same as admonitions [\#15](https://github.com/executablebooks/sphinx-exercise/pull/15) ([najuzilu](https://github.com/najuzilu))

## [v0.1.0](https://github.com/executablebooks/sphinx-exercise/tree/v0.1.0) (2020-10-08)

[Full Changelog](https://github.com/executablebooks/sphinx-exercise/compare/8dd98b62aab873e660c8b09dcb88e22c082b1368...v0.1.0)

### New ✨

`sphinx-exercise` incorporates GitHub Actions to build, test, and deploy our code.

### Improved 👌

Reference placeholders such as _{name}_ and _{number}_ can be used simultaneously while _%s_ works only if not referenced with other placeholders.

### Fixes 🐛

- Manifest path has been fixed to recursively include all CSS and JavaScript files.
- Namespace was removed from `setup.py`.
- ReadTheDocs builds documentation using a dev mode environment through the `rtd` extra.

### Documentation improvements 📚

- Typo fix #14 (@chrisjsewell)


**Closed issues:**

- \[DISC\] Create a new role specific to this extension [\#3](https://github.com/executablebooks/sphinx-exercise/issues/3)
- EBP org? [\#1](https://github.com/executablebooks/sphinx-exercise/issues/1)

**Merged pull requests:**

- 📚 typo [\#14](https://github.com/executablebooks/sphinx-exercise/pull/14) ([chrisjsewell](https://github.com/chrisjsewell))
- 🐛 FIX: Manifest recursive-include path [\#8](https://github.com/executablebooks/sphinx-exercise/pull/8) ([najuzilu](https://github.com/najuzilu))
- 🐛 FIX: Remove namespace from setup.py [\#7](https://github.com/executablebooks/sphinx-exercise/pull/7) ([najuzilu](https://github.com/najuzilu))
- 🐛 FIX: RTD fail - install extension locally [\#6](https://github.com/executablebooks/sphinx-exercise/pull/6) ([najuzilu](https://github.com/najuzilu))
- 👌 IMPROVE: Support numref placeholders [\#5](https://github.com/executablebooks/sphinx-exercise/pull/5) ([najuzilu](https://github.com/najuzilu))
- ✨ NEW: Implement Github workflow [\#4](https://github.com/executablebooks/sphinx-exercise/pull/4) ([najuzilu](https://github.com/najuzilu))



\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
