const express = require('express');
const fs = require('fs');
const path = require('path');
const multer = require('multer');
const bcrypt = require('bcrypt');
const cookieParser = require('cookie-parser');
const crypto = require('crypto');
const app = express();

const ADMIN_USER = 'admin';
const ADMIN_PASS = '12232931';

// Middlewares estándar
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static('public'));
app.use(cookieParser());

// Configuración de Multer para guardar imágenes en /public/imagenes
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, path.join(__dirname, 'public', 'imagenes'));
  },
  filename: function (req, file, cb) {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, uniqueSuffix + '-' + file.originalname);
  }
});
const upload = multer({ storage: storage });

// Sesiones simples en memoria (para demo, usar Redis en producción)
const adminSessions = {};

// Ruta para login de admin (ahora con cookie segura)
app.post('/api/admin-login', (req, res) => {
  const { user, pass } = req.body;
  if (user === ADMIN_USER && pass === ADMIN_PASS) {
    // Generar token de sesión seguro
    const token = crypto.randomBytes(32).toString('hex');
    adminSessions[token] = { user, created: Date.now() };
    res.cookie('admin_token', token, {
      httpOnly: true,
      sameSite: 'strict',
      secure: false, // Cambia a true si usas HTTPS
      maxAge: 24 * 60 * 60 * 1000
    });
    res.json({ success: true });
  } else {
    res.json({ success: false });
  }
});

// Middleware seguro para autenticar admin
function checkAdmin(req, res, next) {
  const token = req.cookies.admin_token;
  if (token && adminSessions[token]) {
    next();
  } else {
    res.status(401).json({ error: 'No autorizado' });
  }
}

// Ruta para logout admin
app.post('/api/admin-logout', (req, res) => {
  const token = req.cookies.admin_token;
  if (token) delete adminSessions[token];
  res.clearCookie('admin_token');
  res.json({ success: true });
});

// Ruta para obtener todas las novelas
app.get('/api/novelas', (req, res) => {
  const novelasPath = path.join(__dirname, 'data', 'novelas.json');
  if (!fs.existsSync(novelasPath)) return res.json([]);
  const novelas = JSON.parse(fs.readFileSync(novelasPath, 'utf8'));
  res.json(novelas);
});

// Ruta HEAD pública para saber si es admin (200 si admin, 401 si no)
app.head('/api/novelas', (req, res) => {
  const token = req.cookies.admin_token;
  if (token && adminSessions[token]) {
    res.status(200).end();
  } else {
    res.status(401).end();
  }
});

// Función para hacer commit y push automático a GitHub
const { exec } = require('child_process');
function autoCommitAndPush(filePath, mensaje = 'Actualización automática de novelas') {
  exec(`git add "${filePath}" && git commit -m "${mensaje}" && git push`, { cwd: __dirname }, (error, stdout, stderr) => {
    if (error) {
      console.error('Error al hacer commit/push automático:', error);
    } else {
      console.log('Commit y push automático realizado:', stdout);
    }
  });
}

// Ruta para añadir una novela (ahora solo acepta enlaces, no archivos)
app.post('/api/novelas', (req, res) => {
  const novelasPath = path.join(__dirname, 'data', 'novelas.json');
  let novelas = [];
  if (fs.existsSync(novelasPath)) {
    novelas = JSON.parse(fs.readFileSync(novelasPath, 'utf8'));
  }
  const { id, titulo, desc, generos, portada, spoilers, android, pc } = req.body;
  if (!id || !titulo || !portada) {
    return res.status(400).json({ error: 'Datos de novela incompletos' });
  }
  const novela = {
    id,
    titulo,
    desc,
    generos: Array.isArray(generos) ? generos : JSON.parse(generos),
    portada,
    spoilers: Array.isArray(spoilers) ? spoilers : (typeof spoilers === 'string' ? spoilers.split(',').map(s => s.trim()).filter(Boolean) : []),
    android,
    pc
  };
  novelas.push(novela);
  fs.writeFileSync(novelasPath, JSON.stringify(novelas, null, 2));
  // Commit y push automático
  autoCommitAndPush(novelasPath, 'Nueva novela añadida');
  res.json({ success: true, novelas });
});

// Ruta para eliminar una novela por índice (sin admin)
app.delete('/api/novelas/:index', (req, res) => {
  const novelasPath = path.join(__dirname, 'data', 'novelas.json');
  let novelas = [];
  if (fs.existsSync(novelasPath)) {
    novelas = JSON.parse(fs.readFileSync(novelasPath, 'utf8'));
  }
  const idx = parseInt(req.params.index, 10);
  if (isNaN(idx) || idx < 0 || idx >= novelas.length) {
    return res.status(400).json({ error: 'Índice inválido' });
  }
  novelas.splice(idx, 1);
  fs.writeFileSync(novelasPath, JSON.stringify(novelas, null, 2));
  res.json({ success: true, novelas });
});

// Rutas para registro y login de usuario normal
const USUARIOS_PATH = path.join(__dirname, 'data', 'usuarios.json');

// Registro de usuario
app.post('/api/register', async (req, res) => {
  const { usuario, password } = req.body;
  if (!usuario || !password) return res.status(400).json({ error: 'Faltan datos' });
  let usuarios = [];
  if (fs.existsSync(USUARIOS_PATH)) {
    usuarios = JSON.parse(fs.readFileSync(USUARIOS_PATH, 'utf8'));
  }
  if (usuarios.find(u => u.usuario === usuario)) {
    return res.status(400).json({ error: 'Usuario ya existe' });
  }
  const hash = await bcrypt.hash(password, 10);
  usuarios.push({ usuario, password: hash, admin: false });
  fs.writeFileSync(USUARIOS_PATH, JSON.stringify(usuarios, null, 2));
  res.json({ success: true });
});

// Login de usuario
app.post('/api/login', async (req, res) => {
  const { usuario, password } = req.body;
  if (!usuario || !password) return res.status(400).json({ error: 'Faltan datos' });
  let usuarios = [];
  if (fs.existsSync(USUARIOS_PATH)) {
    usuarios = JSON.parse(fs.readFileSync(USUARIOS_PATH, 'utf8'));
  }
  const user = usuarios.find(u => u.usuario === usuario);
  if (!user) return res.status(400).json({ error: 'Usuario o contraseña incorrectos' });
  const ok = await bcrypt.compare(password, user.password);
  if (!ok) return res.status(400).json({ error: 'Usuario o contraseña incorrectos' });
  res.json({ success: true, usuario: user.usuario, admin: !!user.admin });
});

// Ruta para saber si ya hay admin creado
app.get('/api/hay-admin', (req, res) => {
  const USUARIOS_PATH = path.join(__dirname, 'data', 'usuarios.json');
  let usuarios = [];
  if (fs.existsSync(USUARIOS_PATH)) {
    usuarios = JSON.parse(fs.readFileSync(USUARIOS_PATH, 'utf8'));
  }
  const hayAdmin = usuarios.some(u => u.admin);
  res.json({ hayAdmin });
});

// Ruta para registrar admin (solo si no existe)
app.post('/api/registrar-admin', async (req, res) => {
  const { usuario, password } = req.body;
  if (!usuario || !password) return res.status(400).json({ error: 'Faltan datos' });
  const USUARIOS_PATH = path.join(__dirname, 'data', 'usuarios.json');
  let usuarios = [];
  if (fs.existsSync(USUARIOS_PATH)) {
    usuarios = JSON.parse(fs.readFileSync(USUARIOS_PATH, 'utf8'));
  }
  if (usuarios.some(u => u.admin)) {
    return res.status(400).json({ error: 'Ya existe un admin' });
  }
  if (usuarios.find(u => u.usuario === usuario)) {
    return res.status(400).json({ error: 'Usuario ya existe' });
  }
  const hash = await bcrypt.hash(password, 10);
  usuarios.push({ usuario, password: hash, admin: true });
  fs.writeFileSync(USUARIOS_PATH, JSON.stringify(usuarios, null, 2));
  res.json({ success: true });
});

// Ruta simple para /ping
app.get('/ping', (req, res) => {
  res.json({ ok: true });
});

// <<<<<<<< CONTADOR de visitas >>>>>>>>
const contadorRouter = require('./contador');
app.use(contadorRouter);

// <<<<<<<< SIEMPRE AL FINAL >>>>>>>>
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log('Servidor listo en puerto ' + PORT));