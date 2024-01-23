FROM python:3.11-alpine

RUN apk --update add curl unzip

RUN curl -O https://gracula.psyc.virginia.edu/public/software/Lmv5.3_64bit.zip \
    && echo "2ca13774c81b13effe85b856e8ae406eeb1adba8  Lmv5.3_64bit.zip" | sha1sum -c - \
    && unzip Lmv5.3_64bit.zip \
    && mkdir -p /io \
    && install -m 755 Lmv5.3_64bit/lmeasure /io \
    && rm -rf Lmv5.3_64bit*

ENV PATH="/io:${PATH}"

ADD . /app
WORKDIR /app
RUN python -m venv venv
RUN venv/bin/python -m pip install --upgrade pip setuptools wheel
RUN venv/bin/python -m pip install -r requirements.txt

EXPOSE 5000

CMD ["venv/bin/python", "app.py"]
