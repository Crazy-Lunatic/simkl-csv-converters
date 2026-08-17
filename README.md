# Simkl CSV Converters

A lightweight, zero-dependency suite of Python tools designed to convert watch history from **Trakt.tv exports** and local **Tautulli databases** into strictly formatted CSV files ready for direct import into [Simkl](https://simkl.com).

With Trakt's recent move to restrict API access for free users, directly syncing data via API (using tools like `plextraktsync`) has become complicated or entirely broken for many. These offline utilities provide a completely free workaround to ensure your watch history remains 100% portable and private without recurring SaaS costs.

## Included Tools

| Script | Source Data | Description |
| :--- | :--- | :--- |
| **`convert_trakt_to_simkl.py`** | Trakt `.zip` Export (`watched-history-*.json`) | Extracts and formats movie and television watch history from official Trakt JSON archives. |
| **`convert_tautulli_to_simkl.py`** | Tautulli SQLite Database (`tautulli.db`) | Queries local Plex stream logs directly from Tautulli with support for user and date filtering. |

## Features
* **Zero Dependencies:** Uses only built-in Python libraries (`sqlite3`, `json`, `csv`, `glob`, `argparse`). No `pip install` required.
* **Safe Database Access:** The Tautulli script queries the local `tautulli.db` using read-only URI mode (`?mode=ro`) to prevent database locking or corruption while Tautulli is actively running.
* **Accurate ID Matching:** Extracts `TMDB`, `IMDB`, and `TVDB` IDs from Trakt exports for near-flawless matching on Simkl's end.
* **Fixes the "Watching" Bug:** Automatically hardcodes the `Watchlist` status to `completed` so Simkl doesn't incorrectly tag your entire history as currently watching.
* **Strict Formatting:** Adheres exactly to Simkl's required headers, including the specific `s1e1` format for episodic data.

## ⚠️ Known Deficiencies & Limitations
* **Simkl Title Matching Bug:** Simkl's CSV importer has a known bug where it shifts column data (putting titles in the `year` column) if it cannot parse an ambiguous TV show title. The Tautulli script mitigates this by stripping `(YYYY)` tags via Regex and injecting hardcoded `TVDB_ID`s for known problematic shows (like *Law & Order* or *The Pitt*). However, brand-new or highly ambiguous titles not in the script's `ID_MAP` may still fail to import.
* **Tautulli Historical Limit:** The Tautulli extraction script can only export data that Tautulli itself has logged. If you watched media on Plex prior to installing Tautulli, that history will not be in the database.
* **Trakt Manual Export:** The Trakt script relies on a manual ZIP download, meaning it is not a real-time sync replacement, but rather a one-time migration tool.

## Prerequisites
* **Python 3.8+** installed on your system.

---

## Usage Guide

### Method 1: Exporting from Trakt.tv

1. Log into your Trakt account and navigate to [Data Settings](https://app.trakt.tv/settings/data).
2. Click **"Export now"** and download the resulting `.zip` file.
3. Extract the archive into a directory alongside **`convert_trakt_to_simkl.py`**.
4. Run the conversion:
   ```bash
   python3 convert_trakt_to_simkl.py
   ```
5. The script parses all `watched-history-*.json` files and outputs **`simkl_import.csv`**.

### Method 2: Exporting from Tautulli (`tautulli.db`)

You can extract your full watch history or filter by specific usernames and date ranges.

**1. Standard Full Export**
```bash
python3 convert_tautulli_to_simkl.py --db /path/to/tautulli.db -o simkl_tautulli_import.csv
```

**2. Filter by Plex Username**
```bash
python3 convert_tautulli_to_simkl.py --db /path/to/tautulli.db --user "your_username" -o simkl_user_history.csv
```

**3. Filter Date Gaps (e.g., records on or after a specific date)**
```bash
python3 convert_tautulli_to_simkl.py --db /path/to/tautulli.db --user "your_username" --since 2026-07-28 -o simkl_gap_import.csv
```

**CLI Options Reference**
* `--db`: Path to `tautulli.db` *(default: auto-detects standard Docker mounts or current directory)*.
* `--output`, `-o`: Output CSV filename *(default: `simkl_tautulli_import.csv`)*.
* `--user`, `-u`: Filter by Plex username *(default: exports all users)*.
* `--since`, `-s`: Filter events on or after date formatted as `YYYY-MM-DD`.

---

## Importing to Simkl
1. Go to Simkl's [CSV Import Tool](https://simkl.com/apps/import/csv/).
2. Upload your generated `.csv` file.
3. *Important:* If you are importing a gap or merging multiple files, select **"Add missing watches"** to prevent duplicate entries.

## Data Schema Reference
For reference, these scripts automatically format your data to match the strict column headers expected by Simkl:

| simkl_id | TVDB_ID | TMDB | IMDB_ID | MAL_ID | Type | Title | Year | LastEpWatched | Watchlist | WatchedDate | Rating | Memo |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| | | 1340138 | tt1340138 | | movie | Terminator Genisys | 2015 | | completed | 2015-08-20 | | |
| | 276562 | | | | tv | Power | 2014 | s2e2 | completed | 2015-08-21 | | |

## Troubleshooting
**Q: I need to wipe a bad import from Simkl and try again.**
**A:** You can bulk-delete specific statuses (like "Watching") or wipe your entire history without deleting your account via the [Simkl Account Cleanup tool](https://simkl.com/settings/login/clean-or-delete/).

---
*Authored by [jshields-ca](https://github.com/jshields-ca). Assisted by Gemini Pro.*
