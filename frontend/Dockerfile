FROM node:20-alpine AS deps
WORKDIR /app/frontend
COPY frontend/package.json .
RUN npm install

FROM node:20-alpine AS builder
WORKDIR /app
ARG NEXT_PUBLIC_API_BASE_URL=http://localhost:8080
ARG NEXT_PUBLIC_APP_LOCALE=ru
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL
ENV NEXT_PUBLIC_APP_LOCALE=$NEXT_PUBLIC_APP_LOCALE
COPY --from=deps /app/frontend/node_modules ./frontend/node_modules
COPY frontend ./frontend
COPY CONTENT ./CONTENT
WORKDIR /app/frontend
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app/frontend
ENV NODE_ENV=production
ENV NEXT_PUBLIC_APP_LOCALE=ru
COPY --from=builder /app/frontend ./
EXPOSE 3000
CMD ["npm", "run", "start"]
