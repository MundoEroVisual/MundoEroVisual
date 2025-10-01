const express = require('express');
const app = express();
const bodyParser = require('body-parser');
const cheerio = require('cheerio');
const axios = require('axios');
const fs = require('fs');
const path = require('path');
const https = require('https');
require('dotenv').config();
// Descarga una imagen desde una URL y la guarda en la ruta indicada
function descargarImagen(url, rutaDestino) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(rutaDestino);
    https.get(url, response => {
      if (response.statusCode !== 200) {
        file.close();
        fs.unlink(rutaDestino, () => {});
        return reject(new Error('No se pudo descargar: ' + url));
      }
      response.pipe(file);
      file.on('finish', () => {
        file.close(resolve);
      });
    }).on('error', err => {
      file.close();
      fs.unlink(rutaDestino, () => {});
      reject(err);
    });
  });
}
// Endpoint para descargar todas las imágenes de las novelas
app.get('/api/descargar_imagenes', async (req, res) => {
  try {
    const novelas = JSON.parse(fs.readFileSync('novelas_recientes.json', 'utf8'));
    for (const novela of novelas) {
      const carpeta = path.join(__dirname, 'imagenes_novelas', novela.titulo.replace(/[^a-zA-Z0-9]/g, '_'));
      if (!fs.existsSync(carpeta)) fs.mkdirSync(carpeta, { recursive: true });
      console.log(`\nDescargando imágenes para: ${novela.titulo}`);
      // Portada
      if (novela.portada) {
        const ext = novela.portada.split('.').pop().split(/\?|#/)[0];
        const nombre = 'portada.' + ext;
        const ruta = path.join(carpeta, nombre);
        console.log(`  Portada: ${novela.portada}`);
        await descargarImagen(novela.portada, ruta);
      }
      // Spoilers
      if (Array.isArray(novela.spoilers)) {
        for (let i = 0; i < novela.spoilers.length; i++) {
          const url = novela.spoilers[i];
          const ext = url.split('.').pop().split(/\?|#/)[0];
          const nombre = 'spoiler_' + (i+1) + '.' + ext;
          const ruta = path.join(carpeta, nombre);
          console.log(`  Spoiler ${i+1}: ${url}`);
          await descargarImagen(url, ruta);
        }
      }
    }
    console.log('\nDescarga de imágenes finalizada.');
    res.json({ ok: true, msg: 'Imágenes descargadas en la carpeta imagenes_novelas.' });
  } catch (err) {
    console.error('Error en la descarga de imágenes:', err);
    res.status(500).json({ error: err.message });
  }
});
// ...existing code...
// GitHub eliminado, todo es local
const pathRecientesJson = 'novelas_recientes.json';

// Eliminar endpoint de cargar github local

app.use(bodyParser.json());
app.use(express.static(__dirname));

function randomId() {
  const base = 'mflxaznvvidxh';
  const letters = 'abcdefghijklmnopqrstuvwxyz';
  return base + letters[Math.floor(Math.random() * 26)] + letters[Math.floor(Math.random() * 26)];
}

function loadNovelas() {
  try {
    return JSON.parse(fs.readFileSync('novelas_recientes.json', 'utf8'));
  } catch {
    return [];
  }
}

app.get('/api/novelas', (req, res) => {
  res.json(loadNovelas());
});

app.post('/api/novela/:id', (req, res) => {
  let novelas = loadNovelas();
  const idx = novelas.findIndex(n => n.id === req.params.id);
  if (idx !== -1) {
    novelas[idx] = { ...novelas[idx], ...req.body };
    fs.writeFileSync('novelas_recientes.json', JSON.stringify(novelas, null, 2));
    res.json({ ok: true });
  } else {
    res.status(404).json({ error: 'No encontrada' });
  }
});

app.post('/api/novela', (req, res) => {
  let novelas = loadNovelas();
  novelas.push({ ...req.body, id: req.body.id || randomId() });
  fs.writeFileSync('novelas_recientes.json', JSON.stringify(novelas, null, 2));
  res.json({ ok: true });
});

app.get('/api/buscar_novelas', async (req, res) => {
  try {
    const url = 'https://www.hotzone18.com/';
    const resMain = await axios.get(url);
    const $ = cheerio.load(resMain.data);
    const links = [];
    $('.post-card-link').each((i, el) => {
      if (i < 12) {
        links.push($(el).attr('href'));
      }
    });
    const results = [];
    for (const gameUrl of links) {
      try {
        const gameRes = await axios.get(gameUrl);
        const html = gameRes.data;
        const $$ = cheerio.load(html);
        const titulo = $$('h1.entry-title').text().trim();
        const generos = [];
        $$('div.entry-categories a').each((i, el) => {
          generos.push($$(el).text().trim());
        });
  let desc = '';
  let estado = '';
        // Extraer estado desde <p> que contiene '• Estado:'
        const estadoP = $$('p').filter((i, el) => $$(el).text().includes('• Estado:')).first();
        if (estadoP.length) {
          // Buscar el valor dentro del span
          const span = estadoP.find('span');
          let spanText = span.length ? span.text().trim() : '';
          if (spanText && !/<.*?>/.test(spanText)) {
            estado = spanText;
          } else {
            // Si el span está vacío o solo tiene etiquetas, buscar después de '• Estado:'
            const txt = estadoP.text();
            const match = txt.match(/• Estado:\s*([A-Za-záéíóúÁÉÍÓÚñÑ]+)(\s|$)/i);
            if (match && match[1]) {
              estado = match[1].trim();
            }
          }
        }
        // Si no se encontró estado, buscar en todo el HTML por variantes
        if (!estado) {
          const allText = $$('body').text();
          // Buscar '• Estado:'
          let estadoTextMatch = allText.match(/• Estado:\s*([A-Za-záéíóúÁÉÍÓÚñÑ ]+)/i);
          // Si no, buscar 'Estado:'
          if (!estadoTextMatch) {
            estadoTextMatch = allText.match(/Estado:\s*([A-Za-záéíóúÁÉÍÓÚñÑ ]+)/i);
          }
          // Si no, buscar 'estado:'
          if (!estadoTextMatch) {
            estadoTextMatch = allText.match(/estado:\s*([A-Za-záéíóúÁÉÍÓÚñÑ ]+)/i);
          }
          if (estadoTextMatch && estadoTextMatch[1]) {
            estado = estadoTextMatch[1].trim();
          }
        }
        // Buscar descripción: <p style="text-align: center"><strong>Descripcion General:</strong></p> seguido de <blockquote>
        let descBlock = '';
        // Busca el <p style="text-align: center"><strong>Descripcion General:</strong></p>
        const descP = $$('p[style*="text-align: center"]').filter((i, el) => $$(el).find('strong').text().toLowerCase().includes('descripcion general'));
        if (descP.length) {
          const nextBlockquote = descP.next('blockquote');
          if (nextBlockquote.length) {
            // Solo toma el texto plano dentro del blockquote
            descBlock = nextBlockquote.text().trim();
          }
        }
  // Filtrar bloques no deseados de la descripción
  let descFiltrada = descBlock || '';
  // Elimina todo lo que esté después de la primera línea vacía, versión, cambios o descargas
  descFiltrada = descFiltrada.replace(/\n\s*\n[\s\S]*/g, '');
  descFiltrada = descFiltrada.replace(/S\d+ v?\d+\.\d+(\.\d+)?[\s\S]*/gi, '');
  descFiltrada = descFiltrada.replace(/Cambios[\s\S]*/gi, '');
  descFiltrada = descFiltrada.replace(/Descargar[\s\S]*/gi, '');
  descFiltrada = descFiltrada.replace(/\[PC\]:[\s\S]*/gi, '');
  descFiltrada = descFiltrada.replace(/ADVERTENCIA:[^\n]*\n?/gi, '');
  descFiltrada = descFiltrada.replace(/Este juego puede incluir etiquetas[\s\S]*?jugar\./gi, '');
  descFiltrada = descFiltrada.replace(/Spoilers[\s\S]*/gi, '');
  descFiltrada = descFiltrada.replace(/\n{2,}/g, '\n');
  descFiltrada = descFiltrada.trim();
  desc = descFiltrada;

        // Buscar portada: <img ... data-src="URL" />
        let portada = '';
        const portadaImg = $$('img[data-src]').first().attr('data-src');
        if (portadaImg && portadaImg.startsWith('http')) {
          portada = portadaImg;
        } else {
          // Fallback: buscar src en img con class single-post-featured-image
          const portadaImg2 = $$('img.single-post-featured-image').attr('src');
          if (portadaImg2 && portadaImg2.startsWith('http')) portada = portadaImg2;
        }
        const spoilerRegex = /href="(https?:\/\/[^\"]+\.(jpg|png|webp))"/gi;
        const spoilers = [];
        let match;
        while ((match = spoilerRegex.exec(html)) !== null) {
          spoilers.push(match[1]);
        }
        let android = '';
        let android_vip = '';
        $$('a.button').each((i, el) => {
          const txt = $$(el).text().trim();
          if (!android && txt === 'Descargar Para Android (Mediafire)') {
            android = $$(el).attr('href');
          }
          if (!android_vip && txt.toLowerCase().includes('descargar para android') && (txt.toLowerCase().includes('directo') || txt.toLowerCase().includes('vip'))) {
            android_vip = $$(el).attr('href');
          }
        });
        // Fecha: la del momento de la búsqueda
        const fecha = new Date().toISOString().slice(0, 10);
        results.push({
          id: randomId(),
          titulo,
          desc,
          generos,
          portada,
          spoilers,
          android,
          android_vip,
          estado,
          peso: "",
          fecha
        });
      } catch (err) {
        console.error('Error en', gameUrl, err.message);
      }
    }
  // Guardar las encontradas en el único JSON
  fs.writeFileSync(pathRecientesJson, JSON.stringify(results, null, 2), 'utf8');
  res.json(results);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/guardar_novelas', (req, res) => {
  try {
    // Cargar novelas existentes
    let existentes = [];
    try {
      existentes = JSON.parse(fs.readFileSync('novelas_recientes.json', 'utf8'));
    } catch {
      existentes = [];
    }
    // Agregar nuevas novelas al final
    const nuevas = Array.isArray(req.body) ? req.body : [req.body];
    const resultado = [...existentes, ...nuevas];
    fs.writeFileSync('novelas_recientes.json', JSON.stringify(resultado, null, 2), 'utf8');
    res.json({ ok: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/subir_github', async (req, res) => {
  try {
    // Ya todo está en novelas_recientes.json
    res.json({ ok: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/editor', (req, res) => {
  res.sendFile(__dirname + '/novelas_interface.html');
});


function randomId() {
  const base = 'mflxaznvvidxh';
  const letters = 'abcdefghijklmnopqrstuvwxyz';
  return base + letters[Math.floor(Math.random() * 26)] + letters[Math.floor(Math.random() * 26)];
}

app.listen(3000, () => console.log('Servidor iniciado en http://localhost:3000'));

