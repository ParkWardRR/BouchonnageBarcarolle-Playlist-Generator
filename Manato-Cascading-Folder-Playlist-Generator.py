#!/usr/bin/env python3
# Manato-Cascading-Folder-Playlist-Generator.py


"""
Manato Cascading Folder Playlist Generator
This script generates playlists for media in a specified directory.
This script checks if git and Barcarolle-Playlist-Generator.py are installed, 
If not, the script prompts the user to download it from a specified URL.
Usage: `python Manato-Cascading-Folder-Playlist-Generator.py -MediaDir /mnt/MonterosaSync/Storage/Other/ -TargetDir /mnt/MonterosaSync/pb_out/Storage/Other/ -horizontal -min_length 300 -os both -shuffle -t 4`
"""

import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
import argparse
import py7zr


def is_valid_directory(parser, path):
    """
    Check if the directory path is valid.
    If path does not exist, a new directory is created.
    """
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


def check_for_git():
    """
    Function to check for git installation.
    """
    try:
        print("Checking for Git installation...")
        subprocess.check_output(["git", "--version"], timeout=10)  # using subprocess.check_output instead
        print("Git is installed.\n")
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f"\nGit is not installed or encountered an error:{e}. Please install or fix Git to proceed.")
        sys.exit()
        
def compress_with_7z(output_directory, zip_path):
    try:
        print('Compressing....')
        with py7zr.SevenZipFile(f'{zip_path}.7z', 'w') as z:
            z.writeall(output_directory)
        print(f'Compressed the directory at: {zip_path}.7z')
    except Exception as e:
        print(f"An error occurred while compressing the directory: {e}")


def check_for_barcarolle_script():
    """
    Function to check for the existence of Barcarolle-Playlist-Generator.py.
    """
    if not os.path.isfile("./Barcarolle-Playlist-Generator.py"):
        print("Barcarolle-Playlist-Generator.py not found.")
        download = input("Should I download it for you? (yes/no): ")
        if download.lower() == "yes":
            print("Downloading Barcarolle-Playlist-Generator.py from the repository...")
            os.system("git clone https://github.com/ParkWardRR/BouchonnageBarcarolle-Playlist-Generator.git")
            print("\nDownloaded Barcarolle-Playlist-Generator.py successfully.")
        else:
            print("\nPlease download Barcarolle-Playlist-Generator.py and place it in the same directory as this script.")
            sys.exit()

def call_playlist_generator(input_dir, output_dir, mac_input_dir, shuffle, **kwargs):
    """
    Function to call Playlist Generator Script with arguments.
    """
    command = ["python", "Barcarolle-Playlist-Generator.py"]

    arg_mapping = {
        "portrait": "-portrait",
        "horizontal": "-horz",
        "min_length": "-min_length",
        "max_length": "-max_length"
    }

    command.extend(["-dir", input_dir])
    command.extend(["-mount", mac_input_dir])
    command.extend(["-output", output_dir])
    command.extend(["-autoplst", "yes"])
    command.extend(["-shuffle", "yes" if shuffle else "no"])
    command.extend(["-overwrite"])

    for arg, value in kwargs.items():
        if value is True and arg in arg_mapping.keys():
            command.append(arg_mapping[arg])
        elif value and arg == "min_length":
            command.extend([arg_mapping[arg], str(value)])

    print("Calling Barcarolle-Playlist-Generator.py...")
    subprocess.call(command)


def playlist_for_directories(executor_arg):
    """
    Creates a playlist for all the directories within the specified path.
    """
    (structure, dirpath, OS, args) = executor_arg
    if OS == "mac":
        mac_input_dir = dirpath.replace("/mnt/", "/Volumes/")
    else:
        mac_input_dir = dirpath

    print(f"\nCreating {OS} folder: {structure}")
    call_playlist_generator(dirpath, structure, mac_input_dir, args.shuffle,
                                    portrait=args.portrait, 
                                    horizontal=args.horizontal,
                                    min_length=args.min_length, 
                                    max_length=args.max_length)

def main():
    parser = argparse.ArgumentParser()
    # Argument for the media directory path
    parser.add_argument("-MediaDir", 
                        help="Specify the root media directory",
                        required=True, 
                        type=lambda x: is_valid_directory(parser, x))
    
    # Argument for the target directory path
    parser.add_argument("-TargetDir", 
                        help="Specify the root target directory",
                        required=True, 
                        type=lambda x: is_valid_directory(parser, x))
    
    # Argument for OS type
    parser.add_argument("-os", 
                        help="Specify the operating system type",
                        choices=["mac", "linux", "both"], 
                        default="linux")
    
    # Argument for portrait filter
    parser.add_argument("-portrait", 
                        help="Specify the portrait filter",
                        action='store_true')
    
    # Argument for horizontal filter
    parser.add_argument("-horizontal", 
                        help="Specify the horizontal filter",
                        action='store_true')
    
    # Argument for minimum length filter
    parser.add_argument("-min_length", 
                        help="Specify the minimum length filter",
                        type=float)
    
    # Argument for maximum length filter
    parser.add_argument("-max_length", 
                        help="Specify the maximum length filter",
                        type=float)
    
    # Argument for shuffle option
    parser.add_argument("-shuffle",
                        help="Specify to shuffle playlist",
                        action='store_true')
    parser.add_argument("--zip", 
                    help="Specify to create a zip file of the output directory",
                    action='store_true')

    parser.add_argument("--zippath", 
                    help="Specify the path of the zipped file",
                    required=False, 
                    default=os.path.join(os.getcwd(), "compressed_dir"))
    # Argument for number of threads
    parser.add_argument("-t", 
                        help="Specify the number of threads to be used, default to number of cores", 
                        type=int, 
                        default=os.cpu_count()) # default to number of cores if not specified
                        
    args = parser.parse_args()
    MAX_WORKERS = args.t # use argument for maximum threads

    # print a statement to confirm num of threads.
    print(f'Running script using {MAX_WORKERS} worker threads.')

    check_for_git()
    check_for_barcarolle_script()

    OSs = ["mac", "linux"] if args.os == "both" else [args.os]
    
    executor_args = []

    for dirpath, dirs, files in os.walk(args.MediaDir):
        for OS in OSs:
            structure = os.path.join(args.TargetDir, OS, os.path.relpath(dirpath, args.MediaDir))
            if not os.path.isdir(structure):
                os.makedirs(structure)
            executor_args.append((structure, dirpath, OS, args))
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(playlist_for_directories, executor_args)
    if args.zip:
        compress_with_7z(args.TargetDir, args.zippath)

if __name__ == "__main__":
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
- Run for mac playlists: Barcarolle-Playlist-Generator.py -dir /mnt/MonterosaSync/Storage/Other/Batch/r1001/ -mount /Volumes/MonterosaSync/Storage/Other/Batch/r1001/ -autoplst yes -shuffle yes -overwrite -horz -output /mnt/MonterosaSync/pb_output
------
"""
