# NetSentry Backend - Dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies (includes pandas, numpy, scikit-learn, joblib for ML)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Copy ML models directory (if it exists)
# Create directory structure for models
RUN mkdir -p modelBuilding/models
COPY modelBuilding/models/* modelBuilding/models/ 2>/dev/null || echo "No ML models found - will need to train models"

# Expose port 8000
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

