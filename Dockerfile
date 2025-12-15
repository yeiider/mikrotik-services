# Stage 1: Builder
FROM python:3.10-slim as builder

WORKDIR /code

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# -----------------------------------------------------------------------------
# Stage 2: Final image
FROM python:3.10-slim

WORKDIR /app

# Create a non-root user
RUN addgroup --system app && adduser --system --ingroup app app
USER app

# Copy installed dependencies from builder stage
COPY --from=builder /root/.local /root/.local

# Copy the application code
COPY . .

# Set the path to include the installed packages
ENV PATH=/root/.local/bin:$PATH

# Expose the port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]