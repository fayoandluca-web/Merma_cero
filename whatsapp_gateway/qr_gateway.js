const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const QRCode = require('qrcode');
const axios = require('axios');
const express = require('express');
const app = express();

let latestQR = '';

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
    latestQR = qr;
    console.log('\n=== ESCANEA ESTE CÓDIGO QR CON TU WHATSAPP ===\n');
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    console.log('¡Cliente de WhatsApp listo y conectado!');
});

client.on('message_create', async (msg) => {
    try {
        if (!msg || !msg.from) return;
        if (msg.fromMe) return; // Omitir mensajes enviados por el bot mismo
        if (msg.from.includes('@g.us')) return; // Omitir grupos

        console.log(`Mensaje detectado de ${msg.from}: ${msg.body}`);
        
        const senderNumber = msg.from.split('@')[0];
        const cleanPhone = '+' + senderNumber;
        userFromCache.set(cleanPhone, msg.from);

        const profileName = (msg._data && msg._data.notifyName) ? msg._data.notifyName : 'Comerciante';

        // Enviar la petición al webhook de FastAPI simulando el formato URL Form Encoded de Twilio
        const params = new URLSearchParams();
        params.append('From', `whatsapp:+${senderNumber}`);
        params.append('Body', msg.body || '');
        params.append('ProfileName', profileName);

        console.log(`Enviando mensaje al webhook de FastAPI (${WEBHOOK_URL})...`);
        const res = await axios.post(WEBHOOK_URL, params, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
        console.log(`Webhook respondio exitosamente:`, res.status);
    } catch (err) {
        console.error('Error en el manejador de mensajes de la pasarela:', err.message, err.stack);
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

app.get('/qr', async (req, res) => {
    if (!latestQR) {
        return res.send('Esperando código QR de WhatsApp... Por favor recarga esta página en 10 segundos.');
    }
    try {
        const qrImage = await QRCode.toDataURL(latestQR);
        res.send(`
            <html>
                <head>
                    <title>Vincular WhatsApp - Merma Cero</title>
                    <style>
                        body { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; background: #0f172a; color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
                        .container { background: #1e293b; padding: 40px; border-radius: 16px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3); text-align: center; max-width: 400px; }
                        img { border: 15px solid white; border-radius: 12px; width: 250px; height: 250px; margin: 20px 0; }
                        h2 { margin: 0 0 10px 0; font-size: 20px; font-weight: 600; color: #38bdf8; }
                        p { margin: 0; font-size: 14px; color: #94a3b8; line-height: 1.5; }
                        .footer { margin-top: 15px; font-size: 11px; color: #64748b; font-style: italic; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h2>Vincular Merma Cero</h2>
                        <p>Abre WhatsApp en tu celular (Chip 5575049383), ve a Dispositivos Vinculados y escanea esta imagen:</p>
                        <img src="${qrImage}" />
                        <p class="footer">Esta página se actualizará o cerrará una vez que se conecte el bot.</p>
                    </div>
                </body>
            </html>
        `);
    } catch (err) {
        res.status(500).send('Error al generar código QR: ' + err.message);
    }
});

app.get('/qr/status', (req, res) => {
    res.json({ ready: client.info ? true : false });
});

app.get('/', (req, res) => {
    res.send('WhatsApp Gateway Online');
});
app.listen(PORT, () => {
    console.log(`Pasarela HTTP escuchando en el puerto ${PORT}`);
    client.initialize();
});
