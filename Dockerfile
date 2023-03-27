FROM python:3.10.0-alpine
COPY requirements.txt .
COPY main_old.py .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]

