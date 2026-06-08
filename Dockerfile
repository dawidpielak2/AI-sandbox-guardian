FROM python:3.10-alpine

RUN adduser -D sandboxuser
WORKDIR /home/sandboxuser
USER sandboxuser

ENTRYPOINT ["python", "-c"]