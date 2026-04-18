FROM python:3.12-slim

# Node 20 LTS
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Build arg para Vite — Railway lo inyecta en build time
ARG VITE_API_URL=http://localhost:8000

COPY Hackaton/package*.json Hackaton/
RUN cd Hackaton && npm ci
COPY Hackaton/ Hackaton/
RUN cd Hackaton && VITE_API_URL=$VITE_API_URL npm run build

COPY unifila-app/package*.json unifila-app/
RUN cd unifila-app && npm ci
COPY unifila-app/ unifila-app/
RUN cd unifila-app && VITE_API_URL=$VITE_API_URL npm run build

# Backend source
COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
