FROM python:3.11-slim

RUN sed -i 's|http://deb.debian.org/debian|https://repo.huaweicloud.com/debian|g; s|http://deb.debian.org/debian-security|https://repo.huaweicloud.com/debian-security|g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends -o Acquire::Retries=5 openmpi-bin libopenmpi-dev build-essential openssh-client openssh-server \
    && mkdir -p /run/sshd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/mpi
COPY requirements.txt .
RUN pip install --no-cache-dir -i https://repo.huaweicloud.com/repository/pypi/simple --trusted-host repo.huaweicloud.com mpi4py

COPY *.py /opt/mpi/
CMD ["python", "/opt/mpi/pi_mpi.py"]
