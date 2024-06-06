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

    completed_dirs = []
    with open("completed.txt", "r") as file:
        completed_dirs = [ line.strip() for line in file.readlines() ]
    # print(completed_dirs)
    # generate_video("sample3.wav", ".", "newfile.mp4")

    # TODO: Use pathlib
    dirs_in_root = [directory for directory in os.listdir(args.root_dir) if os.path.isdir(args.root_dir + "/" + directory)]
    dirs_to_loop = [directory for directory in dirs_in_root if directory not in completed_dirs]
    print(dirs_to_loop)
    # TODO: Loop through each subdir in the root folder, find WAVs, create video for each and spit out to the output directory that is dated
    for directory in dirs_to_loop:
        music_files = [f for f in os.listdir(f"{args.root_dir}/{directory}") if f.endswith(".wav")]
        for song in music_files:
            generate_video(f"{args.root_dir}/{directory}/{song}", f"{args.root_dir}/{directory}", song.strip(".wav"))
        # TODO: If all WAVs are successful, add it to the completed text
        with open("completed.txt", "a") as f:
            f.write(directory + "\n")

    # TODO: Ignore the completed dirs in the txt file
    # TODO: Automate upload to YouTube? is that a thing lol

def generate_video(song_path, files_path, out_path):
    # cmd = ffmpeg -framerate 1/(length of track / number of the images) -i Front.png -i J-Majik\ -\ Shiatsu.wav -c:v libx264 -r 30 -pix_fmt yuv420p -shortest Shiatsu.mp4
    try:
        cmd = gen_cmd(song_path, files_path, out_path)
        print(cmd)
    except Exception as e:
        print(e)
    # subprocess.run(cmd.split(" "))
    pass

def gen_cmd(song_path, files_path, out_path):
    song_length = math.ceil(get_length_of_audio_in_seconds(song_path))
    # TODO: Accept more than just png, python globbing sucks with multiple options
    images = glob.glob(f"{files_path}/*.png")
    num_images = len(images)
    if num_images == 0:
        raise Exception(f"No images found in dir '{files_path}', quitting.")
    seconds_per_image = math.ceil(song_length / num_images)
    cmd = f"ffmpeg -framerate 1/{seconds_per_image} -pattern_type glob -i *.png -i {song_path} -c:v libx264 -r 15 -pix_fmt yuv420p -shortest {out_path}"
    return cmd

def get_length_of_audio_in_seconds(song_path):
    if not os.path.exists:
        raise Exception(f"File at path: '{song_path}' not found")
    f = soundfile.SoundFile(song_path)
    seconds = f.frames / f.samplerate
    return seconds

main()