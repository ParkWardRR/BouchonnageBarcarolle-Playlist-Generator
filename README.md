# BouchonnageBarcarolle-Playlist-Generator

A Python-based media file processor that curates playlists from a pool of files. The program provides a variety of filtering options and is compatible with various Linux distributions such as Ubuntu, Fedora, Debian, and CentOS as well as with its original platform, Alma Linux. 

## Table of Contents

- Getting Started
- Prerequisites
- How to Install
- Running the Scripts
- Contributing
- License

## Getting Started

These instructions will get you a copy of *BouchonnageBarcarolle-Playlist-Generator* up and running on your local machine for development and testing purposes.

## Prerequisites

The script has dependencies on the following packages, which it automatically checks for and installs if not present:

- pip
- ffmpeg
- ffprobe
- ffmpeg-python

Any Linux OS, especially like Alma Linux (Version 9/8), Ubuntu, Fedora, Debian, or CentOS, is required to have these packages for the successful execution of the script. 

## How to Install

1. Clone the repository to your local machine:

```bash
git clone git@github.com:ParkWardRR/BouchonnageBarcarolle-Playlist-Generator.git
```

2. Navigate into the cloned repository:

```bash
cd BouchonnageBarcarolle-Playlist-Generator
```

3. To install *BouchonnageBarcarolle-Playlist-Generator* required packages, run:

```bash
pip install -r requirements.txt
```

## Running the Scripts

You can run the script using the command below:

```bash
python3 BouchonnageBarcarolle-Playlist-Generator.py -dir <directory> -mount <mount-directory> -autoplst <yes/no> -shuffle <yes/no> -output <output-folder> -overwrite -portrait/horz -min_length <minimum length in seconds> -max_length <maximum length in seconds> -filename <filename>
```

Replace the bracketed sections with parameters relevant to your desired output.

## Flags

The tool provides a number of command line arguments or flags to customize the behavior of the script. Here are their descriptions:

| Flag | Description |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| -dir | Directory from which you want to scan media files on the server. **(required)** |
| -mount | The root of the directory on the client corresponding to `-dir`. |
| -autoplst | If you want to autogenerate a playlist name, set `-autoplst` to `yes`. Otherwise, set it to `no` (default setting is `no`). |
| -shuffle | If you want to shuffle the playlist, set `-shuffle` to `yes`. Otherwise, set it to `no` (default setting is `no`). |
| -output | Specify an output directory for the playlist file. **(required)** |
| -overwrite | If you want to overwrite an existing file, provide this flag. |
| -portrait | If you only want to include vertical videos, provide this flag. |
| -horz | If you only want to include horizontal videos, provide this flag. |
| -min_length | To specify a minimum length for a video in seconds. Videos shorter than this will be excluded. |
| -max_length | To specify a maximum length for a video in seconds. Videos longer than this will be excluded. |
| -filename | Specify a filename for the playlist file. |

Example command with some flags:

```bash
python3 BouchonnageBarcarolle-Playlist-Generator.py -dir /path/to/your/media/files -mount /path/on/client -autoplst yes -shuffle yes -output /path/to/output/folder -overwrite -portrait -min_length 30 -max_length 600 -filename my_playlist
```

## Contributing

We welcome contributions of all kinds to *BouchonnageBarcarolle-Playlist-Generator*. Whether you're improving the existing code, adding new functionality, or even fixing a typo, we appreciate your help!

Remember, this is an open-source project, so please interact with respect and assume good intentions. If you're unsure HOW to contribute to open-source code, DO reach out — we'd love to help you learn.

## License

*BouchonnageBarcarolle-Playlist-Generator* is licensed under the MIT License. See `LICENSE` for more information.
