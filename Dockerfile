# Stage 1: Build frontend
FROM node:18-alpine AS frontend-build
WORKDIR /build

# Copy frontend code
COPY ./app-frontend/ ./

# Install and build
RUN npm install && npm run build

# Stage 2: Backend with Python and built frontend
FROM python:3.12.9-alpine
WORKDIR /root

# Install required packages
COPY /app-service/requirements.txt ./
RUN apk update && apk add --no-cache git
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend app
COPY /app-service/app.py ./

# Copy built frontend into backend image
COPY --from=frontend-build /build/dist ./dist

ENTRYPOINT ["python"]
CMD ["app.py"]
