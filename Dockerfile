# Stage 1: Setup LaTeX environment
FROM texlive/texlive:latest

# Initialize tlmgr and update packages
RUN tlmgr init-usertree && \
    tlmgr update --self && \
    tlmgr update --all

# Install Python and virtualenv
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create and activate a virtual environment
RUN python3 -m venv /usr/src/app/venv

# Set the working directory
WORKDIR /usr/src/app

# Copy the requirements file and install dependencies in the virtual environment
COPY requirements.txt ./
RUN /usr/src/app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy the Flask application code into the container
COPY app.py ./

# Set environment variables to use the virtual environment
ENV PATH="/usr/src/app/venv/bin:${PATH}"

# Expose the port the app runs on
EXPOSE 5000

# Define the command to run the Flask application
CMD ["python", "app.py"]
