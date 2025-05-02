FROM python:3.12.9-slim
WORKDIR /root
COPY requirements.txt /root/
RUN pip install -r requirements.txt
COPY app.py /root/
ENTRYPOINT ["python"]
CMD ["app.py"]