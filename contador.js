const fs = require('fs');
const express = require('express');
const path = require('path');
const router = express.Router();

const file = path.join(__dirname, 'data', 'contador.json');

// Sumar una visita (debe llamarse en el frontend)
router.get('/api/sumar-visita', (req, res) => {
  console.log('Llamada a /api/sumar-visita');
  let visitas = 0;
  if (fs.existsSync(file)) {
    try { visitas = JSON.parse(fs.readFileSync(file, 'utf8')).visitas || 0; } catch {}
  }
  visitas++;
  fs.writeFileSync(file, JSON.stringify({ visitas }), 'utf8');
  res.json({ ok: true });
});

// Devolver visitas (¡ahora cualquiera puede verlas!)
router.get('/api/visitas', (req, res) => {
  console.log('Llamada a /api/visitas');
  let visitas = 0;
  if (fs.existsSync(file)) {
    try { visitas = JSON.parse(fs.readFileSync(file, 'utf8')).visitas || 0; } catch {}
  }
  res.json({ visitas });
});

module.exports = router;