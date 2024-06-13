# vinyl2youtube
Generates videos from audio files using ffmpeg!

# Setup
Download supported Python version (I've only used it with Python 3.8.10, use with earlier versions with own risk!)

Install the python requirements
```
$ pip3 install -r requirements.txt
```

# How to Run
`VinylRip` usage:
`usage: rip.py [-h] root_dir [output_dir]`
By default `output_dir` is `./output`. Outputs are organized and dated.

```
# Generates videos for all files in subfolders
$ python3 rip.py /home/user/Music
# Generates videos and sends output to ./awesomeoutput
$ python3 rip.py /home/user/Music ./awesomeoutput
```

# Current qualms
- PNG images are only supported for the videos
- Only audio files in subfolders work (no recursive support, I think)
- PNG images that are an odd sized length or width fail ffmpeg

# Future Plans
- Print out error if failed command
