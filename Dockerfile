FROM python:3.9-alpine

WORKDIR /rrs-api

COPY setup.py .
COPY MANIFEST.in .
COPY app/ ./app


# RUN pip config --user set global.index-url http://pypi.mirrors.ustc.edu.cn/simple/
# RUN pip config --user set global.trusted-host pypi.mirrors.ustc.edu.cn
RUN pip install .
RUN pip install waitress

EXPOSE 5000

CMD ["waitress-serve", "--port=5000", "--call", "app:create_app"]