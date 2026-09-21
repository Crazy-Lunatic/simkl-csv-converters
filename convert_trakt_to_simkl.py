import argparse
import csv
import json
from pathlib import Path


# Define the output CSV file
output_file = 'simkl_import.csv'

# Strict Simkl headers based on their template
csv_columns = [
    'simkl_id', 'TVDB_ID', 'TMDB', 'IMDB_ID', 'MAL_ID', 'Type', 'Title',
    'Year', 'LastEpWatched', 'Watchlist', 'WatchedDate', 'Rating', 'Memo'
]


def prompt_for_input_folder():
    """Fallback for Python installs where the graphical folder picker is unavailable."""
    print('The folder picker is unavailable on this Python installation.')
    typed_path = input(
        'Enter the folder containing watched-history-*.json files: '
    ).strip().strip('"')
    return Path(typed_path).expanduser() if typed_path else None


def choose_input_folder():
    """Open a folder picker for the Trakt export directory."""
    script_dir = Path(__file__).resolve().parent

    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError:
        return prompt_for_input_folder()

    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        selected = filedialog.askdirectory(
            title='Select the folder containing Trakt watched JSON files',
            initialdir=str(script_dir),
            mustexist=True,
        )
        root.destroy()
    except tk.TclError:
        return prompt_for_input_folder()

    return Path(selected) if selected else None


def convert_trakt_export(input_folder, output_path):
    """Convert watched-history-*.json files from one Trakt export folder."""
    json_files = sorted(input_folder.glob('watched-history-*.json'))

    if not json_files:
        print(f'No watched-history-*.json files were found in: {input_folder}')
        return 0, 0

    rows_written = 0

    with output_path.open('w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()

        for file in json_files:
            with file.open('r', encoding='utf-8') as f:
                data = json.load(f)

            for item in data:
                # Initialize an empty row matching the exact column keys
                row = {col: '' for col in csv_columns}

                row['Type'] = item.get('type', '')

                # Trakt dates are ISO 8601; slicing the first 10 chars gives us standard YYYY-MM-DD
                row['WatchedDate'] = (
                    item.get('watched_at', '')[:10]
                    if item.get('watched_at')
                    else ''
                )

                # Hardcoding to 'completed' as defined by Simkl's Watchlist header expectations
                row['Watchlist'] = 'completed'

                # Handle Shows/Episodes
                if row['Type'] == 'episode':
                    show = item.get('show', {})
                    episode = item.get('episode', {})
                    ids = show.get('ids', {})

                    row['Title'] = show.get('title', '')
                    row['Year'] = show.get('year', '')

                    season = episode.get('season', '')
                    ep_num = episode.get('number', '')
                    row['LastEpWatched'] = f"s{season}e{ep_num}"

                    # Extract robust IDs for matching
                    row['TVDB_ID'] = ids.get('tvdb', '')
                    row['TMDB'] = ids.get('tmdb', '')
                    row['IMDB_ID'] = ids.get('imdb', '')

                # Handle Movies
                elif row['Type'] == 'movie':
                    movie = item.get('movie', {})
                    ids = movie.get('ids', {})

                    row['Title'] = movie.get('title', '')
                    row['Year'] = movie.get('year', '')

                    # Extract robust IDs for matching
                    row['TMDB'] = ids.get('tmdb', '')
                    row['IMDB_ID'] = ids.get('imdb', '')

                writer.writerow(row)
                rows_written += 1

    return len(json_files), rows_written


def main():
    parser = argparse.ArgumentParser(
        description='Convert Trakt watched-history JSON exports into a Simkl import CSV.'
    )
    parser.add_argument(
        'folder',
        nargs='?',
        help='Folder containing watched-history-*.json files. If omitted, a folder picker opens.',
    )
    args = parser.parse_args()

    if args.folder:
        input_folder = Path(args.folder).expanduser()
    else:
        input_folder = choose_input_folder()

    if input_folder is None:
        print('No folder selected. Nothing was converted.')
        return 1

    input_folder = input_folder.resolve()

    if not input_folder.is_dir():
        print(f'The selected path is not a folder: {input_folder}')
        return 1

    output_path = Path.cwd() / output_file
    file_count, row_count = convert_trakt_export(input_folder, output_path)

    if file_count == 0:
        return 1

    print(f'Selected Trakt export folder: {input_folder}')
    print(f'Processed {file_count} watched-history JSON file(s) and wrote {row_count} row(s).')
    print(f"Success! Data compiled into {output_path} matching Simkl's strict schema.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
