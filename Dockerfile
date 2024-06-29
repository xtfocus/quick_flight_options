FROM python:3.11-slim
RUN apt-get update && apt-get install -y git
# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt into the container at /app
COPY requirements.txt .

# Install any dependencies specified in requirements.txt
RUN pip install git+https://github.com/xtfocus/quick_flight_options.git

# Copy the rest of the application code into the container at /app
COPY . .

ENTRYPOINT ["/bin/bash"]
