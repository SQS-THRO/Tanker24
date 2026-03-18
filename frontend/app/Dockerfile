FROM node:20-alpine AS build

WORKDIR /app

# install dependencies
COPY package*.json ./
RUN npm ci

COPY . .

# build the app
RUN npm run build
RUN npm prune --production

FROM node:20-alpine

WORKDIR /app

# only copy necessary files
COPY --from=build /app/build build/
COPY --from=build /app/node_modules node_modules/
COPY package.json .

ENV NODE_ENV=production

# expose port
EXPOSE 3000

# run the app
CMD ["node", "build"]
