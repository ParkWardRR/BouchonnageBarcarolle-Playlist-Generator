#!/usr/bin/env python3
# Manato_Cascading_Folder_Playlist_Generator.py

"""
============
Description
============
1. PYTHON 3 script reads a YAML configuration file and generates m3u8 playlists based on each subdirectory.
2. .m3u8 playlist files are generated for each subdirectory with names matching the parent directory.
3. Also supports creating mounting points for playlist paths for Linux, MacOS, and Windows.
4. Generates 7z archives of the output directory.
5. Utilizes Barcarolle_Playlist_Generator functionality.

===============
How to execute
===============
1. python Manato_Cascading_Folder_Playlist_Generator.py -config /path/to/config.yaml
2. (To generate a sample config file:) python Manato_Cascading_Folder_Playlist_Generator.py -generate_sample_config /path/to/sample_config.yaml

======
Params
======
| parameter                  | Description                                                      |
|----------------------------|------------------------------------------------------------------|
| '-config'                  | Path to the YAML configuration file                              |
| '-generate_sample_config'  | Generate a sample YAML configuration file.                       |

Note: All filtering parameters are to be provided in the YAML configuration file. If the output directory is not provided, it will default to the script's directory.
"""

import os
import argparse
import pkg_resources
from datetime import datetime
from pathlib import Path
REQUIRED_PACKAGES = [
    'pyyaml',
    'py7zr'
]

try:
    pkg_resources.require(REQUIRED_PACKAGES)
except pkg_resources.DistributionNotFound as e:
    print("Missing required package: ", e)
    print("Please install by running the command: pip install ", ' '.join(REQUIRED_PACKAGES))
    exit(1)

import yaml
from Barcarolle_Playlist_Generator import is_valid_file, validate_length, scan_directory, generate_output_folder, \
    generate_filters_flag, main as barcarolle_main, VIDEO_EXTENSIONS
import py7zr

def main(config_file):
    # Load parameters from YAML configuration file
    with open(config_file, 'r') as f:
        try:
            config = yaml.safe_load(f)

            # Set current script's directory if output_dir not provided in YAML file
            if 'output_dir' not in config or not config['output_dir']:
                config['output_dir'] = os.getcwd()

            # Run the barcarolle script to generate a playlist for each subdirectory
            for directory in config['dirs']:
                for subdir in os.scandir(directory):
                    if subdir.is_dir():
                        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                        config['dir'] = subdir.path
                        config['output_folder'] = Path(config['output_dir'], subdir.name + '-' + timestamp)     # Appending time stamp to output folder

                        # Checks and creates output directories if they don't exist
                        os.makedirs(config['output_folder'], exist_ok=True)

                        for os_type, os_mount in zip(config['os_types'], config['os_mounts']):
                            config['mount'] = os_mount
                            
                            # Defaulting fields if they are missing in config
                            config['portrait_only'] = config.get('portrait_only', False)
                            config['horz_only'] = config.get('horz_only', False)
                            config['min_length'] = config.get('min_length', None)
                            config['max_length'] = config.get('max_length', None)
                            config['shuffle_playlist'] = config.get('shuffle_playlist', 'no')  # defaulting to 'no' if missing
                            config_namespace = argparse.Namespace(**config)

                        
                            barcarolle_main(config_namespace)  # instead of barcarolle_main(config)

                            archive_name = f"{subdir.name}-{os_type}-{timestamp}.7z"
                            archive_path = os.path.join(config['output_folder'], archive_name)

                            # Archive creation
                            with py7zr.SevenZipFile(archive_path, mode='w') as archive:
                                archive.writeall(config['output_folder'], arcname="/")
                            print(f".7z Archive created: {archive_path}")

        except yaml.YAMLError as err:
            print(err)


def generate_sample_yaml_file(config_file):
    # Generate a sample YAML configuration file with default values
    print("Generating configuration file...")
    try:
        data = {
            'dirs': ['/path/to/dir1', '/path/to/dir2'],
            'output_dir': '/output',
            'os_types': ['linux', 'macos', 'win'],
            'os_mounts': ['/linux/mount/point', '/macos/mount/point', '/win/mount/point'],
            'min_length': 30,
            'max_length': 300,
            'auto_gen_playlist': 'yes',
            'shuffle_playlist': 'yes',
            'portrait_only': False,
            'horz_only': False,
            'zip_output': 'yes'
            
        
        }

        with open(config_file, 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False)
        print(f"Configuration file generated at: {config_file}")
    except Exception as e:
        print(f"An error occurred during sample configuration file generation: {e}")

# the function you import from another module
def is_valid_file(parser, x):
    if not os.path.isfile(x):
        parser.error("The file %s does not exist!" % x)
    else:
        return x

if __name__ == '__main__':
    print("Running script...")
    parser = argparse.ArgumentParser(description="Manato_Playlist_Generator. Provide a YAML config file or generate a sample one.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-config', dest="config_file", type=lambda x: is_valid_file(parser, x), help="Path to the YAML configuration file (required).")
    group.add_argument('-generate_sample_config', dest="sample_config_file", nargs='?', const='Manato_Cascading_Folder_Playlist_Generator.config.yaml', help="Generate a sample YAML configuration file.")
    args = parser.parse_args()

    if args.config_file:
        print("Running main function...")
        main(args.config_file)
    else:
        generate_sample_yaml_file(args.sample_config_file if args.sample_config_file else 'Manato_Cascading_Folder_Playlist_Generator.config.yaml')
