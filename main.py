from fastapi import FastAPI, UploadFile
import ffmpeg
import os
import json
from dotenv import load_dotenv
from module_broker import publish_message

#  Load environment variables from .env file
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)
port = int(os.getenv('CONVERTER_INNER_PORT', 8003))    # 8003 is the default value if PORT is not set


#  Load configurations settings from appconfig file
with open('appconfig.json', 'r') as config_file:
    config = json.load(config_file)
upload_folder = config.get('upload_folder')
output_folder = config.get('output_folder')
is_delete_after_processing = config.get('is_delete_after_processing')
is_send_to_broker = config.get('is_send_to_broker')
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
    os.makedirs(upload_folder, exist_ok=True)  # Create folder if it does not exist

    file_path = os.path.join(upload_folder, file.filename)  # Form the full path for the file

    # Save file
    with open(file_path, "wb") as f:
        f.write(await file.read())

    return file_path


@app.post("/convert/")
async def upload_file(file: UploadFile):
    try:
        input_file_path = await save_file(file)  # Save received file to the incoming files folder

        os.makedirs(output_folder, exist_ok=True)  # Create folder for converted files if it does not exist

        filename, _ = os.path.splitext(file.filename)  # Separate the file name and its extension

        output_file_path = os.path.join(output_folder, f"{filename}.mp3")

        convert_to_mp3(input_file_path, output_file_path)

        if is_delete_after_processing:
            os.remove(input_file_path)  # Delete file after processing

        converted_file_full_path = os.path.abspath(output_file_path)  # Get full path to the converted file
        print(f"File {file.filename} was converted.")

        # Send message to the message broker
        if is_send_to_broker:
            publish_message(queue_name, converted_file_full_path)
            print(f"Message: \"{converted_file_full_path}\" was sent to broker.")

        return {"Status": "Ok"}
    except Exception as e:
        return {"Status": f"Error: {str(e)}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
