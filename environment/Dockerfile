FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb

ENV DEBIAN_FRONTEND=noninteractive

# Least-volatile layers first: fix the working directory before the apt and
# dependency layers so a change to those never invalidates the WORKDIR layer.
WORKDIR /app

RUN set -eu; \
    delay=5; \
    for attempt in 1 2 3 4; do \
        if apt-get -o Acquire::Retries=3 -o Acquire::http::Timeout=20 \
                -o Acquire::https::Timeout=20 update \
            && apt-get -o Acquire::Retries=3 -o Acquire::http::Timeout=20 \
                -o Acquire::https::Timeout=20 install -y --no-install-recommends \
                tmux asciinema; then \
            rm -rf /var/lib/apt/lists/*; \
            exit 0; \
        fi; \
        echo "apt attempt ${attempt} failed, retrying in ${delay}s" >&2; \
        rm -rf /var/lib/apt/lists/*; \
        sleep "${delay}"; \
        delay=$((delay * 2)); \
    done; \
    exit 1

# /app/data/registry_index.json ships TRUNCATED exactly as the failed migration
# left it; the pre-migration snapshot and the replay journal beside it are the
# recovery sources the responder has to merge back into the authoritative index.
COPY app/ /app/
RUN cp /app/workflow/resolver.py /app/workflow/.resolver.original \
    && chmod a-w /app/workflow/.resolver.original
