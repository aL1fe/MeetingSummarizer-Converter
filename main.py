from fastapi import FastAPI, UploadFile
import ffmpeg
import os
import json
from dotenv import load_dotenv
from module_broker import publish_message

#  Load environment variables from .env file
load_dotenv()
port = int(os.getenv('PORT', 8003))    # 8003 is the default value if PORT is not set
broker_login = os.getenv('LOGIN')
broker_password = os.getenv('PASSWORD')

#  Load configurations settings from appconfig file
with open('appconfig.json', 'r') as config_file:
    config = json.load(config_file)
upload_folder = config.get('upload_folder')
output_folder = config.get('output_folder')
delete_after_processing = config.get('delete_after_processing')
conversion_format = config.get('conversion_format')
queue_name = config.get('broker_queue_name')

app = FastAPI()


def convert_to_mp3(input_file, output_file):
    (
        ffmpeg
        .input(input_file)
        .output(output_file, format=conversion_format)
        .overwrite_output()  # Overwrite file if exist
        .run()
    )


async def save_file(file: UploadFile):
    # Create folder if it does not exist
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
        os.makedirs(output_folder, exist_ok=True)

        # Separate the file name and its extension
        filename, _ = os.path.splitext(file.filename)

        # Create filename for converted file
        converted_filename = f"{filename}.mp3"

        converted_file_path = os.path.join(output_folder, converted_filename)

        convert_to_mp3(input_file_path, converted_file_path)

        if delete_after_processing:
            # Delete file after processing
            os.remove(input_file_path)

        # Get full path to the converted file
        converted_file_full_path = os.path.abspath(converted_file_path)

        # Send message to the message broker
        publish_message(queue_name, converted_file_full_path, broker_login, broker_password)

        return {"Status": "Ok"}
    except Exception as e:
        return {"Status": f"Error: {str(e)}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=port)
