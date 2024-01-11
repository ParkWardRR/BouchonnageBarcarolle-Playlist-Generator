#!/usr/bin/env python3
# Manato-Cascading-Folder-Playlist-Generator.py

"""
Sample Execution Commands:
--------------------------
To generate a playlist without any filters and without creating an archive:
python Manato-Cascading-Folder-Playlist-Generator.py -dir /path/to/media -mount /client/media -output /path/to/output -autoplst yes -zip no

To generate a playlist with shuffled content and a minimum video length of 30 seconds, and archive the result:
python Manato-Cascading-Folder-Playlist-Generator.py -dir /path/to/media -mount /client/media -output /path/to/output -shuffle yes -min_length 30

To generate a playlist of horizontal videos only, a specified filename for the playlist, and create an archive:
python Manato-Cascading-Folder-Playlist-Generator.py -dir /path/to/media -mount /client/media -output /path/to/output -filename my_horizontal_playlist.m3u8 -horz -zip yes

For Mac specific playlist run:
python Manato-Cascading-Folder-Playlist-Generator.py -dir /path/to/media/ -mount /client/media/ -autoplst yes -shuffle yes -overwrite -horz -output /path/to/output

Parameters Table:
-----------------
| Flag         | Input Type     | Default  | Description                                                     | Example                                               |
|--------------|----------------|----------|-----------------------------------------------------------------|-------------------------------------------------------|
| -dir         | str (required) | -        | Directory containing media to process.                          | -dir /path/to/media                                   |
| -mount       | str (required) | -        | Root of the directory on the client corresponding to -dir.      | -mount /client/media                                  |
| -autoplst    | str            | no       | Autogenerate a playlist name? 'yes' or 'no'.                    | -autoplst yes                                         |
| -shuffle     | str            | no       | Shuffle the playlist? 'yes' or 'no'.                            | -shuffle yes                                          |
| -output      | str (required) | -        | Output directory for the playlist file.                         | -output /path/to/output                               |
| -overwrite   | flag           | False    | Overwrite existing file if necessary.                           | -overwrite                                            |
| -portrait    | flag           | False    | Include only videos with portrait orientation?                  | -portrait                                             |
| -horz        | flag           | False    | Include only videos with horizontal orientation?                | -horz                                                 |
| -min_length  | float          | -        | Minimum length of video in seconds to include.                  | -min_length 30                                        |
| -max_length  | float          | -        | Maximum length of video in seconds to include.                  | -max_length 120                                       |
| -filename    | str            | -        | Specify a filename for the playlist file.                       | -filename custom_playlist.m3u8                       |
| -zip         | str            | yes      | Create a .7z compressed archive of the output directory? 'yes' or 'no'. | -zip no                                 |

Note: Replace the placeholder paths with actual paths on your system where appropriate.
Additional Script Notes:
- Dependencies: ffmpeg, ffprobe, ffmpeg-python, and pip.
- Use command line arguments for specifying options (via argparse).
- Validity checks are performed for directory and file existence.
- Dependencies are checked at runtime; if missing, they're installed via pip.
- `scan_directory`: Scans for videos, filters by length and orientation.
- `generate_filters_flag`: Defines flags for video selection based on user input.
- `generate_output_folder`: Ensures the output folder exists.
- `main()`: Orchestrates the overall playlist generation process.
------
"""
# Standard library imports
import os
import argparse
import random
import string
import sys
from datetime import datetime

# Third-party imports for handling video-processing and archive creation
import ffmpeg
import py7zr

# Supported media file extensions processed by this script.
VIDEO_EXTENSIONS = ['mp4', 'avi', 'mov']

def is_valid_file(parser, arg):
    """Ensure the specified file system entity exists."""
    if not os.path.exists(arg):
        parser.error(f"The file {arg} does not exist!")
    else:
        return arg

def validate_length(args, full_path):
    """Validate the length of a video using ffmpeg to probe its metadata."""
    try:
        probe = ffmpeg.probe(full_path)
        duration = float(probe['format'].get('duration', '0'))  # Change made here
    except ffmpeg._run.Error as e:
        print(str(e))
        return False
    return not ((args.min_length and duration < args.min_length) or (args.max_length and duration > args.max_length))

def scan_directory(args):
    """Scan the specified directory, applying any filters, and compile the playlist."""
    playlist = []
    for subdir, dirs, files in os.walk(args.dir):
        for file in files:
            ext = file.split('.')[-1]
            if ext in VIDEO_EXTENSIONS:
                full_path = os.path.join(subdir, file)
                if not validate_length(args, full_path):
                    continue
                if args.portrait_only or args.horz_only:
                    probe = ffmpeg.probe(full_path)
                    video_info = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
                    width, height = int(video_info['width']), int(video_info['height'])
                    if (args.portrait_only and width >= height) or (args.horz_only and height > width):
                        continue
                mount_path = subdir.replace(args.dir, args.mount)
                playlist.append(os.path.join(mount_path, file))
    return playlist

def generate_output_folder(args):
    """Generate the specified output folder if it does not exist."""
    if not os.path.exists(args.output_folder):
        os.makedirs(args.output_folder)

def generate_filters_flag(args):
    """Construct a string flag representing the filters applied to the playlist."""
    filters = ['shuffle' if args.shuffle_playlist == 'yes' else '',
               'portrait' if args.portrait_only else '',
               'horizontal' if args.horz_only else '']
    return "-".join(filter(None, filters)) or "nofilter"

def create_7z_archive(output_folder, archive_name):
    """Create a .7z archive of the specified output folder using maximum compression."""
    with py7zr.SevenZipFile(archive_name, 'w', compression='7z') as archive:
        for root, dirs, files in os.walk(output_folder):
            for file in files:
                file_path = os.path.join(root, file)
                archive_path = os.path.relpath(file_path, output_folder)
                archive.write(file_path, archive_path)
    print(f".7z Archive created: {archive_name}")

def main():
    # Parse and manage the script's command-line arguments.
    parser = argparse.ArgumentParser(description="Process media files and create a playlist file with optional .7z archiving.")
    parser.add_argument("-dir", dest="dir", required=True, type=lambda x: is_valid_file(parser, x), help="Directory containing media to process (required).")
    parser.add_argument("-mount", dest="mount", required=True, help="Root of the directory on the client corresponding to -dir (required).")
    parser.add_argument("-autoplst", dest="auto_gen_playlist", default='no', choices=['yes', 'no'],
                        help="Autogenerate a playlist name? 'yes' or 'no' (default 'no').")
    parser.add_argument("-shuffle", dest="shuffle_playlist", default='no', choices=['yes', 'no'],
                        help="Shuffle the playlist? 'yes' or 'no' (default 'no').")
    parser.add_argument("-output", dest="output_folder", required=True, help="Output directory for the playlist file (required).")
    parser.add_argument("-overwrite", dest="overwrite", action='store_true',
                        help="Overwrite existing file? Provide flag if 'yes'.")
    parser.add_argument("-portrait", dest="portrait_only", action='store_true',
                        help="Include only videos with portrait orientation? Provide flag if 'yes'.")
    parser.add_argument("-horz", dest="horz_only", action='store_true',
                        help="Include only videos with horizontal orientation? Provide flag if 'yes'.")
    parser.add_argument("-min_length", dest="min_length", type=float,
                        help="Minimum length of video in seconds. Videos shorter than this will be excluded.")
    parser.add_argument("-max_length", dest="max_length", type=float,
                        help="Maximum length of video in seconds. Videos longer than this will be excluded.")
    parser.add_argument("-filename", dest="filename", help="Specify a filename for the playlist file (optional).")
    parser.add_argument("-zip", dest="zip_output", default='yes', choices=['yes', 'no'],
                        help="Create a .7z compressed archive of the output directory? 'yes' or 'no' (default 'yes').")
    
    args = parser.parse_args()
    
    # Directory handling and playlist generation
    generate_output_folder(args)
    playlist = scan_directory(args)
    filter_string = generate_filters_flag(args)

    # Creating playlist file
    playlist_name = args.filename if args.filename else f'playlist_{datetime.now().strftime("%Y%m%d%H%M%S")}.m3u8'
    output_file = os.path.join(args.output_folder, playlist_name)
    if os.path.exists(output_file) and not args.overwrite:
        print('File already exists, and overwrite is not set. Please change the name or set -overwrite flag.')
        sys.exit(1)
    with open(output_file, 'w') as f:
        for vid_path in playlist:
            f.write(f'{vid_path}\n')
    print(f"Playlist file has been successfully created at: {output_file}")

    # .7z Archive creation (if toggled on)
    if args.zip_output.lower() == 'yes':
        archive_name = f"{playlist_name.rsplit('.', 1)[0]}.7z"
        archive_path = os.path.join(args.output_folder, archive_name)
        create_7z_archive(args.output_folder, archive_path)

if __name__ == '__main__':
    main()

"""
- The following is notes about the Barcarolle-Playlist-Generator.py: 
- This script dependencies are: ffmpeg, ffprobe, ffmpeg-python, and pip. 
- To call this program, command line arguments are taken using argparse. 
- -dir argument specifies the directory to scan. This is mandatory and must be a valid path on the file system.
- -mount argument corresponds to the client root directory of '-dir'. It's a mandatory field but no validation is enforced. (this is useful when specififying the mac path - See below for the "Run for mac playlists")
- -autoplst (default 'no') lets user autogenerate a playlist name. Options are 'yes' and 'no'.
- -shuffle (default 'no') if set to 'yes', shuffles the playlist. Acceptable options are 'yes' and 'no'.
- -output specifies an output directory for the playlist file. It's mandatory.
- Providing -overwrite flag overwrites any existing file in the output directory.
- The -portrait flag only includes vertically oriented videos if provided.
- The -horz flag only includes horizontally oriented videos when used.
- -min_length filters videos shorter than the specified value in seconds.
- -max_length filters out videos longer than the specified value in seconds.
- -filename allows a user to specify a filename for the playlist file.
- The argparse setup also includes a validity check for the provided directory and the file existence.
- Required dependencies checked at runtime; if not found, they're installed via pip (`check_dependencies` function).
- scan_directory function scans provided directory recursively for video files of specific extensions, filters on the basis of length and orientation and populates a playlist.
- generate_filters_flag function defines video selection flags based on user preferences.
- generate_output_folder function creates an output folder if it doesn't exist.
- The main() function runs the overall playlist generation process.
------
"""
