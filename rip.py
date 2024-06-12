import os
import subprocess
import soundfile
import math
import glob
import argparse
from pathlib import Path
import datetime


class ValidatePath(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        path_to_val=Path(values)
        if not ( path_exists(path_to_val) ):
            raise argparse.ArgumentError(self, f"Path does not exist: {values}")
        setattr(namespace, self.dest, values)


def main():
    parser = argparse.ArgumentParser(description="Generate videos from folders")
    parser.add_argument("root_dir", help="Root directory", action=ValidatePath)
    parser.add_argument("output_dir", help="Directory for outputs", nargs="?", default="./output", action=ValidatePath)
    args = parser.parse_args()

    # Path vars
    cur_dir=Path(".")
    root_dir=Path(args.root_dir)
    output_dir=Path(args.output_dir)

    # Grab completed song files from completed.txt
    completed_songs = []
    with open("completed.txt", "r") as file:
        completed_songs = [ line.strip() for line in file.readlines() ]
    dirs_in_root = [directory for directory in root_dir.iterdir() if directory.is_dir()]
    all_songs = []
    for directory in dirs_in_root:
        # TODO: Flac/mp3 support and stuff
        for song in Path(directory).glob("*.wav"):
            all_songs.append(song)
    songs_to_generate = [song for song in all_songs if str(song) not in completed_songs]
    
    num_songs = len(songs_to_generate)
    if num_songs <= 0:
        print("No songs in folder needing to be generated, quitting")
        return
    num_successful = num_songs
    failed_songs = []

    # TODO: Enum all in directory and show progress
    directory_output_dir = output_dir / Path(get_current_date_and_time())
    os.mkdir(directory_output_dir)

    with open("completed.txt", "a") as f:
        for song in songs_to_generate:
            path = str(song)
            if "/" in path:
                path = path[:path.rfind("/")]
            try:
                generate_video(song, path, directory_output_dir / Path(str(song).strip(".wav") + ".mp4").name)  # lol
                f.write(str(song)+"\n")
            except Exception as e:
                num_successful -= 1
                print(str(e))
    
    print("-----RESULTS-----")
    print(f"-> Number of files processed: {num_songs}")
    print(f"-> Success rate: {num_successful} / {num_songs}")
    if num_successful > 0:
        print(f"-> Results located at {str(directory_output_dir)}")
    else:
        os.rmdir(directory_output_dir)
    print("\n")
    # TODO: Automate upload to YouTube? is that a thing lol

def generate_video(song_path, files_path, out_path):
    # cmd = ffmpeg -framerate 1/(length of track / number of the images) -i Front.png -i J-Majik\ -\ Shiatsu.wav -c:v
    #  libx264 -r 30 -pix_fmt yuv420p -shortest Shiatsu.mp4
    cmd = gen_cmd(song_path, files_path, out_path)
    output = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, shell=True)

def gen_cmd(song_path, files_path, out_path):
    song_length = math.ceil(get_length_of_audio_in_seconds(song_path))
    # TODO: Accept more than just png, python globbing sucks with multiple options
    images_glob = f"{files_path}/*.png"
    images = glob.glob(images_glob)
    num_images = len(images)
    if num_images == 0:
        raise Exception(f"No png images found in dir '{files_path}', skipping.")
    seconds_per_image = math.ceil(song_length / num_images)
    # Quotes being eaten for some reason
    cmd = f'ffmpeg -y -framerate 1/{seconds_per_image} -pattern_type glob -i \"{images_glob}\" -i \"{song_path}\" ' \
          f'-c:v libx264 -r 15 -tune stillimage -preset ultrafast -pix_fmt yuv420p -shortest \"{out_path}\"'
    print(cmd)
    return cmd

def get_length_of_audio_in_seconds(song_path):
    if not os.path.exists:
        raise Exception(f"File at path: '{song_path}' not found")
    # This fails, change dir
    f = soundfile.SoundFile(song_path)
    seconds = f.frames / f.samplerate
    return seconds

def get_current_date_and_time():
    date = str(datetime.datetime.now())
    date = date.replace(" ", "-")
    date = date.replace(":", "_")
    return date

def path_exists(path):
    return ( path.exists() and path.is_dir() )

main()