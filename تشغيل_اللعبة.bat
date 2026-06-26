const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 8080;
const FOLDER = __dirname;

const mimeTypes = {
    '.html': 'text/html; charset=utf-8',
    '.js': 'text/javascript',
    '.css': 'text/css',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon'
};

const server = http.createServer((req, res) => {
    // CORS
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }

    let urlPath = req.url === '/' ? '/physics_millionaire_game.html' : req.url;
    urlPath = urlPath.split('?')[0]; // إزالة query string

    // API: save_logo.php (محاكاة)
    if (urlPath === '/save_logo.php') {
        if (req.method === 'POST') {
            let body = '';
            req.on('data', chunk => body += chunk);
            req.on('end', () => {
                try {
                    const data = JSON.parse(body);
                    if (data.logo) {
                        fs.writeFileSync(path.join(FOLDER, 'logo_data.txt'), data.logo);
                        res.writeHead(200, { 'Content-Type': 'application/json' });
                        res.end(JSON.stringify({ success: true }));
                        return;
                    }
                } catch (e) {}
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: false }));
            });
            return;
        }
        if (req.method === 'GET') {
            const logoFile = path.join(FOLDER, 'logo_data.txt');
            const logo = fs.existsSync(logoFile) ? fs.readFileSync(logoFile, 'utf8') : '';
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ success: true, logo: logo }));
            return;
        }
    }

    // ملفات ثابتة
    const filePath = path.join(FOLDER, urlPath);
    const ext = path.extname(filePath).toLowerCase();

    if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
        res.writeHead(404, { 'Content-Type': 'text/html; charset=utf-8' });
        res.end('<h1>404 - Not Found</h1>');
        return;
    }

    const contentType = mimeTypes[ext] || 'application/octet-stream';
    const content = fs.readFileSync(filePath);

    res.writeHead(200, { 'Content-Type': contentType });
    res.end(content);
});

server.listen(PORT, () => {
    console.log(`🚀 Server OK - http://localhost:${PORT}/`);
    console.log('اضغط Ctrl+C لإيقاف');
});

// فتح المتصفح تلقائياً
const { exec } = require('child_process');
setTimeout(() => {
    exec(`start http://localhost:${PORT}/physics_millionaire_game.html`);
}, 1000);