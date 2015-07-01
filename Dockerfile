# vim: set ft=conf
FROM python:2.7

RUN mkdir /app
ADD . /app/
WORKDIR /app
RUN pip install -r requirements-test.txt
RUN pip install tox
RUN python setup.py develop
