FROM python:3.9.7-slim

WORKDIR /app
RUN apt-get update && apt-get install -y libreoffice-writer unoconv
COPY /serverless-container/requrements.txt .
RUN pip install --no-cache-dir --prefer-binary -r requrements.txt
RUN sed -i 's/env //' /usr/bin/unoconv
COPY parsers.py .
COPY /serverless-container/app.py .
COPY /serverless-container/creds/credentials.json ./creds/credentials.json
COPY /serverless-container/creds/token.json ./creds/token.json
COPY /serverless-container/src ./src

CMD [ "python", "app.py" ]
