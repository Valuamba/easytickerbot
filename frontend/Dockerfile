FROM nginx:1.19-alpine

WORKDIR /srv

# Update package index
RUN apk update

# Install node.js and npm
RUN apk add nodejs-current npm

# Install application requirements
COPY package.json .
COPY package-lock.json .
RUN npm install

# Copy nginx configuration templates
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template

# Copy main page file
COPY index.html .

# Copy main application source files
COPY webpack.config.js .
COPY src src

RUN npm run bundle
