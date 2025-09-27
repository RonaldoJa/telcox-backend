FROM ubuntu:latest
LABEL authors="ronal"

ENTRYPOINT ["top", "-b"]