LABEL maintainer="Roi Avivi"
FROM python:3.10.0-alpine
COPY main.py .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]

