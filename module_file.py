import os


async def save_file(file, upload_folder):
    os.makedirs(upload_folder, exist_ok=True)  # Create folder if it does not exist

    file_path = os.path.join(upload_folder, file.filename)  # Form the full path for the file

    # Save file
    with open(file_path, "wb") as f:
        f.write(await file.read())

    return file_path
