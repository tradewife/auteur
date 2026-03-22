FROM python:3.12-slim

WORKDIR /app

ENV PYTHONPATH=/app

# Install deps
COPY pyproject.toml .
RUN pip install --no-cache-dir pydantic>=2.0 pydantic-settings>=2.0 typer>=0.12 httpx>=0.27 rich>=13.0 google-genai>=1.0 "fastmcp>=3.0" uvicorn[standard] eth-account>=0.10

# Copy the auteur package source
COPY auteur/ auteur/

# Railway injects PORT; use it
EXPOSE ${PORT:-8000}

CMD ["python", "-m", "auteur.start"]
