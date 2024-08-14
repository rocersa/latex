# Stage 1: Setup LaTeX environment
FROM texlive/texlive:latest AS texlive

# Initialize tlmgr and update packages
RUN tlmgr init-usertree && \
    tlmgr update --self && \
    tlmgr update --all

# Stage 2: Setup Python environment
FROM python:3.9-slim

# Set the working directory
WORKDIR /usr/src/app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install LaTeX (only the minimal set needed)
RUN apt-get update && \
    apt-get install -y texlive-base && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy LaTeX-related files from the texlive stage
COPY --from=texlive /usr/share/texlive /usr/share/texlive

# Copy the Flask application code into the container
COPY app.py ./

# Expose the port the app runs on
EXPOSE 5000

# Define the command to run the Flask application
CMD ["python", "app.py"]
