FROM python:3.13-slim

# Install required dependencies for UV
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Use non-root user
RUN useradd -m -s /bin/bash --create-home minitap
USER minitap

# Download & install latest UV installer
ADD --chown=minitap:minitap https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh
ENV PATH="/home/minitap/.local/bin:$PATH"

WORKDIR /app

COPY --chown=minitap:minitap src /app/src
COPY --chown=minitap:minitap \
    pyproject.toml pyrightconfig.json requirements.txt uv.lock \
    README.md LICENSE \
    /app/

RUN uv venv && uv sync --locked
ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["python", "/app/src/minitap/servers/start_servers.py"]
CMD ["--only", "screen_api"]