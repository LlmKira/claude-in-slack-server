FROM python:3.10-slim-bullseye

WORKDIR /usr/src/app

ADD ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:fastapi_app", "--host", "0.0.0.0", "--port", "8080"]
