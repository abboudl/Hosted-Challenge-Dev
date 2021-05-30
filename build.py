#!/usr/bin/env python3

import re
import sys
import yaml
import shutil
import os
from os.path import basename, normpath
from zipfile import ZipFile

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


# credits: @TheMatt2
def walklevel(path, depth=1):
    """It works just like os.walk, but you can pass it a level parameter
     that indicates how deep the recursion will go.
     If depth is 1, the current directory is listed.
     If depth is 0, nothing is returned.
     If depth is -1 (or less than 0), the full depth is walked.
    """

    if depth < 0:
        for root, dirs, files in os.walk(path):
            yield root, dirs[:], files
        return
    elif depth == 0:
        return

    base_depth = path.rstrip(os.path.sep).count(os.path.sep)
    for root, dirs, files in os.walk(path):
        yield root, dirs[:], files
        cur_depth = root.count(os.path.sep)
        if base_depth + depth <= cur_depth:
            del dirs[:]


def zip_directory(zip_filename, directory):
    with ZipFile(zip_filename, 'w') as zipObj:
        for folderName, subfolders, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(folderName, filename)
                zipObj.write(file_path, basename(file_path))


def build_challenge(root):

    root = normpath(root)
    challenge_key = basename(root)
    player_files_dir = f"{root}/player_files/"
    player_files_zip_current = f"./{challenge_key}.zip"
    player_files_zip_from_root = f"{root}/{challenge_key}.zip"
    instructions_file = f"{root}/documentation/instructions.txt"
    hint_file = f"{root}/documentation/hint.txt"
    manifest_file = f"{root}/documentation/manifest.yml"
    challenge_dot_yaml_file = f"{root}/challenge.yml"

    print(f"\n>>>Preparing {root} for deployment to CTFd<<<")

    if os.path.exists(manifest_file):
        try:
            print("INFO: reading manifest file.")
            manifest = yaml.load(open(manifest_file), Loader=Loader)["challenge"]
        except (yaml.YAMLError, KeyError):
            print(f"ERROR: Encountered a YAML parsing error when parsing {manifest_file}.")
            raise
    else:
        print(f"ERROR: No manifest file found in {root}.")
        raise

    if os.path.exists(instructions_file):
        try:
            print("INFO: reading instructions.txt file.")
            instructions = open(instructions_file).read().replace("\n", "<br>")
        except OSError:
            print(f"ERROR: Error reading: {instructions_file}.")
            raise
        print("INFO: Adding content of instructions.txt to challenge metadata.")
        manifest.update({"description": instructions})
    else:
        print(f"ERROR: No instructions file found in the {root}/documentation/ directory.")
        raise

    if os.path.exists(hint_file):
        hint = None
        try:
            print("INFO: reading hint.txt file.")
            hint = open(hint_file).read().replace("\n", "<br>")
        except OSError:
            print(f"ERROR: Error reading: {hint_file}.")
        hint_cost = manifest.get("hint_cost", None)
        if hint_cost is not None:
            print("INFO: Adding content of hint.txt to challenge metadata.")
            manifest.update({"hints": [{"content": hint, "cost": manifest["hint_cost"]}]})
            manifest.pop("hint_cost", None)
        else:
            print(f"ERROR: No hint_cost specified even though a hint file was found in the"
                    f" {root}/documentation/ directory.")
            raise

    if os.path.exists(player_files_dir):
        print("INFO: Copying instructions.txt file into player_files directory.")
        shutil.copy(src=instructions_file, dst=player_files_dir)
        print(f"INFO: Zipping player_files directory into {player_files_zip_from_root}.")
        zip_directory(zip_filename=player_files_zip_from_root, directory=player_files_dir)
        print("INFO: Adding player files archive location to challenge metadata.")
        manifest.update({"files": [player_files_zip_from_root]})
    else:
        print(f"INFO: No player_files directory found for {challenge_key}.")

    stream = None
    try:
        stream = open(challenge_dot_yaml_file, "w")
    except OSError:
        print(f"ERROR: error creating/writing to {challenge_dot_yaml_file}.")
        raise

    try:
        print("INFO: Dumping challenge metadata into CTFd challenge.yml file.")
        yaml.dump(manifest, stream)
    except yaml.YAMLError:
        print("ERROR: An error occurred while dumping the challenge.yml file.")
        raise

def get(ll, index):
    try:
        return ll[index]
    except IndexError:
        return None


def run():

    if get(sys.argv, 1)  == "make":

        print(f">>>Starting Build Process<<<")
        
        try:
            if get(sys.argv, 2):
                build_challenge(sys.argv[2])
            else:
                print("ERROR: You must provide a path to the challenge directory you wish to build.")
        except:
            print("ERROR: An error has occurred.")

    elif get(sys.argv, 1) == "--all" or get(sys.argv, 1) == "-a":

        print(f">>>Starting Build Process<<<")

        pattern = re.compile(r'^\./[^.][^/]+/[^/]+$')
        for root, dirs, files in walklevel(path=".", depth=2):
            if pattern.match(root):
                try:
                    build_challenge(root)
                except:
                    continue

    else:
        print("\nUSAGE:")
        print("\n  OPTION #1: Prepare a single challenge for deployment to CTFd.")
        print("  build.py make [challenge_directory]")
        print("\n  OPTION #2: Prepare all challenge for deployment to CTFd.")
        print("  build.py [--all|-a]\n")
      

if __name__ == '__main__':
    run()
