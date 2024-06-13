# mvgenerator
Generates videos from audio files using ffmpeg!

# Setup
**Python=3.8.10**

(I've only used it with Python 3.8.10, use with earlier versions with own risk!)

Install the Python requirements
```
$ pip3 install -r requirements.txt
```

# How to Run
`mvgenerator` usage:

`usage: mvgenerator.py [-h] root_dir [output_dir]`
By default `output_dir` is `./output`. Outputs are organized and dated.

```
# Generates videos for all files in subfolders
$ python3 mvgenerator.py /home/user/Music
# Generates videos and sends output to ./awesomeoutput
$ python3 mvgenerator.py /home/user/Music ./awesomeoutput
```

# Current qualms
- PNG images are only supported for the videos
- Only audio files in subfolders work (no recursive support, I think)
- PNG images that are an odd sized length or width fail ffmpeg

# Future Plans
- Print out error if failed command
