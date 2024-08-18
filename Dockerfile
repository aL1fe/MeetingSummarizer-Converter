FROM python:latest

WORKDIR /app

COPY . .

RUN python -m pip install --upgrade pip && \
    apt-get update
	
RUN apt-get install -y ffmpeg 
RUN pip install -r requirements.txt

CMD [ "python", "main.py" ]