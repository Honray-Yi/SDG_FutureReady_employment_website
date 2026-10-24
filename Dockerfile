FROM node:22-bookworm-slim AS frontend-build
WORKDIR /workspace
RUN corepack enable && corepack prepare pnpm@10 --activate
COPY . .
RUN pnpm install --frozen-lockfile \
    && PORT=5173 BASE_PATH=/ NODE_ENV=production pnpm --filter @workspace/future-ready run build

FROM python:3.13-slim-bookworm AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=10000
WORKDIR /app
COPY requirements.lock /app/requirements.lock
RUN python -m pip install --no-cache-dir --require-hashes -r /app/requirements.lock
COPY artifacts/api-server /app/artifacts/api-server
COPY --from=frontend-build /workspace/artifacts/future-ready/dist/public /app/artifacts/api-server/frontend/dist
WORKDIR /app/artifacts/api-server/backend
EXPOSE 10000
CMD ["python", "run_server.py"]
