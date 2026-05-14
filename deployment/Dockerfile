FROM python:3.11-slim-bookworm AS builder
COPY --from=ghcr.io/astral-sh/uv:0.11.11 /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=0 \
    VENV_PATH=/opt/venv

WORKDIR /app

RUN uv venv "${VENV_PATH}"
ENV PATH="${VENV_PATH}/bin:${PATH}"

ARG INSTALL_EXTRAS=""

COPY pyproject.toml README.md ./

RUN set -eux; \
    extras_args=""; \
    if [ -n "${INSTALL_EXTRAS}" ]; then \
        OLD_IFS="${IFS}"; \
        IFS=','; \
        for extra in ${INSTALL_EXTRAS}; do \
            extra="$(printf '%s' "${extra}" | xargs)"; \
            if [ -n "${extra}" ]; then \
                extras_args="${extras_args} --extra ${extra}"; \
            fi; \
        done; \
        IFS="${OLD_IFS}"; \
    fi; \
    uv pip install -r pyproject.toml ${extras_args}


FROM python:3.11-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:${PATH}" \
    PORT=8000

WORKDIR /app

RUN addgroup --system app \
    && adduser --system --ingroup app --home /app app

COPY --from=builder /opt/venv /opt/venv
COPY api ./api
COPY health ./health
COPY main ./main

USER app

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main.app:app", "--host", "0.0.0.0", "--port", "8000"]
