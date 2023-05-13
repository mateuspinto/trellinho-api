FROM mambaorg/micromamba:latest

ENV DEBIAN_FRONTEND noninteractive

COPY --chown=$MAMBA_USER:$MAMBA_USER env.yaml /tmp/env.yaml
COPY --chown=$MAMBA_USER:$MAMBA_USER requirements.txt /tmp/requirements.txt

RUN micromamba install -y -n base -f /tmp/env.yaml \
    && micromamba clean -a -y

ARG MAMBA_DOCKERFILE_ACTIVATE=1

RUN pip install -r /tmp/requirements.txt

WORKDIR /app

COPY --chown=$MAMBA_USER:$MAMBA_USER src src/
COPY --chown=$MAMBA_USER:$MAMBA_USER trellinho.sqlite3 .

ENTRYPOINT ["/usr/local/bin/_entrypoint.sh", "python", "src/app.py"]