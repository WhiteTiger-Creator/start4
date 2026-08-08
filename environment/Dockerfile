FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb

ENV DEBIAN_FRONTEND=noninteractive

# Least-volatile layers first: fix the working directory before the apt and
# dependency layers so a change to those never invalidates the WORKDIR layer.
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tmux \
        asciinema \
    && rm -rf /var/lib/apt/lists/*

# /app/data/registry_index.json ships TRUNCATED exactly as the failed migration
# left it; the pre-migration snapshot and the replay journal beside it are the
# recovery sources the responder has to merge back into the authoritative index.
COPY app/ /app/
RUN cp /app/workflow/resolver.py /app/workflow/.resolver.original \
    && chmod a-w /app/workflow/.resolver.original
