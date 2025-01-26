# Use an official GPU-enabled PyTorch base image
FROM python:3.9-slim

# Copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

# Set the working directory to /app
WORKDIR /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Uninstall the existing unsloth package and install the latest version from GitHub
RUN pip uninstall unsloth -y && \
    pip install --upgrade --no-cache-dir --no-deps git+https://github.com/unslothai/unsloth.git

# Copy every content from the local folder to the image
COPY . .

# Expose the port Gradio will run on
EXPOSE 7860

# Command to run your Gradio app
CMD ["python", "app.py"]