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
    # parser.add_argument("output_dir", help="Directory for outputs", action=ValidatePath)
    args = parser.parse_args()

    cur_dir=os.curdir
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
        full_dir_path = f"{args.root_dir}/{directory}"
        # os.chdir(full_dir_path)
        music_files = [f for f in os.listdir(full_dir_path) if f.endswith(".wav")]
        for song in music_files:
            # TODO: Use output_dir
            generate_video(f"{args.root_dir}{directory}/{song}", full_dir_path, f"./{song}.mp4")
        # TODO: If all WAVs are successful, add it to the completed text
        with open("completed.txt", "a") as f:
            print("help")
            f.write(directory + "\n")

    # TODO: Ignore the completed dirs in the txt file
    # TODO: Automate upload to YouTube? is that a thing lol

def generate_video(song_path, files_path, out_path):
    # cmd = ffmpeg -framerate 1/(length of track / number of the images) -i Front.png -i J-Majik\ -\ Shiatsu.wav -c:v libx264 -r 30 -pix_fmt yuv420p -shortest Shiatsu.mp4
    try:
        cmd = gen_cmd(song_path, files_path, out_path)
        results = subprocess.run(cmd.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(results.stderr)
        print("cmd ran")
    except Exception as e:
        print(e)
        pass

def gen_cmd(song_path, files_path, out_path):
    song_length = math.ceil(get_length_of_audio_in_seconds(song_path))
    # TODO: Accept more than just png, python globbing sucks with multiple options
    images_glob = f"{files_path}/*.png"
    images = glob.glob(images_glob)
    num_images = len(images)
    if num_images == 0:
        raise Exception(f"No images found in dir '{files_path}', quitting.")
    seconds_per_image = math.ceil(song_length / num_images)
    # Quotes being eaten for some reason
    cmd = f"ffmpeg -framerate 1/{seconds_per_image} -pattern_type glob -i \"{images_glob}\" -i \"{song_path}\" -c:v libx264 -r 15 -tune stillimage -preset ultrafast -pix_fmt yuv420p -shortest \"{out_path}\""
    print(cmd)
    return cmd

def get_length_of_audio_in_seconds(song_path):
    if not os.path.exists:
        raise Exception(f"File at path: '{song_path}' not found")
    f = soundfile.SoundFile(song_path)
    seconds = f.frames / f.samplerate
    return seconds

main()