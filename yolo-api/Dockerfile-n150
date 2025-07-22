# Multi-stage build for React frontend
FROM node:18-alpine as frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# Lightweight Python backend image for N150
FROM python:3.9-slim

# Install minimal system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libgomp1 \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Copy N150-optimized requirements and install Python dependencies
COPY backend/requirements-n150.txt ./requirements.txt
# Install PyTorch CPU version first for N150 compatibility
RUN pip install --no-cache-dir torch==2.0.1 torchvision==0.15.2 --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./
# Use N150-optimized app
COPY backend/app-n150.py ./app.py

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/build ./frontend/build

# Create directories for models, uploads, and results
RUN mkdir -p /app/models /app/uploads /app/results

# Set memory limits for N150
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV OMP_NUM_THREADS=2
ENV MKL_NUM_THREADS=2
ENV TORCH_NUM_THREADS=2

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/models || exit 1

# Run the application
CMD ["python", "app.py"]
