# Use python 3.12 slim image (supports ARM64/Raspberry Pi)
FROM python:3.12-slim

# Install uv from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Ensure python output is sent directly to terminal (for real-time logs)
ENV PYTHONUNBUFFERED=1

# Copy dependency files first for caching
COPY pyproject.toml uv.lock ./

# Install dependencies
# --frozen: sync from lockfile without updating it
# --no-dev: do not install dev dependencies
# --no-install-project: do not install the current project as a package
RUN uv sync --frozen --no-dev --no-install-project

# Copy the rest of the application code
COPY . .

# Expose the API port
EXPOSE 8500

# Run the application
# We use 'uv run' to ensure it uses the environment's dependencies
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8500"]
