# CELL LEADERS — Bulk Login Toolkit

## Project Summary

- Purpose: A small suite to parse raw exported text contact dumps into clean CSVs and perform bulk form submissions to the Cell Leaders site via Selenium.
- Modes: GUI-driven workflow (`app.py`) and lightweight CLI runner (`main.py` / `parsedata.py`).
- Intended users: automation maintainers and campaign operators who need repeatable, auditable bulk submissions.

## Contents / Key files

- `app.py` — Tkinter GUI front-end that: parses `.txt` -> `.csv`, allows picking a CSV file, and runs a Selenium-based bulk-login loop in a background thread.
- `parsedata.py` — Standalone parser: cleans `large_data.txt` and emits `extracted_contacts.csv`.
- `main.py` — Lightweight CLI automation runner that reads a CSV and performs the same Selenium interactions as the GUI (useful for headless or server automation).
- `*.spec`, `build/` — PyInstaller outputs for packaging into single-file executables.

## Architecture & Behavior (high-level)

- Parsing: Regular-expression driven extraction that isolates an email address, uses preceding text as a name, strips bracketed suffixes, and filters placeholder values.
- Automation: Selenium Chrome WebDriver performs explicit-waited element selection and form submission; the GUI executes this on a background thread to remain responsive.
- Packaging: PyInstaller is used to create distributable EXEs (see Packaging section).

## Getting Started (developer)

Prereqs:

- Python 3.10+ (recommend 3.11)
- Chrome browser compatible with your `chromedriver` version
- `pip` available

Install runtime dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If you don't have `requirements.txt`, install minimal deps:

```powershell
pip install selenium
```

Note: `tkinter` ships with CPython on Windows; no install is normally required.

## Usage

GUI mode (recommended for operators):

```powershell
python app.py
```

Work flow:

1. In the GUI, Step 1: Browse a `.txt` file then click "Convert to CSV". The app writes a `*_extracted.csv` next to the `.txt` file.
2. Step 2: Browse the produced `.csv` (auto-populated after conversion) and start the automation. Adjust delay per-login.

CLI mode (scripting / servers):

1. Generate a CSV via `parsedata.py`:

```powershell
python parsedata.py
```

2. Run automation via `main.py` (edit constants at top for `CSV_FILE_PATH` and `WAIT_TIME_PER_USER`):

```powershell
python main.py
```

## Packaging (PyInstaller)

To build a single-file executable used in `build/` already, a common command is:

```powershell
pyinstaller --onefile --noconsole app.py
```

Notes for packaging:

- Ensure top-level imports required by PyInstaller are present in the entry module (see `app.py` comment).
- Test the built EXE on a clean machine similar to your target environment.

## ChromeDriver and Selenium

- Download the Chromedriver that matches your Chrome version: https://chromedriver.chromium.org/
- Either place `chromedriver.exe` on `PATH` or configure the `Service` with the executable path inside `app.py` / `main.py`.
- Consider using a pinned driver manager (e.g., `webdriver-manager`) for CI automation.

## Security & Operational Considerations

- Rate-limit and politeness: Respect target-site limits; use `WAIT_TIME_PER_USER` to avoid throttling or account lockdowns.
- Data handling: The CSVs contain personal emails; treat them as PII — store encrypted in transit, rotate or remove after use.
- Error handling: Current scripts mostly log exceptions; add retry/backoff and structured logging before deploying at scale.

## Tests & Validation

- Add a small test harness that runs `parsedata` against a fixed sample and asserts output row counts.
- For automation, use a staging target or mock server to validate selectors and success paths.

## Contributing (summary)

See `CONTRIBUTING.md` for code style, commit message guidance, and testing expectations.

## GitHub / Release workflow

- This repository is intentionally small. Recommended workflow:
  - Feature branches: `feature/<short-desc>`
  - PRs with a short description + testing steps
  - Tag releases with semantic tags like `v0.1.0`


