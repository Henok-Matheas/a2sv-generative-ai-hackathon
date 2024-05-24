# Use an official Python runtime as a base image
FROM python:3.11-slim

# Set the working directory to the directory containing the Dockerfile
RUN mkdir /code

WORKDIR /code

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=8080"]