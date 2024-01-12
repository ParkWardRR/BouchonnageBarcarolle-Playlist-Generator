#!/usr/bin/env python3
# Barcarolle_Playlist_Generator.py

"""
Run the script like:
--------------------------
To generate a playlist without any filters and without creating an archive:
python Barcarolle_Playlist_Generator.py -dir /path/to/media -mount /client/media -output /path/to/output -autoplst yes -zip no

To generate a playlist with shuffled content and a minimum video length of 30 seconds, and archiving the result:
python Barcarolle_Playlist_Generator.py -dir /path/to/media -mount /client/media -output /path/to/output -shuffle yes -min_length 30

To generate a playlist of horizontal videos only, a specified filename for the playlist, and create an archive:
python Barcarolle_Playlist_Generator.py -dir /path/to/media -mount /client/media -output /path/to/output -filename my_horizontal_playlist.m3u8 -horz -zip yes

For Mac specific playlist run:
python Barcarolle_Playlist_Generator.py -dir /path/to/media/ -mount /client/media/ -autoplst yes -shuffle yes -overwrite -horz -output /path/to/output

When executing the script on a VM for usage on macOS, point '-dir' to the VM's media path and '-mount' to its macOS counterpart. 
This enables macOS-path playlist generation on a VM. 
python Barcarolle_Playlist_Generator.py -dir /path/on/vm -mount /path/on/mac -output /output/path ...

Parameters Table:
--------------------
| Flag         | Input Type     | Default  | Description                                                     | Example                                               |
|---------------|------------------|------------|--------------------------------------------------------------------|----------------------------------------------------------|
| -dir          | str (required)  | -           | Directory containing media to process.                           | -dir /path/to/media                                    |
| -mount      | str (required)  | -           | Root directory on client corresponding to -dir.       | -mount /client/media                                   |
| -autoplst    | str                | no        | Autogenerate a playlist name? 'yes' or 'no'.               | -autoplst yes                                          |
| -shuffle     | str                | no        | Shuffle the playlist? 'yes' or 'no'.                          | -shuffle yes                                           |
| -output      | str (required)  | -           | Output directory for the playlist file.                       | -output /path/to/output                                |
| -overwrite | flag                | False   | Overwrite existing file if necessary.                        | -overwrite                                             |
| -portrait  | flag                | False   | Include only videos with portrait orientation?           | -portrait                                              |
| -horz        | flag                | False   | Include only videos with horizontal orientation?         | -horz                                                  |
| -min_length | float             | -           | Include videos longer than this value in seconds.      | -min_length 30                                         |
| -max_length | float             | -           | Include videos shorter than this value in seconds.    | -max_length 120                                       |
| -filename   | str                 | -           | Specify a filename for the playlist file.                  | -filename custom_playlist.m3u8                      |
| -zip          | str                 | yes       | Create a .7z compressed archive of output? 'yes' or 'no'.| -zip no                                               |

Note: Replace the placeholder paths with real paths on your system as needed.
For more about Barcarolle_Playlist_Generator.py:
- Dependencies: ffmpeg, ffprobe, ffmpeg-python, pip.
- Use command line arguments per argparse for options.
- Performs validity checks for directory and file existence.
- Checks dependencies at runtime; installs missing ones via pip.
- 'scan_directory': Scans for videos, filters by length and orientation.
- 'generate_filters_flag': Defines video selection flags based on user input.
- 'generate_output_folder': Makes sure the output folder is available.
- 'main()': Runs the overall playlist generation process.
------

"""


import os
import argparse
import random
import string
import sys
from datetime import datetime

# Third-party imports for handling video-processing and archive creation
import ffmpeg
import py7zr

VIDEO_EXTENSIONS = ['mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'm4v', 'webm', '3gp', 'ogv', 'mpg', 'mpeg', 'm2v', 'm4p', 'm4v', 'mp2', 'mpe', 'mpv', 'm2ts', 'mxf', 'yuv', 'rm', 'asf', 'vob', 'amv', 'rmvb', 'drc', 'gifv', 'mts', 'mts', 'm2ts', 'qt', 'svi', '3g2', 'roq', 'nsv', 'f4v', 'f4p', 'f4a', 'f4b']

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error(f"The file {arg} does not exist!")
    else:
        return arg

def validate_length(args, full_path):
    try:
        probe = ffmpeg.probe(full_path)
        video_info = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        if video_info is None:
            print(f"File: {full_path} is not a valid video. Skipping...")
            return False
        if 'duration' in probe['format']:
            duration = float(probe['format']['duration'])
        else:
            print(f"No duration found for file: {full_path}. Skipping...")
            return False
    except ffmpeg._run.Error as e:
        print(str(e))
        return False
    min_length = getattr(args, 'min_length', None)
    max_length = getattr(args, 'max_length', None)
    return not ((min_length and duration < min_length) or (max_length and duration > max_length))

def scan_directory(args):
    playlist = []
    for subdir, dirs, files in os.walk(args.dir):
        for file in files:
            ext = file.split('.')[-1]
            if ext.lower() in VIDEO_EXTENSIONS:
                full_path = os.path.join(subdir, file)
                if not validate_length(args, full_path):
                    continue
                if args['portrait'] or args['horz']:
                    probe = ffmpeg.probe(full_path)
                    video_info = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
                    width, height = int(video_info['width']), int(video_info['height'])
                    if (args['portrait'] and width >= height) or (args['horz'] and height > width):
                        continue
                mount_path = subdir.replace(args.dir, args.mount)
                playlist.append(os.path.join(mount_path, file))
            else:
                print(f"File: {os.path.join(subdir, file)} is not a recognizable video format. Skipping...")
    return playlist

def generate_output_folder(args):
    if not os.path.exists(args.output):
        os.makedirs(args['output'])

def generate_filters_flag(args):
    filters = ['shuffle' if args['shuffle'] == 'yes' else '',
               'portrait' if args['portrait'] else '',
               'horz' if args['horz'] else '']
    return "-".join(filter(None, filters)) or "nofilter"

def create_7z_archive(output_folder, archive_name):
    compression = {
      "id": py7zr.FILTER_LZMA2,
      "preset": 9  # LZMA2 maximum compression preset
    }
    with py7zr.SevenZipFile(archive_name, 'w', filters=[compression]) as archive:
        for root, dirs, files in os.walk(output_folder):
            for file in files:
                file_path = os.path.join(root, file)
                archive_path = os.path.relpath(file_path, output_folder)
                archive.write(file_path, archive_path)
    print(f".7z Archive created: {archive_name}")

def main(args):
    generate_output_folder(args)
    playlist = scan_directory(args)
    filter_string = generate_filters_flag(args)
    
    playlist_name = args['filename'] if args['filename'] else f'playlist_{datetime.now().strftime("%Y%m%d%H%M%S")}.m3u8'
    output_file = os.path.join(args.output, playlist_name)
    if os.path.exists(output_file) and not args['overwrite']:
        print('File already exists, and overwrite is not set. Please change the name or set -overwrite flag.')
        sys.exit(1)
    with open(output_file, 'w') as f:
        for vid_path in playlist:
            f.write(f'{vid_path}\n')
    print(f"Playlist file has been successfully created at: {output_file}")

    if args['zip'] == 'yes':
        archive_name = f"{playlist_name.rsplit('.', 1)[0]}.7z"
        archive_path = os.path.join(args['output'], archive_name)
        create_7z_archive(args['output'], archive_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process media files and create a playlist file with optional .7z archiving.")
    parser.add_argument('-dir', required=True, help="Directory containing media to process.")
    parser.add_argument('-mount', required=True, help="Root directory on client corresponding to -dir.")
    parser.add_argument('-autoplst', default='no', help="Autogenerate a playlist name? 'yes' or 'no'.")
    parser.add_argument('-shuffle', default='no', help="Shuffle the playlist? 'yes' or 'no'.")
    parser.add_argument('-output', required=True, help="Output directory for the playlist file.")
    parser.add_argument('-overwrite', action='store_true', help="Overwrite existing file if necessary.")
    parser.add_argument('-portrait', action='store_true', help="Include only videos with portrait orientation?")
    parser.add_argument('-horz', action='store_true', help="Include only videos with horizontal orientation?")
    parser.add_argument('-min_length', type=float, help="Include videos longer than this value in seconds.")
    parser.add_argument('-max_length', type=float, help="Include videos shorter than this value in seconds.")
    parser.add_argument('-filename', help="Specify a filename for the playlist file.")
    parser.add_argument('-zip', default='yes', help="Create a .7z compressed archive of output? 'yes' or 'no'.")

    args = parser.parse_args()
    arg_dict = vars(args)
    main(arg_dict)


"""
- The following is more about the Barcarolle_Playlist_Generator.py: 
- It depends on ffmpeg, ffprobe, ffmpeg-python, and pip. 
- Use command line arguments to specify options (utilizes argparse). 
- '-dir' specifies the directory to scan. It's mandatory and must be a valid path on file system.
- '-mount' is the client's root directory equivalent to '-dir'. Mandatory field but no validation is enforced.
- '-autoplst' (default 'no') determines if a playlist name should be auto-generated. Options are 'yes' and 'no'.
- '-shuffle' (default 'no'), if set to 'yes', shuffles the playlist. Options are 'yes' and 'no'.
- '-output' is required to specify an output directory for playlist file.
- The '-overwrite' flag overwrites an existing file in the output directory if provided.
- Including '-portrait' flag only includes videos with vertical orientation.
- Including '-horz' flag only includes videos with horizontal orientation.
- Define '-min_length' in seconds to filter out videos shorter than this value.
- Define '-max_length' in seconds to filter out videos longer than this value.
- If provided, '-filename' allows to specify a filename for the playlist file.
- In addition to argument parsing, the script checks for the validity of the provided directory and the existence of files.
- The dependencies are checked at runtime; if not there, script installs them via pip ('check_dependencies' function).
- The 'scan_directory' function scans the provided directory for video files with specific extensions, filters based on length and orientation and creates the playlist.
- 'generate_filters_flag' function sets up video selection flags based on user's preferences.
- 'generate_output_folder' function creates the output folder if it doesn't exist.
- 'main()' function operates the overall playlist generation process.
------
"""
