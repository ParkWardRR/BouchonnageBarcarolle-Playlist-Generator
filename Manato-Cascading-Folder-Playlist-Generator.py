#!/usr/bin/env python3
# Manato-Cascading-Folder-Playlist-Generator.py

"""
Manato Cascading Folder Playlist Generator
This script generates playlists for media in a specified directory.
After checking if git and Barcarolle-Playlist-Generator.py are installed, 
the script prompts the user to download it from a specified URL if not.

To run the command with various options, use the following flags:
-MediaDir to specify the root media directory
-TargetDir to specify the root target directory
-os to specify the operating system type
-portrait to specify the portrait filter
-horizontal to specify the horizontal filter
-min_length to specify the minimum length filter
-max_length to specify the maximum length filter
  
For example:
python Manato-Cascading-Folder-Playlist-Generator.py -MediaDir /your/media/directory/ 
-TargetDir /your/target/directory/ -horizontal -min_length 300 -os both
"""

import argparse
import os
import subprocess
from getpass import getpass

def is_valid_directory(parser, path):
    """
    Check if the directory path is valid.
    """
    if not os.path.isdir(path):
        os.makedirs(path)
    return path

def check_for_git():
    """
    Function to check for the installation of git. 
    If it is not installed, it prompts the user to install it.
    """
    command = ["git", "--version"]
    try:
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print("\nGit is not installed. Please install git to proceed.")
        quit()
        
def check_for_barcarolle_script():
    """
    Function to check for the presence of the Barcarolle-Playlist-Generator.py script.
    If it is not found, it prompts the user to download it.
    """
    if not os.path.isfile("./Barcarolle-Playlist-Generator.py"):
        download = input("\nBarcarolle-Playlist-Generator.py not found. Should I download it for you? (yes/no): ")
        if download.lower() == "yes":
            os.system("git clone https://github.com/ParkWardRR/BouchonnageBarcarolle-Playlist-Generator.git")
            print("\nDownloaded Barcarolle-Playlist-Generator.py successfully.")
        else:
            print("\nKindly download Barcarolle-Playlist-Generator.py from the mentioned URL and place it in the same directory as this script.")

def call_playlist_generator(input_dir, output_dir, **kwargs):
    """
    Function to call the Playlist Generator Script with appropriate arguments.
    """
    # Base command
    command = ["python", "Barcarolle-Playlist-Generator.py"]
    
    # Mapping of kwargs to command line arguments
    arg_mapping = {
        "portrait": "-portrait",
        "horizontal": "-horz",
        "min_length": "-min_length",
        "max_length": "-max_length"
    }

    # Construct the command
    command.extend(["-dir", input_dir])
    command.extend(["-mount", input_dir])
    command.extend(["-output", output_dir])
    command.extend(["-autoplst", "yes"])
    command.extend(["-overwrite"])

    # Extend the command with kwargs
    for arg, value in kwargs.items():
        if value is True and arg in arg_mapping.keys():
            command.append(arg_mapping[arg])
        elif value and arg == "min_length":
            command.extend([arg_mapping[arg], str(value)])

    subprocess.call(command)

def main():
    # Parser for arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-MediaDir", 
                        help="Specify the root media directory", 
                        required=True, 
                        type=lambda x: is_valid_directory(parser, x))
    parser.add_argument("-TargetDir", 
                        help="Specify the root target directory", 
                        required=True, 
                        type=lambda x: is_valid_directory(parser, x))
    parser.add_argument("-os", 
                        help="Specify the operating system type", 
                        choices=["mac", "linux", "both"], 
                        default="linux")
    parser.add_argument("-portrait", 
                        help="Specify the portrait filter", 
                        action='store_true')
    parser.add_argument("-horizontal", 
                        help="Specify the horizontal filter", 
                        action='store_true')
    parser.add_argument("-min_length", 
                        help="Specify the minimum length filter", 
                        type=float)
    parser.add_argument("-max_length", 
                        help="Specify the maximum length filter", 
                        type=float)
    
    # Parse arguments
    args = parser.parse_args()

    # Checks for git and Barcarolle-Playlist-Generator.py
    check_for_git()
    check_for_barcarolle_script()
    
    # Operative Systems
    OSs = ["mac", "linux"] if args.os == "both" else [args.os]
    for dirpath, dirs, files in os.walk(args.MediaDir):
        for OS in OSs:
            structure = os.path.join(args.TargetDir, OS, os.path.relpath(dirpath, args.MediaDir))

            # If the structure doesn't exist, create it
            if not os.path.isdir(structure):
                os.makedirs(structure)

            print(f"Creating {OS} folder: {structure}")
            call_playlist_generator(dirpath, structure, 
                                    portrait=args.portrait, 
                                    horizontal=args.horizontal,
                                    min_length=args.min_length, 
                                    max_length=args.max_length)

if __name__ == "__main__":
    main()
