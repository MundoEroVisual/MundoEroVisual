const express = require('express');
const fs = require('fs');
const path = require('path');
const multer = require('multer');
const app = express();

const ADMIN_USER = 'admin';
const ADMIN_PASS = '12232931';

// Middlewares estándar
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static('public'));

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

// Ruta para obtener todas las novelas
app.get('/api/novelas', (req, res) => {
  const novelasPath = path.join(__dirname, 'data', 'novelas.json');
  if (!fs.existsSync(novelasPath)) return res.json([]);
  const novelas = JSON.parse(fs.readFileSync(novelasPath, 'utf8'));
  res.json(novelas);
});

// Ruta para login de admin
app.post('/api/admin-login', (req, res) => {
  const { user, pass } = req.body;
  if (user === ADMIN_USER && pass === ADMIN_PASS) {
    res.json({ success: true });
  } else {
    res.json({ success: false });
  }
});

// Middleware simple para autenticar admin en rutas protegidas
function checkAdmin(req, res, next) {
  // Si viene por multipart/form-data, los datos están en req.body
  const { user, pass } = req.body;
  if (user === ADMIN_USER && pass === ADMIN_PASS) {
    next();
  } else {
    res.status(401).json({ error: 'No autorizado' });
  }
}

// Ruta para añadir una novela (solo admin, con imágenes, sin límite en spoilers)
app.post('/api/novelas',
  upload.fields([
    { name: 'portada', maxCount: 1 },
    { name: 'spoilers' } // sin maxCount = sin límite de imágenes
  ]),
  checkAdmin,
  (req, res) => {
    const novelasPath = path.join(__dirname, 'data', 'novelas.json');
    let novelas = [];
    if (fs.existsSync(novelasPath)) {
      novelas = JSON.parse(fs.readFileSync(novelasPath, 'utf8'));
    }
    const { id, titulo, desc, generos, android, pc } = req.body;
    if (!id || !titulo) {
      return res.status(400).json({ error: 'Datos de novela incompletos' });
    }
    const portada = req.files['portada'] ? '/imagenes/' + req.files['portada'][0].filename : '';
    // Aquí aceptas todas las imágenes subidas en spoilers (pueden ser 1, 10 o 100)
    const spoilers = req.files['spoilers'] ? req.files['spoilers'].map(f => '/imagenes/' + f.filename) : [];
    const novela = {
      id,
      titulo,
      desc,
      generos: JSON.parse(generos),
      portada,
      spoilers,
      android,
      pc
    };
    novelas.push(novela);
    fs.writeFileSync(novelasPath, JSON.stringify(novelas, null, 2));
    res.json({ success: true, novelas });
  }
);

// Ruta para eliminar una novela por índice (solo admin)
app.delete('/api/novelas/:index', checkAdmin, (req, res) => {
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

// <<<<<<<< CONTADOR de visitas >>>>>>>>
const contadorRouter = require('./contador');
app.use(contadorRouter);

// <<<<<<<< SIEMPRE AL FINAL >>>>>>>>
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log('Servidor listo en puerto ' + PORT));