FROM python:3.7.0
RUN mkdir -p /home/app
WORKDIR /app
COPY . /app
CMD ["python","test.py"]
