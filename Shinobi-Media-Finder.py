#!/usr/bin/env python3
# Shinobi-Media-Finder.py

"""
Sample Execution Commands:
--------------------------
To perform a complete media search within a directory:
python Shinobi-Media-Finder.py -t /path/to/media

To perform a specific type search within a directory (videos, images, documents, audios):
python Shinobi-Media-Finder.py -t /path/to/media -m

Replace the placeholder paths with the actual paths on your system where appropriate.

Parameters Table:
-----------------
| Flag  | Long Flag | Input Type     | Default | Description                                          |
|-------|-----------|----------------|---------|------------------------------------------------------|
| -t    | --target  | str (required) | -       | Directory containing media to process.              |
| -m    | --movie   | None (optional) | -       | Look for video/movie files only.                     |
| -p    | --picture | None (optional) | -       | Look for picture files only.                         |
| -d    | --document| None (optional) | -       | Look for document files only.                        |
| -s    | --sound   | None (optional) | -       | Look for sound/audio files only.                     |

If none of the optional parameters (-m, -p, -d, -s) are used, the script defaults to looking for all media types.

To keep the code lightweight, only one of the optional parameters is allowed at a time.
"""

import os
import argparse
from concurrent.futures import ThreadPoolExecutor
import time

# Supported file extensions
VIDEO_EXTENSIONS = ['mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'm4v', 'webm', '3gp', 'ogv', 'mpg', 'mpeg', 'm2v', 'm4p', 'm4v', 'mp2', 'mpe', 'mpv', 'm2ts', 'mxf', 'yuv', 'rm', 'asf', 'vob', 'amv', 'rmvb', 'drc', 'gifv', 'mts', 'm2ts', 'qt', 'svi', '3g2', 'roq', 'nsv', 'f4v', 'f4p', 'f4a', 'f4b']
IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'tiff', 'bmp', 'ico', 'jfif', 'webp', 'heif', 'ind', 'ai', 'eps', 'pdf', 'svg']
DOCUMENT_EXTENSIONS = ['doc', 'docx', 'pdf', 'otf', 'txt', 'rtf', 'xls', 'xlsx', 'csv', 'ods', 'ppt', 'pptx']
AUDIO_EXTENSIONS = ['mp3', 'wav', 'ogg', 'flac', 'aiff', 'mid']

def is_valid_dir(parser, arg):
    if not os.path.isdir(arg):
        parser.error(f"The directory {arg} does not exist!")
    else:
        return arg

def search_files(path, file_extensions):
    file_counts = {ext: 0 for ext in file_extensions}
    for subdir, dirs, files in os.walk(path):
        for file in files:
            ext = file.split('.')[-1]
            if ext in file_extensions:
                file_counts[ext] += 1
    return file_counts

def main():
    parser = argparse.ArgumentParser(description="Process media files and count per file type extension.")
    parser.add_argument("-t", "--target", dest="target", required=True, type=lambda x: is_valid_dir(parser, x),
                        help="Directory containing media to process (required).")
    search_by_type = parser.add_mutually_exclusive_group()
    search_by_type.add_argument("-m", "--movie", dest="movie", action='store_true', help="Look for video/movie files only.")
    search_by_type.add_argument("-p", "--picture", dest="picture", action='store_true', help="Look for picture files only.")
    search_by_type.add_argument("-d", "--document", dest="document", action='store_true', help="Look for document files only.")
    search_by_type.add_argument("-s", "--sound", dest="sound", action='store_true', help="Look for sound/audio files only.")
   
    args = parser.parse_args()

    start_time = time.time()

    search_types = {
        "movie": VIDEO_EXTENSIONS,
        "picture": IMAGE_EXTENSIONS,
        "document": DOCUMENT_EXTENSIONS,
        "sound": AUDIO_EXTENSIONS
    }
    
    if args.movie:
        search_extensions = VIDEO_EXTENSIONS
    elif args.picture:
        search_extensions = IMAGE_EXTENSIONS
    elif args.document:
        search_extensions = DOCUMENT_EXTENSIONS
    elif args.sound:
        search_extensions = AUDIO_EXTENSIONS
    else:
        search_extensions = sum([exts for exts in search_types.values()], [])

    with ThreadPoolExecutor() as executor:
        future = executor.submit(search_files, args.target, search_extensions)
        counts = future.result()

    execution_time = time.time() - start_time
    total_files = sum(counts.values())
    performance_index = total_files / execution_time if execution_time > 0 else 0

    print(f"Searching for {','.join(search_types.keys()) if not any(vars(args).values()) else ', '.join(key for key, value in vars(args).items() if value and key in search_types)} files:\n")

    print("{:<10} {:<10}".format("Extension", "Count"))
    for ext_type, exts in search_types.items():
        if not vars(args)[ext_type] and any(vars(args).values()): 
            continue
        print(f"{'-' * 20} {ext_type.upper()} {'-' * 20}")
        for ext in exts:
            if counts[ext] > 0:
                print("{:<10} {:<10}".format(ext.upper(), counts[ext]))

    print("\n{:<10} {:<10}".format("Total Files:", total_files))
    print("{:<10} {:.2f} seconds".format("Total Time Spent:", execution_time))
    print("{:<10} {:.2f} files/second".format("Performance Index:", performance_index))

if __name__ == '__main__':
    main()
