# syntax=docker/dockerfile:1.6

# Global build arguments
ARG CI=true
ARG DEBIAN_FRONTEND=noninteractive
ARG PYTHON_VERSION=3.11
ARG PIP_ROOT_USER_ACTION=ignore
ARG PIP_DISABLE_PIP_VERSION_CHECK=1
ARG MX3_BUILD_DEPS_URL="https://s3-api.asci.synchrotron.org.au/beamline-mx3/build_deps/dozor"


#### PyDozor Builder ####
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

ARG DEBIAN_FRONTEND
ARG PYTHON_VERSION
ARG PIP_ROOT_USER_ACTION
ARG PIP_DISABLE_PIP_VERSION_CHECK
ARG MX3_BUILD_DEPS_URL
ARG AS_PIP_INDEX_URL="https://pypi.asci.synchrotron.org.au/root/pypi/+simple"
ARG POETRY_VIRTUALENVS_IN_PROJECT=true
ARG POETRY_VIRTUALENVS_CREATE=false
ARG POETRY_NO_INTERACTION=1
ARG POETRY_VERSION=1.8.2
ARG POETRY_DEPENDENCY_GROUPS=main
ARG LIB_DOZOR_BUILD="20/dozor_20_1714113381.tar.gz"
ARG LIB_DOZOR_BUILD_SHA256=c38a3044f834085c5db6bf7c0e5972cfd1ec51c19768eea97e84bedeb07a8cc9
ENV LIB_DOZOR_PATH="/opt/dozor/libdozor.so"

# Install system packages
RUN <<EOT bash
set -eux
apt-get update
apt-get install -y gcc libgomp1 libquadmath0 gfortran
rm -rf /var/lib/apt/lists/*
EOT

# Download and unpack Dozor build archive
WORKDIR /opt/dozor
ADD --checksum=sha256:${LIB_DOZOR_BUILD_SHA256} \
    "${MX3_BUILD_DEPS_URL}/artifacts/${LIB_DOZOR_BUILD}" \
    ./build_archive.tar.gz
RUN tar -xzf ./build_archive.tar.gz && rm ./build_archive.tar.gz

# Install Poetry package manager
RUN python -m pip install poetry==${POETRY_VERSION}

WORKDIR /opt/pydozor

# Copy across project files
COPY --link ./pyproject.toml ./poetry.lock ./README.md ./
COPY --link ./pydozor/__init__.py ./pydozor/__init__.py

# Install project and dependencies
RUN python${PYTHON_VERSION} -m poetry install \
    --compile --only ${POETRY_DEPENDENCY_GROUPS}

ENV HDF5_PLUGIN_PATH="/opt/pydozor/.venv/lib/python${PYTHON_VERSION}/site-packages/bitshuffle/plugin"

COPY --link ./pydozor ./pydozor


FROM python:${PYTHON_VERSION}-alpine AS build_pyproject

ARG PYTHON_VERSION
ARG PIP_ROOT_USER_ACTION
ARG PIP_DISABLE_PIP_VERSION_CHECK

WORKDIR /opt/pydozor
COPY --link ./pyproject.toml ./pyproject.toml

# Install PIP dependencies
COPY --link <<EOF requirements.txt
tomlkit == 0.12.4 --hash=sha256:5cd82d48a3dd89dee1f9d64420aa20ae65cfbd00668d6f094d7578a78efbb77b
EOF
RUN <<EOT /bin/sh
_pip_index_url="https://pypi.org/simple"
_pip_user_agent=python - <<-\GET_PIP_USER_AGENT
from sys import stdout
from pip._internal.network.session import user_agent
stdout.write(user_agent())
GET_PIP_USER_AGENT

# Check if configured index is actually network accessible
if wget --spider -T 10 -U "${_pip_user_agent}" -q "${AS_PIP_INDEX_URL}"; then
    # Index is network accessible
    _pip_index_url="${AS_PIP_INDEX_URL}"
fi

# Install Python dependencies
pip install \
    --no-deps \
    --ignore-installed \
    --compile \
    --require-hashes \
    --progress-bar off \
    --no-clean \
    --extra-index-url "${_pip_index_url}" \
    --no-input \
    --no-cache-dir \
    --no-color \
    -r requirements.txt
EOT

# Modify `pyproject.toml` to include `libdozor.so`
RUN <<EOT python
from __future__ import annotations

from typing import TYPE_CHECKING
from tomlkit import load as tomlkit_load, dump as tomlkit_dump

if TYPE_CHECKING:
    from tomlkit import TOMLDocument


def main() -> None:
    # Read `pyproject.toml`
    _pyproject: TOMLDocument
    with open("pyproject.toml", "r") as _file:
        _pyproject = tomlkit_load(_file)

    if "include" not in _pyproject["tool"]["poetry"]:
        _pyproject["tool"]["poetry"].add("include", [])

    # Add `libdozer.so` to build includes
    _pyproject["tool"]["poetry"]["include"].append(
        {
            "path": "*.so",
            "format": ["sdist", "wheel"],
        }
    )

    # Write modified `pyproject.toml`
    with open("pyproject.toml", "w") as _file:
        tomlkit_dump(_pyproject, _file)


if __name__ == "__main__":
    main()
EOT


#### PyDozor Build Step ####
FROM builder AS build

# Build PyDozor package with `libdozor.so`
WORKDIR /opt/pydozor
COPY --from=build_pyproject /opt/pydozor/pyproject.toml ./pyproject.toml
RUN cp /opt/dozor/libdozor.so /opt/pydozor/libdozor.so && \
    poetry build --no-interaction


#### Output Build Files ####
FROM scratch AS dist
COPY --from=build /opt/pydozor/dist .


#### Container Runtime ####
FROM builder AS runtime

COPY --link ./dozor_offline.py ./test.py ./
