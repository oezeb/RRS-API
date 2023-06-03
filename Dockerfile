FROM python:3.9-slim

WORKDIR /

COPY setup.py .
COPY MANIFEST.in .
COPY app/ app/

RUN pip install .

ENV DATABASE=$DATABASE
ENV DB_USER=$DB_USER
ENV DB_PASSWORD=$DB_PASSWORD

CMD ["flask", "run"]
