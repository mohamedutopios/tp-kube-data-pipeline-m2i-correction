FROM node:20-alpine
WORKDIR /app
RUN npm init -y && npm install express mysql2
COPY server.js ./
COPY public ./public
EXPOSE 3000
CMD ["node","server.js"]
