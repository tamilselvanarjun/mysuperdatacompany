# Use the official Python image from the Docker Hub
FROM python:3.8-slim-buster

# Set the working directory to /code
WORKDIR /code

# Copy the requirements file into the image
COPY requirements.txt /code/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /code
COPY . /code/
