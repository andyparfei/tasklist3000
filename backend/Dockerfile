# Install uv
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Change the working directory to the `app` directory
WORKDIR /app

# Copy the lockfile and `pyproject.toml` into the image
COPY uv.lock /app/uv.lock
COPY pyproject.toml /app/pyproject.toml

# Copy the entire project into the image
COPY . /app

# Install dependencies (after copying the full project)
#RUN uv sync --frozen --no-install-project

# Sync the project
#RUN uv sync --frozen
EXPOSE 8080
RUN uv pip install --system .

CMD [ "python", "-m", "tasklist3000.main" ]
