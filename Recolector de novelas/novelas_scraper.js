// Endpoint para buscar novelas en HotZone18 y devolverlas a la interfaz
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
        const descBlock = $$('blockquote').first().text().trim();
        if (descBlock) desc = descBlock;
        let portada = '';
        const portadaImg = $$('img').first().attr('src');
        if (portadaImg && portadaImg.startsWith('http')) portada = portadaImg;
        const spoilerRegex = /href="(https?:\/\/[^\"]+\.(jpg|png|webp))"/gi;
        const spoilers = [];
        let match;
        while ((match = spoilerRegex.exec(html)) !== null) {
          spoilers.push(match[1]);
        }
        let android = '';
        $$('a.button').each((i, el) => {
          const txt = $$(el).text().toLowerCase();
          if (txt.includes('descargar') && txt.includes('android')) {
            android = $$(el).attr('href');
          }
        });
        let estado = '';
        $$('p, span, div').each((i, el) => {
          const txt = $$(el).text().toLowerCase();
          if (!estado && (txt.includes('en desarrollo') || txt.includes('completo') || txt.includes('finalizado'))) estado = txt;
        });
        let fecha = '';
        $$('span.post-card-date-meta').each((i, el) => {
          const txt = $$(el).text().trim();
          if (txt) fecha = txt;
        });
        results.push({
          id: randomId(),
          titulo,
          desc,
          generos,
          portada,
          spoilers,
          android,
          estado,
          peso: "",
          fecha
        });
      } catch (err) {
        console.error('Error en', gameUrl, err.message);
      }
    }
    res.json(results);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Endpoint para guardar la lista editada en el archivo local
app.post('/api/guardar_novelas', (req, res) => {
  try {
    fs.writeFileSync('novelas_recientes.json', JSON.stringify(req.body, null, 2), 'utf8');
    res.json({ ok: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});
const axios = require('axios');
const cheerio = require('cheerio');
const fs = require('fs');

function randomId() {
  const base = 'mflxaznvvidxh';
  const letters = 'abcdefghijklmnopqrstuvwxyz';
  return base + letters[Math.floor(Math.random() * 26)] + letters[Math.floor(Math.random() * 26)];
}

async function getRecentGames() {
  const url = 'https://www.hotzone18.com/';
  const res = await axios.get(url);
  const $ = cheerio.load(res.data);

  // Extrae las 12 URLs de las novelas más recientes
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

      // Título
      const titulo = $$('h1.entry-title').text().trim();

      // Géneros
      const generos = [];
      $$('div.entry-categories a').each((i, el) => {
        generos.push($$(el).text().trim());
      });

      // Descripción
      let desc = '';
      const descBlock = $$('blockquote').first().text().trim();
      if (descBlock) desc = descBlock;

      // Portada (primera imagen relevante)
      let portada = '';
      const portadaImg = $$('img').first().attr('src');
      if (portadaImg && portadaImg.startsWith('http')) portada = portadaImg;

      // Spoilers: busca en el código fuente con regex
      const spoilerRegex = /href="(https?:\/\/[^\"]+\.(jpg|png|webp))"/gi;
      const spoilers = [];
      let match;
      while ((match = spoilerRegex.exec(html)) !== null) {
        spoilers.push(match[1]);
      }

      // Enlace Android
      let android = '';
      $$('a.button').each((i, el) => {
        const txt = $$(el).text().toLowerCase();
        if (txt.includes('descargar') && txt.includes('android')) {
          android = $$(el).attr('href');
        }
      });

      // Estado
      let estado = '';
      $$('p, span, div').each((i, el) => {
        const txt = $$(el).text().toLowerCase();
        if (!estado && (txt.includes('en desarrollo') || txt.includes('completo') || txt.includes('finalizado'))) estado = txt;
      });

      // Fecha
      let fecha = '';
      $$('span.post-card-date-meta').each((i, el) => {
        const txt = $$(el).text().trim();
        if (txt) fecha = txt;
      });

      // Genera el objeto
      results.push({
        id: randomId(),
        titulo,
        desc,
        generos,
        portada,
        spoilers,
        android,
        estado,
        peso: "",
        fecha
      });
    } catch (err) {
      console.error('Error en', gameUrl, err.message);
    }
  }

  // Guarda en archivo
  fs.writeFileSync('novelas_recientes.json', JSON.stringify(results, null, 2), 'utf8');
  console.log('Guardado en novelas_recientes.json');
}

getRecentGames();
