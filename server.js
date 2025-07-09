<<<<<<< HEAD


// ================== IMPORTS Y APP INIT AL PRINCIPIO ==================
// ================== IMPORTS Y APP INIT AL PRINCIPIO ==================
const dotenv = require('dotenv');
dotenv.config();
=======
>>>>>>> 9653951fa63fcf97460d92dfb69bc561f71a1352
const express = require('express');
const fs = require('fs');
const path = require('path');
const multer = require('multer');
const bcrypt = require('bcrypt');
const cookieParser = require('cookie-parser');
const crypto = require('crypto');
<<<<<<< HEAD
const fetch = require('node-fetch');
const archiver = require('archiver');
const bodyParser = require('body-parser');
// const { exec } = require('child_process'); // Ya está importado arriba, no es necesario duplicar

// --- Configuración para GitHub API ---
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const GITHUB_OWNER = process.env.GITHUB_OWNER;
const GITHUB_REPO = process.env.GITHUB_REPO;
const GITHUB_BRANCH = process.env.GITHUB_BRANCH || 'main';

// ================== ADMIN SESSIONS GLOBAL ==================
let adminSessions = {};

const ADMIN_USER = 'admin';
const ADMIN_PASS = '12232931';

// Middlewares estándar
const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static('public'));
app.use(cookieParser());
// ================== FIN IMPORTS Y APP INIT ==================

// Ruta de traducción usando LibreTranslate con logs detallados
app.post('/api/traducir', async (req, res) => {
  try {
    const { texto, target } = req.body;
    console.log('[TRADUCIR] Recibido:', { texto, target });
    if (!texto || !target) {
      console.log('[TRADUCIR] Faltan datos');
      return res.status(400).json({ error: 'Faltan datos' });
    }
    let source = 'auto';
    // Usar la instancia pública recomendada y agregar api_key vacío por compatibilidad
    const response = await fetch('https://libretranslate.com/translate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        q: texto,
        source,
        target,
        format: 'text',
        api_key: ''
      })
    });
    const data = await response.json();
    console.log('[TRADUCIR] Respuesta LibreTranslate:', data);
    if (data && data.translatedText) {
      res.json({ traduccion: data.translatedText });
    } else {
      console.log('[TRADUCIR] No se pudo traducir, respuesta:', data);
      res.status(500).json({ error: 'No se pudo traducir', libretranslate: data });
    }
  } catch (e) {
    console.error('[TRADUCIR] Error:', e);
    res.status(500).json({ error: e.message });
  }
});

// --- RUTA DE MEMBRESÍA DE USUARIO ---
// --- RUTA DE MEMBRESÍA DE USUARIO ---
app.get('/api/usuario-membresia', (req, res) => {
  const usuario = req.query.usuario;
  if (!usuario) return res.json({ membresia_activa: false });
  const USUARIOS_PATH = path.join(__dirname, 'data', 'usuario.json');
  let usuarios = [];
  if (fs.existsSync(USUARIOS_PATH)) {
    usuarios = JSON.parse(fs.readFileSync(USUARIOS_PATH, 'utf8'));
  }
  const user = usuarios.find(u => u.usuario === usuario);
  if (!user || !user.premium_expira) return res.json({ membresia_activa: false });
  const expira = new Date(user.premium_expira);
  const ahora = new Date();
  if (expira > ahora) {
    return res.json({ membresia_activa: true, membresia_expira: user.premium_expira });
  } else {
    return res.json({ membresia_activa: false });
  }
});
// ...existing code...

// --- PAYPAL IPN AUTOMÁTICO ---
// Ruta para recibir notificaciones IPN de PayPal
app.post('/api/paypal-ipn', async (req, res) => {
  // Paso 1: reenviar los datos a PayPal para validación
  let params = new URLSearchParams({ cmd: '_notify-validate', ...req.body });
  const response = await fetch('https://ipnpb.paypal.com/cgi-bin/webscr', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: params.toString()
  });
  const text = await response.text();
  if (text !== 'VERIFIED') {
    return res.status(400).send('IPN no verificado');
  }
  // Paso 2: comprobar el pago
  const paymentStatus = req.body.payment_status;
  const receiverEmail = req.body.receiver_email;
  const subscrEmail = req.body.payer_email;
  const custom = req.body.custom || '';
  // Usa variable de entorno o directamente tu correo de PayPal
  const TU_CORREO_PAYPAL = process.env.PAYPAL_EMAIL || 'albersonquezada@gmail.com';
  if (paymentStatus === 'Completed' && receiverEmail === TU_CORREO_PAYPAL) {
    // Buscar usuario por email (o por custom si lo usas)
    const USUARIOS_PATH = path.join(__dirname, 'data', 'usuario.json');
    let usuarios = [];
    if (fs.existsSync(USUARIOS_PATH)) {
      usuarios = JSON.parse(fs.readFileSync(USUARIOS_PATH, 'utf8'));
    }
    // Buscar por email (debe coincidir con el email de registro)
    let userIdx = usuarios.findIndex(u => u.usuario === subscrEmail);
    if (userIdx === -1 && custom) {
      userIdx = usuarios.findIndex(u => u.usuario === custom);
    }
    if (userIdx !== -1) {
      // Lógica de expiración mensual
      const ahora = new Date();
      let nuevaExpiracion = new Date(ahora);
      // Si ya tenía premium y expiración futura, suma 1 mes a la expiración actual
      if (usuarios[userIdx].premium_expira && new Date(usuarios[userIdx].premium_expira) > ahora) {
        nuevaExpiracion = new Date(usuarios[userIdx].premium_expira);
        nuevaExpiracion.setMonth(nuevaExpiracion.getMonth() + 1);
      } else {
        nuevaExpiracion.setMonth(nuevaExpiracion.getMonth() + 1);
      }
      usuarios[userIdx].premium = true;
      usuarios[userIdx].premium_expira = nuevaExpiracion.toISOString();
      fs.writeFileSync(USUARIOS_PATH, JSON.stringify(usuarios, null, 2));
      return res.status(200).send('Usuario actualizado a premium con expiración');
    }
    return res.status(404).send('Usuario no encontrado');
  }
  res.status(200).send('IPN recibido');
});
=======
const dotenv = require('dotenv');
const fetch = require('node-fetch');
>>>>>>> 9653951fa63fcf97460d92dfb69bc561f71a1352

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

<<<<<<< HEAD
// Ruta para login de admin (ahora con cookie segura)
// Nuevo login de admin: usa usuarios.json y bcrypt igual que el login normal
app.post('/api/admin-login', async (req, res) => {
  const { user, pass } = req.body;
  const USUARIOS_PATH = path.join(__dirname, 'data', 'usuario.json');
  let usuarios = [];
  if (fs.existsSync(USUARIOS_PATH)) {
    usuarios = JSON.parse(fs.readFileSync(USUARIOS_PATH, 'utf8'));
  }
  const admin = usuarios.find(u => u.usuario === user && u.admin);
  if (!admin) return res.json({ success: false });
  const ok = await bcrypt.compare(pass, admin.password);
  if (!ok) return res.json({ success: false });
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
=======
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
>>>>>>> 9653951fa63fcf97460d92dfb69bc561f71a1352
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
<<<<<<< HEAD
=======
const { exec } = require('child_process');
>>>>>>> 9653951fa63fcf97460d92dfb69bc561f71a1352
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
<<<<<<< HEAD
    // Validar y limpiar campos
    let { id, titulo, desc, generos, portada, spoilers, android, pc, estado, peso, enlace_premium, android_vip } = req.body;
    // No aceptar campos como 'enlace_android'
    if (req.body.enlace_android) {
      android = req.body.enlace_android; // Si por error viene, lo usamos como android
    }
    // Validar campo estado obligatorio
    if (!estado || typeof estado !== 'string' || !estado.trim()) {
      return res.status(400).json({ error: 'El campo "estado" es obligatorio' });
    }
=======
    const { id, titulo, desc, generos, portada, spoilers, android, pc } = req.body;
>>>>>>> 9653951fa63fcf97460d92dfb69bc561f71a1352
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
<<<<<<< HEAD
      android_vip,
      pc,
      estado,
      peso,
      enlace_premium // <-- Añadido el campo enlace_premium
=======
      pc
>>>>>>> 9653951fa63fcf97460d92dfb69bc561f71a1352
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

<<<<<<< HEAD
// --- USUARIOS Y CONTADOR: LOCAL ---
const USUARIOS_PATH = path.join(__dirname, 'data', 'usuario.json');
=======
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
>>>>>>> 9653951fa63fcf97460d92dfb69bc561f71a1352
const CONTADOR_PATH = path.join(__dirname, 'data', 'contador.json');

// Rutas para registro y login de usuario normal

// Registro de usuario
<<<<<<< HEAD
// Registro de usuario (ahora con avatar y apodo opcionales)
app.post('/api/register', async (req, res) => {
  const { usuario, password, avatar, apodo } = req.body;
  if (!usuario || !password) return res.status(400).json({ error: 'Faltan datos' });
  try {
    console.log('Intentando guardar usuarios en:', USUARIOS_PATH);
    // Asegura que la carpeta data existe
    const dataDir = path.dirname(USUARIOS_PATH);
    if (!fs.existsSync(dataDir)) {
      fs.mkdirSync(dataDir, { recursive: true });
      console.log('Carpeta creada:', dataDir);
    }
=======
app.post('/api/register', async (req, res) => {
  const { usuario, password } = req.body;
  if (!usuario || !password) return res.status(400).json({ error: 'Faltan datos' });
  try {
>>>>>>> 9653951fa63fcf97460d92dfb69bc561f71a1352
    let usuarios = [];
    if (fs.existsSync(USUARIOS_PATH)) {
      usuarios = JSON.parse(fs.readFileSync(USUARIOS_PATH, 'utf8'));
    }
    if (usuarios.find(u => u.usuario === usuario)) {
      return res.status(400).json({ error: 'Usuario ya existe' });
    }
    const hash = await bcrypt.hash(password, 10);
<<<<<<< HEAD
    usuarios.push({
      usuario,
      password: hash,
      admin: false,
      avatar: avatar || '',
      apodo: apodo || '',
      premium: false,
      premium_expira: null
    });
    fs.writeFileSync(USUARIOS_PATH, JSON.stringify(usuarios, null, 2));
    console.log('Usuarios guardados correctamente. Total:', usuarios.length);
=======
    usuarios.push({ usuario, password: hash, admin: false });
    fs.writeFileSync(USUARIOS_PATH, JSON.stringify(usuarios, null, 2));
>>>>>>> 9653951fa63fcf97460d92dfb69bc561f71a1352
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
<<<<<<< HEAD
    // Forzar avatar y apodo por defecto si no existen
    let avatar = user.avatar;
    if (!avatar || avatar.trim() === '') {
      avatar = `https://api.dicebear.com/7.x/identicon/svg?seed=${encodeURIComponent(user.usuario)}`;
    }
    let apodo = user.apodo;
    if (!apodo || apodo.trim() === '') {
      apodo = user.usuario.charAt(0).toUpperCase() + user.usuario.slice(1);
    }
    res.json({ success: true, usuario: user.usuario, admin: !!user.admin, avatar, apodo });
=======
    res.json({ success: true, usuario: user.usuario, admin: !!user.admin });
>>>>>>> 9653951fa63fcf97460d92dfb69bc561f71a1352
  } catch (e) {
    console.error('Error login:', e);
    res.status(500).json({ error: e.message });
  }
});
<<<<<<< HEAD
// Endpoint para actualizar avatar y apodo del usuario
app.post('/api/usuario/update', async (req, res) => {
  const { usuario, avatar, apodo } = req.body;
  if (!usuario) return res.status(400).json({ error: 'Falta usuario' });
  try {
    let usuarios = [];
    if (fs.existsSync(USUARIOS_PATH)) {
      usuarios = JSON.parse(fs.readFileSync(USUARIOS_PATH, 'utf8'));
    }
    const idx = usuarios.findIndex(u => u.usuario === usuario);
    if (idx === -1) return res.status(404).json({ error: 'Usuario no encontrado' });
    if (avatar !== undefined) usuarios[idx].avatar = avatar;
    if (apodo !== undefined) usuarios[idx].apodo = apodo;
    fs.writeFileSync(USUARIOS_PATH, JSON.stringify(usuarios, null, 2));
    res.json({ success: true, usuario: usuarios[idx] });
  } catch (e) {
    console.error('Error update usuario:', e);
    res.status(500).json({ error: e.message });
  }
});

// Ruta para saber si ya hay admin creado
app.get('/api/hay-admin', (req, res) => {
  const USUARIOS_PATH = path.join(__dirname, 'data', 'usuario.json');
=======

// Ruta para saber si ya hay admin creado
app.get('/api/hay-admin', (req, res) => {
  const USUARIOS_PATH = path.join(__dirname, 'data', 'usuarios.json');
>>>>>>> 9653951fa63fcf97460d92dfb69bc561f71a1352
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
<<<<<<< HEAD
  const USUARIOS_PATH = path.join(__dirname, 'data', 'usuario.json');
=======
  const USUARIOS_PATH = path.join(__dirname, 'data', 'usuarios.json');
>>>>>>> 9653951fa63fcf97460d92dfb69bc561f71a1352
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

<<<<<<< HEAD


=======
>>>>>>> 9653951fa63fcf97460d92dfb69bc561f71a1352
// Servir novela.html directamente para rutas /novela.html (debe ir antes del catch-all)
app.get('/novela.html', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'novela.html'));
});

<<<<<<< HEAD
// Servir novelasvipdetalle.html solo para usuarios premium y con membresía activa
app.get('/novelasvipdetalle.html', (req, res) => {
  try {
    const usuario = req.cookies && req.cookies.usuario;
    if (!usuario) return res.redirect('/index.html');
    const USUARIOS_PATH = path.join(__dirname, 'data', 'usuario.json');
    if (!fs.existsSync(USUARIOS_PATH)) return res.redirect('/index.html');
    const usuarios = JSON.parse(fs.readFileSync(USUARIOS_PATH, 'utf8'));
    const user = usuarios.find(u => u.usuario === usuario);
    const ahora = new Date();
    if (!user || !user.premium || !user.premium_expira || new Date(user.premium_expira) < ahora) {
      // Si expiró, cancelar premium automáticamente
      if (user && user.premium) {
        user.premium = false;
        user.premium_expira = null;
        fs.writeFileSync(USUARIOS_PATH, JSON.stringify(usuarios, null, 2));
      }
      return res.redirect('/index.html');
    }
    res.sendFile(path.join(__dirname, 'public', 'novelasvipdetalle.html'));
  } catch (e) {
    res.redirect('/index.html');
  }
});

// Servir eroverse-vip.html para /eroversevip y /eroversevip/ (con o sin barra final)
app.get(['/eroversevip', '/eroversevip/'], (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'eroversevip.html'));
});

=======
>>>>>>> 9653951fa63fcf97460d92dfb69bc561f71a1352
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

// Editar novela por slug (id)
app.put('/api/novelas/:slug', checkAdmin, async (req, res) => {
  try {
    const slug = req.params.slug;
    let novelas = await getJsonFromGitHub('data/novelas-1.json');
    if (!Array.isArray(novelas)) novelas = [];
    const idx = novelas.findIndex(n => n.id === slug);
    if (idx === -1) {
      return res.status(404).json({ error: 'Novela no encontrada' });
    }
<<<<<<< HEAD
    // Actualizar solo los campos permitidos
    const campos = ['titulo','desc','generos','portada','spoilers','android','android_vip','pc','estado','peso','enlace_premium'];
    for (const campo of campos) {
      if (req.body[campo] !== undefined) {
        novelas[idx][campo] = req.body[campo];
      }
    }
    const result = await updateFileOnGitHub('data/novelas-1.json', novelas);
    if (result && result.commit) {
      res.json({ success: true, novela: novelas[idx] });
=======
    // Actualizar todos los campos recibidos
    const nuevaNovela = { ...novelas[idx], ...req.body };
    // Si se envía generos como string, parsear
    if (typeof nuevaNovela.generos === 'string') {
      try { nuevaNovela.generos = JSON.parse(nuevaNovela.generos); } catch {}
    }
    // Si se envía spoilers como string, parsear
    if (typeof nuevaNovela.spoilers === 'string') {
      nuevaNovela.spoilers = nuevaNovela.spoilers.split(',').map(s => s.trim()).filter(Boolean);
    }
    novelas[idx] = nuevaNovela;
    const result = await updateFileOnGitHub('data/novelas-1.json', novelas);
    if (result && result.commit) {
      res.json({ success: true, novela: nuevaNovela });
>>>>>>> 9653951fa63fcf97460d92dfb69bc561f71a1352
    } else {
      res.status(500).json({ error: 'No se pudo actualizar en GitHub', github: result });
    }
  } catch (e) {
    console.error('Error al editar novela:', e);
    res.status(500).json({ error: e.message });
  }
});

// Borrar novela por slug (id)
app.delete('/api/novelas/:slug', checkAdmin, async (req, res) => {
  try {
    const slug = req.params.slug;
    let novelas = await getJsonFromGitHub('data/novelas-1.json');
    if (!Array.isArray(novelas)) novelas = [];
    const idx = novelas.findIndex(n => n.id === slug);
    if (idx === -1) {
      return res.status(404).json({ error: 'Novela no encontrada' });
    }
    const novelaEliminada = novelas.splice(idx, 1)[0];
    const result = await updateFileOnGitHub('data/novelas-1.json', novelas);
    if (result && result.commit) {
      res.json({ success: true, novela: novelaEliminada });
    } else {
      res.status(500).json({ error: 'No se pudo actualizar en GitHub', github: result });
    }
  } catch (e) {
    console.error('Error al borrar novela:', e);
    res.status(500).json({ error: e.message });
  }
});
<<<<<<< HEAD

app.post('/api/descargar-imagenes', express.json(), async (req, res) => {
  try {
    const { imagenes, info, nombreCarpeta, id } = req.body; // nombreCarpeta: nombre seguro de la carpeta
    if (!Array.isArray(imagenes)) return res.status(400).json({ error: 'Faltan imágenes' });
    // Usar nombre seguro para la carpeta
    let carpeta = nombreCarpeta || 'juego';
    carpeta = carpeta.replace(/[^a-zA-Z0-9\-_ ]/g, '').trim() || 'juego';
    res.setHeader('Content-Type', 'application/zip');
    res.setHeader('Content-Disposition', `attachment; filename="${carpeta}.zip"`);
    const archive = archiver('zip', { zlib: { level: 9 } });
    archive.pipe(res);
    // Agregar info.txt dentro de la carpeta
    let infoFinal = info || '';
    // Obtener el peso de la novela del campo datos.peso si existe
    let peso = req.body.peso;
    // Si no viene en el body, intentar buscarlo en datos (novela)
    if (!peso && id) {
      try {
        // Buscar la novela por id en el JSON de novelas
        const novelas = await getJsonFromGitHub('data/novelas-1.json');
        const novela = Array.isArray(novelas) ? novelas.find(n => n.id === id) : null;
        if (novela && novela.peso) peso = novela.peso;
      } catch {}
    }
    // Si no está la línea Peso: en info.txt y tenemos el peso, añadirlo
    if (peso) {
      // Eliminar cualquier línea previa de Peso: para evitar duplicados
      infoFinal = infoFinal.replace(/\n?Peso:.*(\n|$)/gi, '');
      infoFinal += `\nPeso: ${peso}`;
    }
    archive.append(infoFinal.trim(), { name: `${carpeta}/info.txt` });

    // --- ELIMINADO: generación de guion_youtube.txt ---

    // Descargar y agregar imágenes dentro de la carpeta
    for (const img of imagenes) {
      try {
        const response = await fetch(img.url);
        if (!response.ok) throw new Error('No se pudo descargar ' + img.url);
        archive.append(response.body, { name: `${carpeta}/${img.nombre || 'imagen.jpg'}` });
      } catch (e) {
        archive.append(`Error al descargar: ${img.url}\n`, { name: `${carpeta}/error_${img.nombre || 'imagen.txt'}` });
      }
    }
    archive.finalize();
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});
=======
>>>>>>> 9653951fa63fcf97460d92dfb69bc561f71a1352
