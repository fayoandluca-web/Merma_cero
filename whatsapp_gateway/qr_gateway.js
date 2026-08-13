const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');
const express = require('express');
const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const PORT = process.env.PORT || 3000;
const WEBHOOK_URL = process.env.WEBHOOK_URL || 'http://localhost:8000/webhook';

// Mapa en memoria para recordar los identificadores originales (ej. @lid o @c.us)
const userFromCache = new Map();

const executablePath = process.env.PUPPETEER_EXECUTABLE_PATH || 'C:\\Users\\arqis\\.cache\\puppeteer\\chrome\\win64-146.0.7680.31\\chrome-win64\\chrome.exe';

const client = new Client({
    authStrategy: new LocalAuth({
        dataPath: './.wwebjs_auth'
    }),
    puppeteer: {
        headless: true,
        executablePath: executablePath,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }
});

client.on('qr', (qr) => {
    console.log('\n=== ESCANEA ESTE CÓDIGO QR CON TU WHATSAPP ===\n');
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    console.log('¡Cliente de WhatsApp listo y conectado!');
});

client.on('message', async (msg) => {
    if (msg.from.includes('@g.us')) return;

    console.log(`Mensaje recibido de ${msg.from}: ${msg.body}`);
    
    // Guardar el identificador original asociado a la versión con "+" para responder correctamente
    const cleanPhone = '+' + msg.from.split('@')[0];
    userFromCache.set(cleanPhone, msg.from);

    try {
        // Enviar la petición al webhook de FastAPI simulando el formato URL Form Encoded de Twilio
        const params = new URLSearchParams();
        params.append('From', `whatsapp:+${msg.from.split('@')[0]}`);
        params.append('Body', msg.body);
        params.append('ProfileName', msg._data.notifyName || 'Comerciante');

        await axios.post(WEBHOOK_URL, params, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
    } catch (err) {
        console.error('Error al enviar al webhook de FastAPI:', err.message);
    }
});

app.post('/send', async (req, res) => {
    const { to, body } = req.body;
    try {
        const cleanTo = to.replace('whatsapp:', '').trim();
        // Intentar recuperar el identificador original de la caché
        const cachedId = userFromCache.get(cleanTo);
        const formattedTo = cachedId || (cleanTo.replace('+', '') + '@c.us');
        
        await client.sendMessage(formattedTo, body);
        console.log(`Mensaje enviado a ${formattedTo}: ${body}`);
        res.json({ status: 'success' });
    } catch (err) {
        console.error('Error al enviar mensaje:', err.message);
        res.status(500).json({ status: 'error', error: err.message });
    }
});

app.listen(PORT, () => {
    console.log(`Pasarela HTTP escuchando en el puerto ${PORT}`);
    client.initialize();
});
