FROM node:18-slim

# Instalar dependencias del sistema requeridas para ejecutar Puppeteer y Google Chrome
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    ca-certificates \
    git \
    && rm -rf /var/lib/apt/lists/*

# Descargar e instalar la clave y repositorio oficial de Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' \
    && apt-get update \
    && apt-get install -y --no-install-recommends google-chrome-stable fonts-ipafont-gothic fonts-wqy-zenhei fonts-thai-tlwg fonts-kacst fonts-freefont-ttf libxss1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar configuracion de dependencias de Node
COPY package.json ./
RUN npm install

# Copiar el script de la pasarela y la sesión de confianza
COPY qr_gateway.js ./
COPY .wwebjs_auth/ ./.wwebjs_auth/

# Omitir descarga interna de Chromium en Puppeteer y usar el Chrome instalado en el sistema
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/google-chrome-stable

EXPOSE 3000

CMD ["npm", "start"]
