#!/usr/bin/env python3
"""
Tautulli to Simkl CSV Converter
Authored by jshields-ca (assisted by Gemini Pro)

Extracts watch history from a local Tautulli SQLite database (tautulli.db)
and converts it into a CSV schema ready for direct import into Simkl.
"""

import argparse
import csv
import datetime
import os
import sqlite3
import sys
import re

SIMKL_COLUMNS = [
    'simkl_id', 'TVDB_ID', 'TMDB', 'IMDB_ID', 'MAL_ID',
    'Type', 'Title', 'Year', 'LastEpWatched',
    'Watchlist', 'WatchedDate', 'Rating', 'Memo'
]

# Hardcoded database IDs for ambiguous or brand-new shows that fail Simkl's text matching
ID_MAP = {
    "law & order": {"TVDB_ID": "70522", "TMDB": "549", "IMDB_ID": "tt0098844"},
    "the pitt": {"TVDB_ID": "448698", "TMDB": "249673", "IMDB_ID": "tt31953406"},
    "paradise": {"TVDB_ID": "445209", "TMDB": "247063", "IMDB_ID": "tt31062634"},
    "the amateur": {"TMDB": "1129598", "IMDB_ID": "tt8332922"}, 
    "platonic": {"TVDB_ID": "391448", "TMDB": "114461", "IMDB_ID": "tt13317132"},
    "the last frontier": {"TVDB_ID": "430538", "TMDB": "221376", "IMDB_ID": "tt26887532"},
    "fallout": {"TVDB_ID": "339031", "TMDB": "113988", "IMDB_ID": "tt12637874"}
}

def find_default_db():
    """Check common locations for tautulli.db."""
    candidates = [
        os.path.expanduser('~/docker/appdata/tautulli/tautulli.db'),
        os.path.expanduser('./tautulli.db'),
        '/opt/tautulli/tautulli.db'
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return './tautulli.db'

def export_tautulli_history(db_path, output_path, user=None, since=None):
    if not os.path.exists(db_path):
        print(f"[ERROR] Database not found at: {db_path}", file=sys.stderr)
        sys.exit(1)

    # Open SQLite in URI Read-Only mode to protect database integrity while Tautulli runs
    db_uri = f"file:{os.path.abspath(db_path)}?mode=ro"
    try:
        conn = sqlite3.connect(db_uri, uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
    except sqlite3.Error as e:
        print(f"[ERROR] Failed to connect to database: {e}", file=sys.stderr)
        sys.exit(1)

    query = """
        SELECT 
            sh.media_type,
            sh.user,
            shm.grandparent_title,
            shm.title,
            shm.year,
            shm.parent_media_index AS season,
            shm.media_index AS episode,
            sh.started
        FROM session_history sh
        JOIN session_history_metadata shm ON sh.id = shm.id
        WHERE sh.media_type IN ('episode', 'movie')
    """
    params = []

    if user:
        query += " AND LOWER(sh.user) = LOWER(?)"
        params.append(user)

    if since:
        try:
            dt = datetime.datetime.strptime(since, '%Y-%m-%d')
            epoch_since = int(dt.timestamp())
            query += " AND sh.started >= ?"
            params.append(epoch_since)
        except ValueError:
            print(f"[WARNING] Invalid date format for --since '{since}'. Expected YYYY-MM-DD. Ignoring date filter.")

    query += " ORDER BY sh.started ASC"

    cursor.execute(query, params)
    rows = cursor.fetchall()

    if not rows:
        print("[INFO] No watch records found matching the specified criteria.")
        conn.close()
        return

    with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=SIMKL_COLUMNS)
        writer.writeheader()

        count = 0
        for row in rows:
            simkl_row = {col: '' for col in SIMKL_COLUMNS}
            
            if row['started']:
                simkl_row['WatchedDate'] = datetime.datetime.fromtimestamp(row['started']).strftime('%Y-%m-%d')
            
            simkl_row['Watchlist'] = 'completed'
            media_type = (row['media_type'] or '').lower()

            if media_type == 'episode':
                simkl_row['Type'] = 'tv'
                simkl_row['Title'] = row['grandparent_title'] or row['title']
                simkl_row['Year'] = '' 
                season = row['season']
                episode = row['episode']
                if season is not None and episode is not None:
                    simkl_row['LastEpWatched'] = f"s{season}e{episode}"
            elif media_type == 'movie':
                simkl_row['Type'] = 'movie'
                simkl_row['Title'] = row['title'] or ''
                simkl_row['Year'] = row['year'] or ''

            # Inject explicit IDs for known ambiguous titles
            # Automatically strips the " (YYYY)" from Tautulli titles to ensure a perfect ID map match
            title_clean = re.sub(r'\s*\(\d{4}\)$', '', simkl_row['Title']).lower().strip()
            if title_clean in ID_MAP:
                if 'TVDB_ID' in ID_MAP[title_clean]:
                    simkl_row['TVDB_ID'] = ID_MAP[title_clean]['TVDB_ID']
                if 'TMDB' in ID_MAP[title_clean]:
                    simkl_row['TMDB'] = ID_MAP[title_clean]['TMDB']
                if 'IMDB_ID' in ID_MAP[title_clean]:
                    simkl_row['IMDB_ID'] = ID_MAP[title_clean]['IMDB_ID']

            writer.writerow(simkl_row)
            count += 1

    conn.close()
    print(f"[SUCCESS] Exported {count} records to '{output_path}'.")

def main():
    parser = argparse.ArgumentParser(
        description="Export all (or filtered) watch history from Tautulli to a Simkl-compatible CSV."
    )
    parser.add_argument(
        '--db',
        default=find_default_db(),
        help="Path to tautulli.db"
    )
    parser.add_argument(
        '--output', '-o',
        default='simkl_tautulli_import.csv',
        help="Output CSV file path"
    )
    parser.add_argument(
        '--user', '-u',
        default=None,
        help="Filter watch history by a specific username"
    )
    parser.add_argument(
        '--since', '-s',
        default=None,
        help="Filter records watched on or after this date (YYYY-MM-DD)"
    )

    args = parser.parse_args()
    export_tautulli_history(args.db, args.output, args.user, args.since)

if __name__ == '__main__':
    main()