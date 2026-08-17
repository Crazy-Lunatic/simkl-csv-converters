# Trakt to Simkl CSV Converter

A lightweight, zero-dependency Python script to convert your Trakt.tv data export into a strictly formatted CSV file ready for direct import into Simkl.

With Trakt's recent move to restrict API access for free users, directly syncing data via API (using tools like `plextraktsync`) has become complicated or entirely broken for many. This script provides an offline, completely free workaround by converting your official Trakt data export into a CSV schema that Simkl natively understands.

## Features
* **Zero Dependencies:** Uses only built-in Python libraries (`json`, `csv`, `glob`). No `pip install` required.
* **Accurate ID Matching:** Extracts `TMDB`, `IMDB`, and `TVDB` IDs from your Trakt data for near-flawless matching on Simkl's end.
* **Fixes the "Watching" Bug:** Automatically hardcodes the `Watchlist` status to `completed` so Simkl doesn't incorrectly tag your entire history as currently watching.
* **Strict Formatting:** Adheres exactly to Simkl's required headers, including the specific `s1e1` format for episodic data.

## Prerequisites
* **Python 3.x** installed on your system.

## Step-by-Step Migration Guide

### Step 1: Export Your Data from Trakt
1. Log into your Trakt account.
2. Navigate to your [Data Settings page](https://app.trakt.tv/settings/data).
3. Click the **"Export now"** button.
4. Wait for the export to build and download the resulting `.zip` file.

### Step 2: Prepare the Script
1. Extract the downloaded Trakt `.zip` file into a new folder.
2. Place the `convert_trakt_to_simkl.py` script from this repository into the **same folder** as your extracted JSON files.

### Step 3: Run the Conversion
Open your terminal or command prompt, navigate to the folder, and run:

```bash
python3 convert_trakt_to_simkl.py
```

The script will scan for all `watched-history-*.json` files and compile them into a new file named `simkl_import.csv`.

### Step 4: Import to Simkl
1. Go to Simkl's [CSV Import Tool](https://simkl.com/apps/import/csv/).
2. Upload the newly generated `simkl_import.csv` file.
3. Review your newly imported data!

## Data Schema Reference
For reference, this script automatically formats your data to match the strict column headers expected by Simkl:

| simkl_id | TVDB_ID | TMDB | IMDB_ID | MAL_ID | Type | Title | Year | LastEpWatched | Watchlist | WatchedDate | Rating | Memo |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| | | 1340138 | tt1340138 | | movie | Terminator Genisys | 2015 | | completed | 2015-08-20 | | |
| | 276562 | | | | tv | Power | 2014 | s2e2 | completed | 2015-08-21 | | |

## Troubleshooting
**Q: I uploaded to Simkl, but it says I am currently watching everything.**
**A:** This happens if the `Watchlist` column is missing or incorrectly formatted. Ensure you are using the latest version of this script, which hardcodes the status to `completed`.

**Q: I need to wipe a bad import from Simkl and try again.**
**A:** You can bulk-delete specific statuses (like "Watching") or wipe your entire history via the [Simkl Account Cleanup tool](https://simkl.com/settings/login/clean-or-delete/).

---
*Authored by [jshields-ca](https://github.com/jshields-ca). Assisted by Gemini Pro.*
