import os
import subprocess
import soundfile
import math
import glob
import argparse
from pathlib import Path

class ValidatePath(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not os.path.exists(values):
            raise argparse.ArgumentError(self, f"Path does not exist: {values}")
        setattr(namespace, self.dest, values)

def main():
    parser = argparse.ArgumentParser(description="Generate videos from folders")
    parser.add_argument("root_dir", help="Root directory", action=ValidatePath)

    args = parser.parse_args()
    print(Path(args.root_dir).resolve())
    print("Hello world!")
    completed_dirs = []
    with open("completed.txt", "r") as file:
        completed_dirs = [ line.strip() for line in file.readlines() ]
    print(completed_dirs)
    # TODO: Add argument for the root folder
    # TODO: Loop through each subdir in the root folder, find WAVs, create video for each and spit out to the output directory that is dated
    # TODO: If all WAVs are successful, add it to the completed text
    # TODO: Ignore the completed dirs in the txt file
    # TODO: Automate upload to YouTube? is that a thing lol

def generate_video(song_path, out_path):
    # cmd = ffmpeg -framerate 1/(length of track / number of the images) -i Front.png -i J-Majik\ -\ Shiatsu.wav -c:v libx264 -r 30 -pix_fmt yuv420p -shortest Shiatsu.mp4
    pass

def gen_cmd(song_path, files_path, out_path):
    song_length = math.ceil(get_length_of_audio_in_seconds(song_path))
    # TODO: Accept more than just jpg, python globbing sucks with multiple options
    images = glob.glob(f"{files_path}/*.jpg")
    num_images = len(images)
    if num_images == 0:
        raise Exception(f"No images found in dir '{files_path}', quitting.")
    seconds_per_image = math.ceil(song_length / num_images)
    cmd = f"ffmpeg -framerate 1/{seconds_per_image} -pattern_type glob -i {files_path}*.jpg -i {song_path} -c:v libx264 -r 15 -pix_fmt yuv420p -shortest {out_path}"
    print(cmd)

def get_length_of_audio_in_seconds(song_path):
    if not os.path.exists:
        raise Exception(f"File at path: '{song_path}' not found")
    f = soundfile.SoundFile(song_path)
    seconds = f.frames / f.samplerate
    return seconds

main()