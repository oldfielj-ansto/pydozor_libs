# syntax=docker/dockerfile:1.6

FROM docker.asci.synchrotron.org.au/mx3/dozor:latest

ARG DEBIAN_FRONTEND=noninteractive
ARG PYTHON_VERSION=3.11
ARG PIP_ROOT_USER_ACTION=ignore
ARG PIP_DISABLE_PIP_VERSION_CHECK=1
ARG POETRY_VIRTUALENVS_IN_PROJECT=true
ARG POETRY_VIRTUALENVS_CREATE=false
ARG POETRY_NO_INTERACTION=1
ARG POETRY_VERSION=1.8.1
ARG POETRY_DEPENDENCY_GROUPS=main

RUN apt-get update -y && apt-get install -y \
    python${PYTHON_VERSION} python${PYTHON_VERSION}-dev python${PYTHON_VERSION}-venv \
    python3-pip

RUN rm /usr/lib/python${PYTHON_VERSION}/EXTERNALLY-MANAGED
RUN python${PYTHON_VERSION} -m pip install poetry==${POETRY_VERSION}

WORKDIR /opt/pydozor

# Setup entrypoint script
# COPY <<EOF entrypoint.sh
# #!/usr/bin/env bash
# set -e
# source /opt/pydozor/.venv/bin/activate
# if [ -z "\$*" ]; then
#   exec bash --login
# else
#   python /opt/pydozor/dozor_offline.py "\$@"
# fi
# EOF
# RUN chmod +x entrypoint.sh
COPY ./entrypoint.sh ./

# Create project virtual environment
RUN python${PYTHON_VERSION} -m venv ./.venv

# Install project and dependencies
# COPY --link ./pyproject.toml ./poetry.lock ./
COPY ./pyproject.toml ./poetry.lock ./
RUN python${PYTHON_VERSION} -m poetry install \
    --compile --only ${POETRY_DEPENDENCY_GROUPS}

ENV HDF5_PLUGIN_PATH="/opt/pydozor/.venv/lib/python${PYTHON_VERSION}/site-packages/bitshuffle/plugin"

# Copy across project files
# COPY --link ./pydozor ./pydozor
COPY ./pydozor ./pydozor
# COPY --link ./dozor_offline.py ./
COPY ./dozor_offline.py ./

ENTRYPOINT [ "/opt/pydozor/entrypoint.sh" ]
