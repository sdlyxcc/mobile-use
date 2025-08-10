FROM python:3.13-slim

ARG MAESTRO_VERSION=1.41.0

# Install required dependencies for UV & adb
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates adb unzip wget && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install JRE
RUN apt-get update && \
    apt-get install -y --no-install-recommends default-jre && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Use non-root user
RUN useradd -m -s /bin/bash --create-home minitap && \
    chown -R minitap:minitap /opt/
USER minitap

# Download & install latest UV installer
ADD --chown=minitap:minitap https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh
ENV PATH="/home/minitap/.local/bin:$PATH"

# Download & install Maestro
RUN mkdir -p /opt/maestro && \
    wget -q -O /tmp/${MAESTRO_VERSION} "https://github.com/mobile-dev-inc/maestro/releases/download/cli-${MAESTRO_VERSION}/maestro.zip" && \
    unzip -q /tmp/${MAESTRO_VERSION} -d /opt/ && \
    rm /tmp/${MAESTRO_VERSION}
ENV PATH="/opt/maestro/bin:${PATH}"

WORKDIR /app

COPY --chown=minitap:minitap src /app/src
COPY --chown=minitap:minitap \
    pyproject.toml pyrightconfig.json requirements.txt uv.lock \
    README.md LICENSE \
    /app/

RUN uv sync --locked

COPY --chown=minitap:minitap docker-entrypoint.sh /app/docker-entrypoint.sh
ENTRYPOINT ["/app/docker-entrypoint.sh"]
