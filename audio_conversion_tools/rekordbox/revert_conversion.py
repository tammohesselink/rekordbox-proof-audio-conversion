import csv
import os
import shutil

import typer


def restore_files_from_csv(
    archive_csv_path: str = typer.Option(...),
):
    with open(archive_csv_path, newline="") as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            if len(row) >= 2:
                source_file = row[2]  # Get the source path (archive location)
                destination_file = row[1]  # Get the destination path (original location)

                # Check if the source file exists and is in the archive folder
                if os.path.exists(source_file):
                    # Move the file from the archive to the original location
                    shutil.move(source_file, destination_file)
                    print(f"Restored '{os.path.basename(destination_file)}' from archive.")


def main():
    typer.run(restore_files_from_csv)
