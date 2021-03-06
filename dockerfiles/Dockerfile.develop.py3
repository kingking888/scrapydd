FROM kevenli/scrapydd-dockerbase:py3

RUN apk add libffi-dev \
    openssl-dev gcc libc-dev make libxml2-dev libxslt-dev \
    tzdata jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
WORKDIR /scrapydd_src
ADD scrapydd ./scrapydd
ADD tests ./tests
ADD samples ./samples
COPY setup.py requirements.txt requirements_test.txt README.rst ./
RUN pip install -r /scrapydd_src/requirements.txt
RUN pip install -r /scrapydd_src/requirements_test.txt
RUN python setup.py install
WORKDIR /scrapydd
ENV TZ /usr/share/zoneinfo/Etc/UTC
CMD ["scrapydd"]