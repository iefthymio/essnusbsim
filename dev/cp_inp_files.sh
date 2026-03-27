#!/bin/bash
#
# Copy generated .inp files to fluka directory
# Delete .flair files if exist

# Check for correct number of arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 file_list.txt destination_directory"
    exit 1
fi

# Assign arguments to variables
file_list=$1
destination_directory=$2

# Check if file_list exists
if [ ! -f "$file_list" ]; then
    echo "Error: File list '$file_list' does not exist."
    exit 1
fi

# Check if destination directory exists
if [ ! -d "$destination_directory" ]; then
    echo "Error: Destination directory '$destination_directory' does not exist."
    exit 1
fi

# Loop through each file in the file list
while IFS= read -r file; do
    # Skip empty lines or lines with only whitespace
    if [[ -z "$file" ]]; then
        continue
    fi


    # Get the base name of the file (without directory and extension)
    base_name=$(basename "$file" | sed 's/\.[^.]*$//')

    # Find and delete all files in the destination directory with the same base name
    echo "Removing files with base name '$base_name' in $destination_directory"
    find "$destination_directory" -type f -name "$base_name.inp" -exec rm {} \;
    find "$destination_directory" -type f -name "$base_name.flair" -exec rm {} \;

    # Copy the file to the destination directory
    if [ -e "$file" ]; then
        echo "Copying $file to $destination_directory"
        cp "$file" "$destination_directory"
    else
        echo "Warning: File '$file' not found, skipping."
    fi
done < "$file_list"

echo "File copy operation completed."