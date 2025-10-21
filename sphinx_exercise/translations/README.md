# Translations for sphinx-exercise

This directory contains internationalization (i18n) files for `sphinx-exercise`.

## Structure

- `jsons/` - Source translation files in JSON format
  - `Exercise.json` - Translations for "Exercise" label
  - `Solution.json` - Translations for "Solution to" label
- `locales/` - Compiled locale files (`.po` and `.mo` files)
- `_convert.py` - Script to generate locale files from JSON sources

## Supported Languages

Currently supporting 27 languages:

Arabic (ar), Bengali (bn), Chinese (zh_CN), Czech (cs), Dutch (nl), French (fr), German (de), Greek (el), Hindi (hi), Hungarian (hu), Indonesian (id), Italian (it), Japanese (ja), Korean (ko), Malay (ms), Norwegian (no), Polish (pl), Portuguese (pt), Romanian (ro), Russian (ru), Spanish (es), Swedish (sv), Tamil (ta), Turkish (tr), Ukrainian (uk), Vietnamese (vi)

## Adding or Updating Translations

To add a new language or update existing translations:

1. Edit the JSON files in `jsons/` directory
   - Add translations to both `Exercise.json` and `Solution.json`
   - Ensure the language symbol follows ISO 639-1 standard (or locale codes like `zh_CN`)
   - Keep entries alphabetically sorted by language name

2. Run the conversion script to generate `.po` and `.mo` files:
   ```bash
   python _convert.py
   ```

3. The script will:
   - Remove existing `.po` files
   - Generate new `.po` files from JSON sources
   - Compile `.mo` files using `msgfmt`

## Requirements

The `msgfmt` utility (from gettext) must be installed on your system to compile `.mo` files.

## Contributing

Contributions for new languages or improvements to existing translations are welcome! Please ensure:
- Translations are accurate and culturally appropriate
- Both `Exercise.json` and `Solution.json` are updated
- The conversion script runs successfully
- Documentation is updated to list the new language
