# Stage 1: Build the React app
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the source code and build the app
COPY . .

EXPOSE 5173
CMD ["npm", "run", "dev"]
