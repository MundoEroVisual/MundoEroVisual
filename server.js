const express = require('express');
const fs = require('fs');
const path = require('path');
const multer = require('multer');
const bcrypt = require('bcrypt');
const cookieParser = require('cookie-parser');
const crypto = require('crypto');
const dotenv = require('dotenv');
const fetch = require('node-fetch');

// Leer archivo JSON directamente desde GitHub
async function getJsonFromGitHub(githubPath) {
  const url = `https://raw.githubusercontent.com/${GITHUB_OWNER}/${GITHUB_REPO}/${GITHUB_BRANCH}/${githubPath}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('No se pudo leer el archivo de GitHub');
  return await res.json();
}

// Obtener SHA del archivo en GitHub
async function getFileSha(githubPath) {
  const url = `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/contents/${githubPath}?ref=${GITHUB_BRANCH}`;
  const res = await fetch(url, {
    headers: {
      Authorization: `token ${GITHUB_TOKEN}`,
      Accept: 'application/vnd.github+json',
    }
  });
  const data = await res.json();
  return data.sha;
}

// Actualizar archivo en GitHub
async function updateFileOnGitHub(githubPath, newContent) {
  const sha = await getFileSha(githubPath);
  const url = `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/contents/${githubPath}`;
  const body = {
    message: 'Actualización automática desde la app',
    content: Buffer.from(JSON.stringify(newContent, null, 2)).toString('base64'),
    sha: sha,
    branch: GITHUB_BRANCH
  };
  const res = await fetch(url, {
    method: 'PUT',
    headers: {
      Authorization: `token ${GITHUB_TOKEN}`,
      Accept: 'application/vnd.github+json',
    },
    body: JSON.stringify(body)
  });
  return await res.json();
}

dotenv.config();

const ADMIN_USER = 'admin';
const ADMIN_PASS = '12232931';

// --- Configuración para GitHub API ---
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const GITHUB_OWNER = process.env.GITHUB_OWNER;
const GITHUB_REPO = process.env.GITHUB_REPO;
const GITHUB_BRANCH = process.env.GITHUB_BRANCH || 'main';

// Middlewares estándar
const app = express();
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

// Ruta para obtener todas las novelas (lee desde GitHub)
app.get('/api/novelas', async (req, res) => {
  try {
    let novelas = await getJsonFromGitHub('data/novelas-1.json');
    if (!Array.isArray(novelas)) novelas = [];
    res.json(novelas);
  } catch (e) {
    console.error('Error al leer novelas de GitHub:', e);
    res.status(500).json({ error: e.message });
  }
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

// Nueva ruta para añadir novela y dividir archivos
app.post('/api/novelas', async (req, res) => {
  try {
    let novelas = await getJsonFromGitHub('data/novelas-1.json');
    if (!Array.isArray(novelas)) novelas = [];
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
    const result = await updateFileOnGitHub('data/novelas-1.json', novelas);
    if (result && result.commit) {
      res.json({ success: true, novelas });
    } else {
      console.error('GitHub API error (novelas):', result);
      res.status(500).json({ error: 'No se pudo actualizar novelas en GitHub', github: result });
    }
  } catch (e) {
    console.error('Error novelas:', e);
    res.status(500).json({ error: e.message });
  }
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

// --- USUARIOS Y CONTADOR: LOCAL ---
const USUARIOS_PATH = path.join(__dirname, 'data', 'usuarios.json');
const CONTADOR_PATH = path.join(__dirname, 'data', 'contador.json');

// Rutas para registro y login de usuario normal

// Registro de usuario
app.post('/api/register', async (req, res) => {
  const { usuario, password } = req.body;
  if (!usuario || !password) return res.status(400).json({ error: 'Faltan datos' });
  try {
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
  } catch (e) {
    console.error('Error register:', e);
    res.status(500).json({ error: e.message });
  }
});

// Login de usuario
app.post('/api/login', async (req, res) => {
  const { usuario, password } = req.body;
  if (!usuario || !password) return res.status(400).json({ error: 'Faltan datos' });
  try {
    let usuarios = [];
    if (fs.existsSync(USUARIOS_PATH)) {
      usuarios = JSON.parse(fs.readFileSync(USUARIOS_PATH, 'utf8'));
    }
    const user = usuarios.find(u => u.usuario === usuario);
    if (!user) return res.status(400).json({ error: 'Usuario o contraseña incorrectos' });
    const ok = await bcrypt.compare(password, user.password);
    if (!ok) return res.status(400).json({ error: 'Usuario o contraseña incorrectos' });
    res.json({ success: true, usuario: user.usuario, admin: !!user.admin });
  } catch (e) {
    console.error('Error login:', e);
    res.status(500).json({ error: e.message });
  }
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

// Servir novela.html directamente para rutas /novela.html (debe ir antes del catch-all)
app.get('/novela.html', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'novela.html'));
});

// <<<<<<<< SIEMPRE AL FINAL >>>>>>>>
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Ruta para forzar commit y push de todos los archivos de novelas
app.post('/guardar-y-sincronizar', async (req, res) => {
  const dataDir = path.join(__dirname, 'data');
  const files = fs.readdirSync(dataDir).filter(f => f.startsWith('novelas-') && f.endsWith('.json'));
  let resultados = [];
  for (const file of files) {
    const filePath = path.join(dataDir, file);
    const content = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    try {
      const githubPath = `data/${file}`;
      await updateFileOnGitHub(githubPath, content);
      resultados.push({ file, status: 'ok' });
    } catch (e) {
      resultados.push({ file, status: 'error', error: e.message });
    }
  }
  res.json({ resultados });
});

// Ruta para sumar visita y guardar localmente
app.post('/api/sumar-visita', async (req, res) => {
  try {
    let data = { visitas: 0 };
    if (fs.existsSync(CONTADOR_PATH)) {
      data = JSON.parse(fs.readFileSync(CONTADOR_PATH, 'utf8'));
    }
    data.visitas = (data.visitas || 0) + 1;
    fs.writeFileSync(CONTADOR_PATH, JSON.stringify(data, null, 2));
    res.json({ ok: true, visitas: data.visitas });
  } catch (e) {
    console.error('Error sumar-visita:', e);
    res.status(500).json({ ok: false, error: e.message });
  }
});

// Ruta para obtener el número actual de visitas (local)
app.get('/api/visitas', async (req, res) => {
  try {
    let data = { visitas: 0 };
    if (fs.existsSync(CONTADOR_PATH)) {
      data = JSON.parse(fs.readFileSync(CONTADOR_PATH, 'utf8'));
    }
    res.json({ visitas: data.visitas });
  } catch (e) {
    console.error('Error obtener visitas:', e);
    res.status(500).json({ visitas: 0, error: e.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log('Servidor listo en puerto ' + PORT));