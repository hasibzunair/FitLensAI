# Use official Python base image
FROM python:3.9-slim

# Install git
RUN apt-get update && apt-get install -y git

# Copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

# Set the working directory to /app
WORKDIR /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Uninstall the existing unsloth package and install the latest version from GitHub
# RUN pip uninstall unsloth -y && \
#    pip install --upgrade --no-cache-dir --no-deps git+https://github.com/unslothai/unsloth.git

# Copy every content from the local folder to the image
COPY . .

# Expose the port Gradio will run on
EXPOSE 7860

# Command to run your Gradio app
CMD ["python", "app.py"]

### HOW TO ###
# Build
# docker buildx build -t gr-hello-app:v1 --platform Linux/amd64 .
# Run locally
# docker run -p 7860:7860 --name hello-app gr-hello-app:v1
# Tag
# docker tag gr-hello-app:v1 hasibzunair/gr-hello-app:v1
# Push
# docker push hasibzunair/gr-hello-app:v1
# Run from hub
# docker run -p 7860:7860 --name hello-app hasibzunair/gr-hello-app:v1