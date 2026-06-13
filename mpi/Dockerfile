FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends openmpi-bin libopenmpi-dev build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/mpi
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py /opt/mpi/
CMD ["python", "/opt/mpi/pi_mpi.py"]
