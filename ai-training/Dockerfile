FROM python:3.11-slim
WORKDIR /work

COPY requirements.txt .
RUN pip install --no-cache-dir \
    -i https://repo.huaweicloud.com/repository/pypi/simple \
    --trusted-host repo.huaweicloud.com \
    -r requirements.txt

COPY download_mnist.py ./
RUN python download_mnist.py

COPY train_single.py train_ddp.py ./
CMD ["python", "train_single.py", "--epochs", "2"]
