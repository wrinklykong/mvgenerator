import os
import subprocess
import soundfile
import math
import glob
import argparse
import datetime

from pathlib import Path
from tempfile import NamedTemporaryFile


COMMANDS = ["album", "single"]


class ValidatePath(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        path_to_val=Path(values)
        if not ( path_exists(path_to_val) ):
            raise argparse.ArgumentError(self, f"Path does not exist: {values}")
        setattr(namespace, self.dest, values)


def main():
    # CLI arguments
    parser = argparse.ArgumentParser(description="Generate videos from folders")
    parser.add_argument("root_dir", help="Root directory", action=ValidatePath)
    parser.add_argument("output_dir", help="Directory for outputs", nargs="?", default="./output", action=ValidatePath)
    parser.add_argument("cmd", help="Command to run", choices=COMMANDS)
    args = parser.parse_args()

    # Path vars
    cur_dir=Path(".")
    root_dir=Path(args.root_dir)
    output_dir=Path(args.output_dir)

    # Grab completed song files from completed.txt
    completed_songs = []
    with open("completed.txt", "r") as file:
        completed_songs = [ line.strip() for line in file.readlines() ]
    dirs_to_check = [directory for directory in root_dir.iterdir() if directory.is_dir()]
    if not dirs_to_check:
        dirs_to_check = [root_dir]
    all_songs = []
    for directory in dirs_to_check:
        # TODO: Flac/mp3 support and stuff
        for song in Path(directory).glob("*.wav"):
            all_songs.append(song)
        for song in Path(directory).glob("*.flac"):
            all_songs.append(song)
    songs_to_generate = [song for song in all_songs if str(song) not in completed_songs]

    # May need to look at tagging?
    songs_to_generate.sort()
    # Grab number of songs being generated for future use
    num_songs = len(songs_to_generate)
    if num_songs <= 0:
        print("No songs in folder needing to be generated, quitting")
        return
    num_successful = num_songs
    failed_songs = []

    # Create the output directory
    directory_output_dir = output_dir / Path(get_current_date_and_time())
    os.mkdir(directory_output_dir)

    if args.cmd == 'single':
        # Generate all videos
        with open("completed.txt", "a") as f:
            for song in songs_to_generate:
                path = str(song)
                if "/" in path:
                    path = path[:path.rfind("/")]
                try:
                    print(f"-> Creating video for '{str(song)}'")
                    generate_video(song, path, directory_output_dir / Path(str(song).strip(".wav") + ".mp4").name)  # lol
                    f.write(str(song)+"\n")
                except Exception as e:
                    num_successful -= 1
                    print("-!! ERROR: "+str(e))
        
        # Print results
        print("\n-----RESULTS-----")
        print(f"-> Number of files processed: {num_songs}")
        print(f"-> Success rate: {num_successful} / {num_songs}")
        if num_successful > 0:
            print(f"-> Results located at {str(directory_output_dir)}")
        else:
            os.rmdir(directory_output_dir)
        print("\n")
        # TODO: Automate upload to YouTube? is that a thing lol
    if args.cmd == 'album':
        # Normalize the audio first...
        shell_supported = args.root_dir.strip('/').replace(' ', '\\ ')
        cmd = f"normalize-audio -b {shell_supported}/*.flac"
        print(f"[+]  Running command: \"{cmd}\"")
        output = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, shell=True)
        # Generate a concat temp file to generate a single audio file
        combined_path = Path("combined_audio.flac").absolute()
        # Timestamp stuff
        timestamp_info = []
        time_in_seconds = 0
        timestamp_path = directory_output_dir / "timestamp.txt"

        if combined_path.exists():
            os.unlink(combined_path)
        with NamedTemporaryFile() as f:
            contents = []
            for song in songs_to_generate:
                sanitized_filename = str(Path.cwd() / song).replace("'", "'\\''")
                contents.append(f"file '{sanitized_filename}'")
                song_length = get_length_of_audio_in_seconds(song)
                timestamp_info.append(f"{readable_seconds(math.ceil(time_in_seconds))} - {Path(song).name}")
                time_in_seconds += song_length
            f.write('\n'.join(contents).encode())
            f.flush()
            # We combine everything together...
            cmd = f"ffmpeg -f concat -safe 0 -i {f.name} -c:a flac {combined_path}"
            print(f"[+]  Running command: \"{cmd}\"")
            output = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, shell=True)
            print(output.stderr)
        # output path = directory_output_dir / Path(args.root_dir).name + ".mp4"
        output_filename = Path(args.root_dir).name + ".mp4"

        generate_video(str(combined_path), args.root_dir, directory_output_dir / output_filename)  # lol
        with open(timestamp_path, "w") as f:
            f.write('\n'.join(timestamp_info))
        print(f"[+]  Success! Video output at path: {directory_output_dir / output_filename}")

def generate_video(song_path, files_path, out_path):
    # cmd = ffmpeg -framerate 1/(length of track / number of the images) -i Front.png -i J-Majik\ -\ Shiatsu.wav -c:v
    #  libx264 -r 30 -pix_fmt yuv420p -shortest Shiatsu.mp4
    cmd = gen_cmd(song_path, files_path, out_path)
    print(f"[+]  Running command: \"{cmd}\"")
    output = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, shell=True)

def gen_cmd(song_path, files_path, out_path):
    shell_supported = files_path.strip('/').replace(' ', '\\ ')
    song_length = math.ceil(get_length_of_audio_in_seconds(song_path))
    # TODO: Accept more than just png, python globbing sucks with multiple options
    jpeg_glob = f"{files_path.strip('/')}/*.jpeg"
    images = glob.glob(jpeg_glob)
    num_images = len(images)
    if num_images == 0:
        raise Exception(f"No images found in dir '{files_path}', skipping.")
    seconds_per_image = math.ceil(song_length / num_images)
    cmd = f'ffmpeg -y -framerate 1/{seconds_per_image} -pattern_type glob -i {shell_supported.strip("/")}/*.jpeg -i \"{song_path}\" ' \
          f'-c:v libx264 -r 15 -tune stillimage -preset ultrafast -pix_fmt yuv420p -shortest \"{out_path}\"'
    return cmd

def get_length_of_audio_in_seconds(song_path):
    if not os.path.exists:
        raise Exception(f"File at path: '{song_path}' not found")
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

def readable_seconds(seconds):
    s_seconds = str(seconds%60)
    return f'{seconds//60}:{"0"*(2-len(s_seconds))}{s_seconds}'

main()