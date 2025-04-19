# Creates environment to build python binaries
FROM ubuntu:20.04 as seedsync_build_pyinstaller_env
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.8 \
    python3.8-dev \
    python3.8-distutils \
    curl \
    binutils \
    ca-certificates \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
# Switch to Python 3.8
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1
RUN update-alternatives --set python /usr/bin/python3.8
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1
RUN update-alternatives --set python3 /usr/bin/python3.8

# Install pip using get-pip.py
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python get-pip.py --force-reinstall && \
    rm get-pip.py && \
    pip install --no-cache-dir --upgrade pip

# Install Poetry using official installer - pinning version for stability
ENV POETRY_VERSION=1.1.13
ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN curl -sSL https://install.python-poetry.org | python - --version ${POETRY_VERSION}

# Configure Poetry and install dependencies
RUN poetry config virtualenvs.create false
COPY src/python/pyproject.toml /app/python/
COPY src/python/poetry.lock /app/python/
WORKDIR /app/python
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Remove the explicit install/upgrade - let Poetry handle it
# RUN pip install --no-cache-dir --upgrade setuptools packaging

RUN poetry install


# Builds seedsync with pyinstaller
# Output is in /build/dist/seedsync/
FROM seedsync_build_pyinstaller_env as seedsync_build_pyinstaller
COPY src/python /python
COPY src/pyinstaller_hooks /pyinstaller_hooks
RUN mkdir -p /build
RUN pyinstaller /python/seedsync.py \
    -y \
    -p /python \
    --distpath /build/dist \
    --workpath /build/work \
    --specpath /build \
    --additional-hooks-dir /pyinstaller_hooks/ \
    --hidden-import="pkg_resources.py2_warn" \
    --name seedsync


# Builds scanfs with pyinstaller
# Output is in /build/dist/
FROM seedsync_build_pyinstaller_env as seedsync_build_scanfs
COPY src/python /python
RUN mkdir -p /build
RUN	pyinstaller /python/scan_fs.py \
    -y \
    --onefile \
    -p /python \
    --distpath /build/dist \
    --workpath /build/work \
    --specpath /build \
    --name scanfs


# Creates environment for angular
FROM node:12.16 as seedsync_build_angular_env
COPY src/angular/package*.json /app/
WORKDIR /app
RUN npm install

# Builds angular app into html
# Output is in /build/dist/
FROM seedsync_build_angular_env as seedsync_build_angular
COPY src/angular /app
WORKDIR /app
RUN node_modules/@angular/cli/bin/ng build -prod --output-path /build/dist/


# Creates environment to build deb packages
FROM ubuntu:16.04 as seedsync_build_deb_env
RUN apt-get update
RUN apt-get install -y build-essential dh-systemd debhelper
RUN apt-get install -y devscripts


# Builds debian package
# Output is in /build/dist/
FROM seedsync_build_deb_env as seedsync_build_deb
RUN mkdir -p /build/work
COPY src/debian /build/work/debian
COPY --from=seedsync_build_pyinstaller /build/dist/seedsync /build/work/seedsync
COPY --from=seedsync_build_scanfs /build/dist/scanfs /build/work/seedsync/
COPY --from=seedsync_build_angular /build/dist /build/work/seedsync/html
WORKDIR /build/work
RUN dpkg-buildpackage -B -uc -us
RUN ls /build/*.deb && echo "----" && ls /build/work


# Exports deb package to host
FROM scratch AS seedsync_build_deb_export
COPY --from=seedsync_build_deb /build/*.deb .

# Exports scanfs to host
FROM scratch AS seedsync_build_scanfs_export
COPY --from=seedsync_build_scanfs /build/dist/scanfs .

# Exports html to host
FROM scratch AS seedsync_build_angular_export
COPY --from=seedsync_build_angular /build/dist ./html
