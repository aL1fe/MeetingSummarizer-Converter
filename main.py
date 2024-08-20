from fastapi import FastAPI, UploadFile
import ffmpeg
import os
from dotenv import load_dotenv
from module_broker import publish_message
from module_file import save_file


load_dotenv()
port = int(os.getenv('CONVERTER_PORT', 8003))    # 8003 is the default value if PORT is not set
is_delete_after_processing = (os.getenv('CONVERTER_IS_DELETE_AFTER_PROCESSING', 'False')
                              .lower() in ('true', '1', 'yes'))
is_send_to_broker = (os.getenv('CONVERTER_IS_SEND_TO_BROKER', 'False')
                     .lower() in ('true', '1', 'yes'))
conversion_format = os.getenv('CONVERTER_FORMAT')
queue_name = os.getenv('CONVERTER_QUEUE_NAME')
upload_folder = "incoming_files"
output_folder = "converted_files"

app = FastAPI()


def convert_to_mp3(input_file, output_file):
    (
        ffmpeg
        .input(input_file)
        .output(output_file, format=conversion_format, audio_bitrate='320k')
        .overwrite_output()  # Overwrite file if exist
        .run()
    )


@app.post("/convert/")
async def upload_file(file: UploadFile):
    try:
        input_file_path = await save_file(file, upload_folder)  # Save received file to the incoming files folder

        os.makedirs(output_folder, exist_ok=True)  # Create folder for converted files if it does not exist

        filename, _ = os.path.splitext(file.filename)  # Separate the file name and its extension

        output_file_path = os.path.join(output_folder, f"{filename}.mp3")

        convert_to_mp3(input_file_path, output_file_path)
        print(f"File {file.filename} was converted.")
        
        if is_delete_after_processing:
            os.remove(input_file_path)  # Delete file after processing    

        # Send message to the message broker
        if is_send_to_broker:
            converted_file_full_path = os.path.abspath(output_file_path)  # Get full path to the converted file
            publish_message(queue_name, converted_file_full_path)
            print(f"Message: \"{converted_file_full_path}\" was sent to broker.")

        return {"Status": "Ok"}
    except Exception as e:
        return {"Status": f"Error: {str(e)}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
