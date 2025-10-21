# Unreleased Changes

This document tracks changes that have been merged but not yet released.

## Internationalization Support

### New Features

`sphinx-exercise` now includes comprehensive internationalization (i18n) support, allowing the extension to display exercise and solution labels in 27 different languages.

#### Supported Languages

The extension now supports the following languages:

- **East Asian**: Chinese, Japanese, Korean
- **South Asian**: Bengali, Hindi, Tamil
- **Middle Eastern**: Arabic, Turkish
- **European**: Czech, Dutch, French, German, Greek, Hungarian, Italian, Norwegian, Polish, Portuguese, Romanian, Russian, Spanish, Swedish, Ukrainian
- **Southeast Asian**: Indonesian, Malay, Vietnamese

#### Automatic Language Detection

The extension automatically detects your Sphinx project's language configuration and applies the appropriate translations. Simply set the `language` option in your `conf.py`:

```python
# For Spanish
language = 'es'

# For Chinese
language = 'zh_CN'

# For Japanese
language = 'ja'
```

For Jupyter Book projects, configure in `_config.yml`:

```yaml
sphinx:
  config:
    language: zh_CN  # For Chinese
```

#### Translation Examples

With language configured, the directive labels automatically translate:

- **Spanish**: "Exercise" → "Ejercicio", "Solution to" → "Solución a"
- **Chinese**: "Exercise" → "练习", "Solution to" → "解答"
- **Japanese**: "Exercise" → "練習", "Solution to" → "解答"
- **French**: "Exercise" → "Exercice", "Solution de" → "Solution de"
- **German**: "Exercise" → "Übung", "Solution to" → "Lösung zu"

### Contributing Translations

We welcome contributions for additional languages or improvements to existing translations. The translation files are maintained in `sphinx_exercise/translations/jsons/` as JSON files for easy editing. See the [translation guide](https://github.com/executablebooks/sphinx-exercise/tree/main/sphinx_exercise/translations) for details.

### Documentation Updates

- Added internationalization section to [syntax guide](../syntax.md#internationalization-i18n)
- Updated README with i18n feature highlights
- Enhanced translation documentation with contribution guidelines

---

For the complete list of changes, see the [CHANGELOG](https://github.com/executablebooks/sphinx-exercise/blob/main/CHANGELOG.md).
