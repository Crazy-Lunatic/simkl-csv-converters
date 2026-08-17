import json
import csv
import glob

# Define the output CSV file
output_file = 'simkl_import.csv'
# Strict Simkl headers based on their template
csv_columns = ['simkl_id', 'TVDB_ID', 'TMDB', 'IMDB_ID', 'MAL_ID', 'Type', 'Title', 'Year', 'LastEpWatched', 'Watchlist', 'WatchedDate', 'Rating', 'Memo']

# Find all watched history JSON files in the current directory
json_files = glob.glob('watched-history-*.json')

with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    writer.writeheader()

    for file in json_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                # Initialize an empty row matching the exact column keys
                row = {col: '' for col in csv_columns}
                
                row['Type'] = item.get('type', '')
                # Trakt dates are ISO 8601; slicing the first 10 chars gives us standard YYYY-MM-DD
                row['WatchedDate'] = item.get('watched_at', '')[:10] if item.get('watched_at') else ''
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

print(f"Success! Data compiled into {output_file} matching Simkl's strict schema.")