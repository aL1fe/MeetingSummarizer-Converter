from fastapi import FastAPI, UploadFile
import ffmpeg
import os

app = FastAPI()


def convert_to_mp3(input_file, output_file):
    (
        ffmpeg
        .input(input_file)
        .output(output_file, format='mp3')
        .overwrite_output()  # Overwrite file if exist
        .run()
    )


async def save_file(file: UploadFile) -> str:
    # Create folder if it does not exist
    upload_folder: str = "incoming_files"
    os.makedirs(upload_folder, exist_ok=True)

    # Form the full path for the file
    file_path = os.path.join(upload_folder, file.filename)

    # Save file
    with open(file_path, "wb") as f:
        f.write(await file.read())

    return file_path


@app.post("/convert/")
async def upload_file(file: UploadFile):
    try:
        # Save received file to the incoming files folder
        input_file_path = await save_file(file)

        # Create folder for converted files if it does not exist
        converted_folder = "converted_files"
        os.makedirs(converted_folder, exist_ok=True)

        # Separate the file name and its extension
        filename, _ = os.path.splitext(file.filename)

        # Create filename for converted file
        converted_filename = f"{filename}.mp3"

        converted_file_path = os.path.join(converted_folder, converted_filename)

        convert_to_mp3(input_file_path, converted_file_path)

        return {"Ok"}
    except Exception as e:
        return {"Error": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8003)

# TODO Add config json for incoming and converted folder name and flag if incoming file need to delete
