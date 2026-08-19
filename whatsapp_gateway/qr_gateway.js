const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const QRCode = require('qrcode');
const axios = require('axios');
const express = require('express');
const fs = require('fs');
const path = require('path');
const app = express();

// Captura de Logs para diagnóstico remoto en contenedores
const containerLogs = [];
const originalLog = console.log;
const originalError = console.error;
const originalWarn = console.warn;

console.log = function(...args) {
    containerLogs.push(`[LOG] ${new Date().toISOString()} - ${args.map(a => typeof a === 'object' ? JSON.stringify(a) : String(a)).join(' ')}`);
    if (containerLogs.length > 500) containerLogs.shift();
    originalLog.apply(console, args);
};

console.error = function(...args) {
    containerLogs.push(`[ERROR] ${new Date().toISOString()} - ${args.map(a => typeof a === 'object' ? JSON.stringify(a) : String(a)).join(' ')}`);
    if (containerLogs.length > 500) containerLogs.shift();
    originalError.apply(console, args);
};

console.warn = function(...args) {
    containerLogs.push(`[WARN] ${new Date().toISOString()} - ${args.map(a => typeof a === 'object' ? JSON.stringify(a) : String(a)).join(' ')}`);
    if (containerLogs.length > 500) containerLogs.shift();
    originalWarn.apply(console, args);
};

process.on('uncaughtException', (err) => {
    console.error(`UNCAUGHT EXCEPTION: ${err.message}\nStack: ${err.stack}`);
});

process.on('unhandledRejection', (reason, promise) => {
    const errorMsg = reason instanceof Error ? `${reason.message}\nStack: ${reason.stack}` : (typeof reason === 'object' ? JSON.stringify(reason) : String(reason));
    console.error('UNHANDLED REJECTION reason:', errorMsg);
});

// Podar quirúrgicamente el perfil de Chrome para dejar solo Cookies, Local Storage e IndexedDB, reduciendo drásticamente el consumo de RAM
function pruneProfile(dir) {
    if (!fs.existsSync(dir)) return;
    try {
        const files = fs.readdirSync(dir);
        for (const file of files) {
            const fullPath = path.join(dir, file);
            const stat = fs.lstatSync(fullPath);
            
            if (stat.isDirectory()) {
                // Eliminar solo carpetas de caché pesadas e innecesarias
                if (file === 'Cache' || file === 'Code Cache' || file === 'GPUCache') {
                    try {
                        fs.rmSync(fullPath, { recursive: true, force: true });
                        console.log(`Pruned directory: ${fullPath}`);
                    } catch (err) {
                        console.error(`Failed to prune directory ${fullPath}: ${err.message}`);
                    }
                } else {
                    pruneProfile(fullPath);
                }
            } else {
                // Eliminar archivos de bloqueo
                if (file === 'LOCK' || file === 'SingletonLock' || file === 'SingletonSocket') {
                    try {
                        fs.unlinkSync(fullPath);
                        console.log(`Pruned file: ${fullPath}`);
                    } catch (err) {
                        console.error(`Failed to delete file ${fullPath}: ${err.message}`);
                    }
                }
            }
        }
    } catch (e) {
        console.error(`Error pruning profile in ${dir}:`, e.message);
    }
}

pruneProfile('./.wwebjs_auth');

let latestQR = '';
let latestPairingCode = '';

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const PORT = process.env.PORT || 3000;
const WEBHOOK_URL = process.env.WEBHOOK_URL || 'https://merma-cero-backend-production.up.railway.app/webhook';

// Mapa en memoria para recordar los identificadores originales (ej. @lid o @c.us)
const userFromCache = new Map();
const MAX_CACHE_SIZE = 5000;

function cacheUser(phone, from) {
    if (userFromCache.size >= MAX_CACHE_SIZE) {
        const firstKey = userFromCache.keys().next().value;
        userFromCache.delete(firstKey);
    }
    userFromCache.set(phone, from);
}

const executablePath = process.env.PUPPETEER_EXECUTABLE_PATH || 'C:\\Users\\arqis\\.cache\\puppeteer\\chrome\\win64-146.0.7680.31\\chrome-win64\\chrome.exe';

const isLocal = process.env.LOCAL_RUN === 'true';

const client = new Client({
    authStrategy: new LocalAuth({
        dataPath: './.wwebjs_auth'
    }),
    puppeteer: {
        headless: isLocal ? false : 'new',
        executablePath: isLocal ? 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe' : executablePath,
        protocolTimeout: 300000,
        args: isLocal ? ['--no-sandbox', '--disable-setuid-sandbox'] : [
            '--no-sandbox', 
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--no-zygote',
            '--disable-renderer-backgrounding',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-ipc-flooding-protection',
            '--disable-blink-features=AutomationControlled'
        ]
    },
    userAgent: isLocal ? 
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36' : 
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    pairWithPhoneNumber: undefined
});

client.on('code', (code) => {
    latestPairingCode = code;
    console.log(`\n=================================\nCÓDIGO DE VINCULACIÓN WHATSAPP (code): ${code}\n=================================\n`);
});

client.on('pairing_code', (code) => {
    latestPairingCode = code;
    console.log(`\n=================================\nCÓDIGO DE VINCULACIÓN WHATSAPP (pairing_code): ${code}\n=================================\n`);
});

client.on('qr', (qr) => {
    latestQR = qr;
    console.log('\n=== ESCANEA ESTE CÓDIGO QR CON TU WHATSAPP ===\n');
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    console.log('¡Cliente de WhatsApp listo y conectado!');
});

client.on('disconnected', async (reason) => {
    console.warn(`[WhatsApp] Cliente desconectado. Razón: ${reason}`);
    latestQR = '';
    latestPairingCode = '';

    if (reason === 'LOGOUT') {
        console.log('[WhatsApp] Limpiando datos de sesión locales debido a LOGOUT...');
        try {
            if (fs.existsSync('./.wwebjs_auth')) {
                fs.rmSync('./.wwebjs_auth', { recursive: true, force: true });
                console.log('[WhatsApp] Datos de sesión eliminados con éxito.');
            }
        } catch (err) {
            console.error(`[WhatsApp] Error al eliminar datos de sesión: ${err.message}`);
        }
    }

    try {
        console.log('[WhatsApp] Destruyendo cliente anterior...');
        await client.destroy();
        console.log('[WhatsApp] Cliente destruido con éxito.');
    } catch (err) {
        console.error(`[WhatsApp] Error al destruir el cliente: ${err.message}`);
    }

    console.log('[WhatsApp] Re-inicializando cliente en 5 segundos...');
    setTimeout(() => {
        client.initialize();
    }, 5000);
});

client.on('message_create', async (msg) => {
    try {
        if (!msg || !msg.from) return;
        if (msg.fromMe) return; // Omitir mensajes enviados por el bot mismo
        if (msg.from.includes('@g.us') || msg.from.includes('@broadcast') || msg.from.includes('@newsletter')) return; // Omitir grupos, estados y canales

        console.log(`Mensaje detectado de ${msg.from}: ${msg.body}`);
        
        const senderNumber = msg.from.split('@')[0];
        const cleanPhone = '+' + senderNumber;
        cacheUser(cleanPhone, msg.from);

        const profileName = (msg._data && msg._data.notifyName) ? msg._data.notifyName : 'Comerciante';

        // Enviar la petición al webhook de FastAPI simulando el formato URL Form Encoded de Twilio
        const params = new URLSearchParams();
        params.append('From', `whatsapp:+${senderNumber}`);
        params.append('Body', msg.body || '');
        params.append('ProfileName', profileName);

        console.log(`Enviando mensaje al webhook de FastAPI (${WEBHOOK_URL})...`);
        const res = await axios.post(WEBHOOK_URL, params, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            timeout: 15000
        });
        console.log(`Webhook respondio exitosamente:`, res.status);
    } catch (err) {
        console.error('Error en el manejador de mensajes de la pasarela:', err.message, err.stack);
    }
});

app.post('/send', async (req, res) => {
    const { to, body } = req.body;
    if (!to || !body) {
        return res.status(400).json({ status: 'error', error: 'Parámetros obligatorios faltantes: to, body' });
    }
    try {
        const cleanTo = String(to).replace('whatsapp:', '').trim();
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
    if (latestPairingCode) {
        return res.send(`
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Vincular WhatsApp - Merma Cero</title>
                    <meta http-equiv="refresh" content="15">
                    <style>
                        body { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; background: #0f172a; color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
                        .container { background: #1e293b; padding: 40px; border-radius: 16px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3); text-align: center; max-width: 400px; border: 1px solid #334155; }
                        .code { font-size: 36px; font-weight: 700; color: #38bdf8; background: #0f172a; padding: 20px; border-radius: 12px; margin: 25px 0; letter-spacing: 4px; border: 1px dashed #38bdf8; font-family: monospace; }
                        h2 { margin: 0 0 10px 0; font-size: 22px; font-weight: 600; color: #38bdf8; }
                        p { margin: 0; font-size: 14px; color: #94a3b8; line-height: 1.5; }
                        .footer { margin-top: 20px; font-size: 11px; color: #64748b; font-style: italic; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h2>Vincular con Código</h2>
                        <p>Abre WhatsApp en tu celular (Chip 5575049383), ve a Dispositivos Vinculados, selecciona <strong>"Vincular con número de teléfono"</strong> (al final de tu pantalla) e ingresa este código:</p>
                        <div class="code">${latestPairingCode}</div>
                        <p class="footer">Esta página se actualizará o cerrará una vez que se conecte el bot.</p>
                    </div>
                </body>
            </html>
        `);
    }

    if (!latestQR) {
        return res.send(`
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Vincular WhatsApp - Merma Cero</title>
                    <meta http-equiv="refresh" content="5">
                    <style>
                        body { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; background: #0f172a; color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
                        .container { background: #1e293b; padding: 40px; border-radius: 16px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3); text-align: center; max-width: 400px; border: 1px solid #334155; }
                        h2 { margin: 0 0 10px 0; font-size: 20px; font-weight: 600; color: #e2e8f0; }
                        p { margin: 0; font-size: 14px; color: #94a3b8; line-height: 1.5; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h2>Inicializando canal seguro...</h2>
                        <p>Generando código de vinculación o QR de WhatsApp. Por favor espera, esta página se recargará automáticamente en unos segundos.</p>
                    </div>
                </body>
            </html>
        `);
    }
    try {
        const qrImage = await QRCode.toDataURL(latestQR);
        res.send(`
            <html>
                <head>
                    <title>Vincular WhatsApp - Merma Cero</title>
                    <meta http-equiv="refresh" content="15">
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

app.get('/qr/debug', async (req, res) => {
    try {
        const state = await client.getState().catch(e => 'error: ' + e.message);
        res.json({
            ready: client.info ? true : false,
            state: state,
            info: client.info || null,
            latestPairingCode: latestPairingCode || null,
            latestQR: latestQR ? 'present' : 'none'
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.get('/pairing-code', (req, res) => {
    res.json({ code: latestPairingCode || null });
});

app.get('/qr/logs', (req, res) => {
    res.type('text/plain').send(containerLogs.join('\n'));
});

app.get('/', (req, res) => {
    res.send('WhatsApp Gateway Online');
});
app.listen(PORT, () => {
    console.log(`Pasarela HTTP escuchando en el puerto ${PORT}`);
    client.initialize();
});
