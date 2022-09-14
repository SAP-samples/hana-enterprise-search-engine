FROM python:3.10.7-slim

# Dockerfile to build an image with the latest main branch on git.
# !! The secrets must be in a file .config.json which is NOT present in the image
# !! The .config.json must be added at runtime:
# docker run -ti --mount type=bind,source=$(pwd)/src/.config.json,target=/home/appowner/hana-esh-odata/src/.config.json,readonly hana-esh 

LABEL "origin"="https://github.com/SAP-samples/hana-enterprise-search-engine"

ENV APP_FOLDER=/home/appowner/hana-esh-odata

RUN adduser --disabled-login -q appowner
USER appowner

ADD --chown=appowner:appowner https://codeload.github.com/SAP-samples/hana-enterprise-search-engine/tar.gz/refs/heads/main /home/appowner/hana-esh-odata.tar.gz

WORKDIR /home/appowner

RUN tar -xzf ./hana-esh-odata.tar.gz \
    && mv hana-enterprise-search-engine-main ${APP_FOLDER} \
    && rm -f ./hana-esh-odata.tar.gz \
    && python3 -m pip install --user -r ${APP_FOLDER}/requirements/core.txt


WORKDIR ${APP_FOLDER}

CMD ["python3", "src/server.py"]
