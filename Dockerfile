FROM python:3.9-slim as base

# Setup env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1


FROM base AS python-deps

# Install pipenv and curl for if/necessary internal debug
RUN pip install pipenv
RUN apt-get update && apt-get install -y --no-install-recommends curl

# Install python dependencies in /.venv
COPY Pipfile .
COPY Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy


FROM base AS setup

# Copy virtual env from python-deps stage
COPY --from=python-deps /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

# Create and switch to a new user
# RUN useradd --create-home appuser
# WORKDIR /home/appuser
# USER appuser
WORKDIR /app

# Install application into container
COPY . .

# Init the application
ENV FLASK_APP=data_site
ENV FLASK_ENV=development

RUN flask db init \
    && flask db migrate \
    && flask db upgrade \
    && flask import-planmap

FROM setup AS runtime

ARG FLASK_ENV=production
ENV FLASK_ENV=$FLASK_ENV
ENTRYPOINT ["python", "-m", "flask", "run"]
CMD ["--host", "0.0.0.0", "--port", "5000"]
# CMD ["--port", "5000"]
