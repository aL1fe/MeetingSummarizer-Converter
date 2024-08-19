FROM al1fe/converter_base

WORKDIR /app

COPY . .

CMD [ "python", "main.py" ]
