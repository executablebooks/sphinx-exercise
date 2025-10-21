# Copilot Instructions for sphinx-exercise

## General Guidelines

### Code Philosophy
- **Simplicity First**: Pursue simple code with low complexity when making changes
- **Maintainability**: Keep code modular and easy to understand
- **Minimal Dependencies**: Avoid adding unnecessary dependencies

### Documentation Standards
- **Do NOT create summary documents** when making changes
- Instead, **update existing documents** where needed (README.md, docs/, etc.)
- Keep documentation in sync with code changes

### Release Management
- **Review Documentation**: Before making any releases, please review all documentation in `docs/`
- **Update CHANGELOG.md**: Keep the CHANGELOG.md up to date with all significant changes
- **Release Notes**: Maintain detailed release information in `docs/releases/`
- Follow semantic versioning principles

### Release Information Structure
Release documentation should be maintained in `docs/releases/` with the following structure:
- One file per version (e.g., `v0.5.0.md`)
- Link to releases from main documentation
- Include migration guides for breaking changes

## Project-Specific Guidelines

### Internationalization (i18n)
- Translation files are located in `sphinx_exercise/translations/`
- JSON source files: `sphinx_exercise/translations/jsons/`
- Compiled locale files: `sphinx_exercise/translations/locales/`
- Use `_convert.py` to regenerate locale files from JSON sources
- When adding new languages:
  1. Add translations to both `Exercise.json` and `Solution.json`
  2. Run `python sphinx_exercise/translations/_convert.py` to generate `.po` and `.mo` files
  3. Update documentation to mention new language support

### Testing
- All changes should include appropriate tests
- Test files are in `tests/` directory
- Run tests before committing changes
- Maintain test coverage

### Code Structure
- Main extension code: `sphinx_exercise/`
- Directives: `directive.py`
- Transforms: `transforms.py` and `post_transforms.py`
- LaTeX support: `latex.py`
- Node definitions: `nodes.py`

### Documentation
- Main docs: `docs/source/`
- Build docs locally before committing documentation changes
- Ensure all examples work correctly
- Update syntax documentation when adding new features

## Workflow

1. **Before Starting**: Review relevant existing code and documentation
2. **During Development**:
   - Write simple, clear code
   - Update tests as needed
   - Update existing documentation inline
3. **Before Committing**:
   - Run tests
   - Review documentation changes
   - Update CHANGELOG.md if applicable
4. **Before Releasing**:
   - Review all documentation in `docs/`
   - Create release notes in `docs/releases/`
   - Update CHANGELOG.md
   - Verify all tests pass
