FROM python:3.11-slim
WORKDIR /work

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY train_single.py train_ddp.py ./
CMD ["python", "train_single.py", "--epochs", "2"]
