# Use an official Python runtime as a parent image
FROM python:3.12.2-slim-bullseye

# Set the working directory in the container
WORKDIR /usr/src/app

# Install Chrome
RUN apt-get update && apt-get install -y wget gnupg2 curl unzip software-properties-common \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run app.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0"]
