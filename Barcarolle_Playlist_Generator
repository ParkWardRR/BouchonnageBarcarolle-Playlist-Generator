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

[The rest of your script remains unchanged]

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
