import argparse
import json
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog="Validator",
                    description="Validates that the length of stations.json matches the length of the data")
    parser.add_argument("directory")
    parser.add_argument("multiplier", type=int)
    args = parser.parse_args()
    print(args.directory, args.multiplier)
    subdirs = [i for i in os.listdir(args.directory) if os.path.isdir(args.directory)]
    files = [i for i in os.listdir(args.directory) if not os.path.isdir(args.directory)]
    file_count = len(files)
    stations_file = os.path.join(args.directory, "stations.json")
    if os.path.exists(stations_file):
        with open(stations_file, "r") as f:
            stations_raw = f.read()
        stations = json.loads(stations_raw)
        if len(stations) != file_count * args.multiplier:
            print(f"Subdir {args.directory} failed validation.") 
    for subdir in subdirs:
        full_dir_path = os.path.join(args.directory, subdir)
        stations_file = os.path.join(full_dir_path, "stations.json")
        file_count = len(os.listdir(full_dir_path)) - 1
        if os.path.exists(stations_file):
            with open(stations_file, "r") as f:
                stations_raw = f.read()
            stations = json.loads(stations_raw)
            expected_length = len(stations) * args.multiplier
            if file_count != expected_length:
                print(f"Subdir {full_dir_path} failed validation: {file_count} {expected_length}.")
