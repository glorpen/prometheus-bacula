FROM python:3-alpine as base

LABEL maintainer="Arkadiusz Dzięgiel <arkadiusz.dziegiel@glorpen.pl>"

FROM base as build

COPY ./setup.py /srv/
COPY ./src/ /srv/src/

RUN pip install --root /out --no-warn-script-location /srv \
    && rm -rf /root/.cache \
    && find /out -depth \
    \( -type d -a \( -name test -o -name tests -o -name "__pycache__" \) \) \
    -exec rm -rf '{}' +;

FROM base

COPY --from=build /out/ /

ENTRYPOINT [ "prometheus-bacula" ]
