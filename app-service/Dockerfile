FROM python:3.12.9-alpine
WORKDIR /root
COPY requirements.txt /root/
RUN <<EOF
apk update
apk add git
EOF
RUN pip install -r requirements.txt
COPY app.py /root/
ENTRYPOINT ["python"]
CMD ["app.py"]