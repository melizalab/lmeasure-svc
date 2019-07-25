FROM python:3.6-stretch

RUN apt-get update && apt-get install -y \
    curl \
    unzip

RUN curl -O http://cng.gmu.edu:8080/Lm/release/linux/Lmv5.3_64bit.zip \
    && echo "2ca13774c81b13effe85b856e8ae406eeb1adba8  Lmv5.3_64bit.zip" | sha1sum -c - \
    && unzip Lmv5.3_64bit.zip \
    && mkdir -p /io \
    && install -m 755 Lmv5.3_64bit/lmeasure /io \
    && rm -rf Lmv5.3_64bit*

ENV PATH="/io:${PATH}"

ADD . /app
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]
