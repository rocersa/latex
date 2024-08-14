# Stage 1: Setup LaTeX environment
FROM texlive/texlive:latest

# Initialize tlmgr and update packages
RUN tlmgr init-usertree && \
    tlmgr update --self && \
    tlmgr update --all

# Install Python
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /usr/src/app

# Install Python dependencies
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the Flask application code into the container
COPY app.py ./

# Expose the port the app runs on
EXPOSE 5000

# Define the command to run the Flask application
CMD ["python3", "app.py"]
