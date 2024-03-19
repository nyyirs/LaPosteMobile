# Use an official Python runtime as a parent image
FROM python:3.12.2-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Install Chrome, ChromeDriver, Xvfb, and other utilities
RUN apt-get update && apt-get install -y wget gnupg2 curl unzip software-properties-common xvfb \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable

# Install ChromeDriver
RUN CHROMEDRIVER_VERSION=$(curl https://chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget -q --continue -P /chromedriver "http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip" && \
    unzip /chromedriver/chromedriver* -d /usr/local/bin/

# Copy the current directory contents into the container at /usr/src/app
COPY /app /app

COPY ./requirements.txt /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set up the Xvfb environment variable for virtual display
ENV DISPLAY=:99

# Optionally, you can start Xvfb when the container starts. To do this, create an entrypoint script.
COPY ./entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
ENTRYPOINT ["entrypoint.sh"]

# Run app.py when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
