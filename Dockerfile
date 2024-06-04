# Use the official Python 3.10 runtime as a parent image
FROM python:3.10

WORKDIR /app

VOLUME ["/app"]
COPY requirements.txt /app/

# YOU NEED THESE IN THE FINAL BUILD
# COMMENT OUT FOR DEV THOUGH
# COPY agent.py /app/
# COPY softbeing/ /app/softbeing

# Install LangChain and its components
RUN pip install --no-cache-dir -r requirements.txt

# Define the directory that can be mounted from the host.
# This is where the host's directory will be seen in the container.
VOLUME ["/app/configs", "/logs", "/app/personality"]

ENTRYPOINT python agent.py /app/configs/$CONFIG_FILENAME