

require('dotenv').config();
const { Client, GatewayIntentBits, EmbedBuilder } = require('discord.js');
const fetch = require('node-fetch');
// --- Configuración para GitHub API ---
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const GITHUB_OWNER = process.env.GITHUB_OWNER;
const GITHUB_REPO = process.env.GITHUB_REPO;
const GITHUB_BRANCH = process.env.GITHUB_BRANCH || 'main';

// Función para subir archivo a GitHub (crea si no existe)
async function updateFileOnGitHub(githubPath, newContent) {
  let sha = null;
  try {
    sha = await getFileSha(githubPath);
  } catch (e) {
    sha = null;
  }
  const url = `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/contents/${githubPath}`;
  const body = {
    message: 'Actualización automática desde el bot',
    content: Buffer.from(JSON.stringify(newContent, null, 2)).toString('base64'),
    branch: GITHUB_BRANCH
  };
  if (sha) body.sha = sha;
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

// Devuelve el SHA del archivo en GitHub, o lanza error si no existe
async function getFileSha(githubPath) {
  const url = `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/contents/${githubPath}?ref=${GITHUB_BRANCH}`;
  const res = await fetch(url, {
    headers: {
      Authorization: `token ${GITHUB_TOKEN}`,
      Accept: 'application/vnd.github+json',
    }
  });
  if (res.status === 404) throw new Error('Archivo no existe');
  const data = await res.json();
  return data.sha;
}
const RSSParser = require('rss-parser');
console.log("TOKEN del .env es:", process.env.DISCORD_TOKEN);
const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMembers,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent
  ]
});

// Comandos de mantenimiento para admins
client.on('messageCreate', async msg => {

  if (msg.author.bot || !msg.guild) return;
  if (!msg.content.startsWith('!')) return;
  const args = msg.content.slice(1).trim().split(/ +/);
  const command = args.shift().toLowerCase();
  // Solo admins pueden usar estos comandos
  const isAdmin = msg.member.permissions.has('Administrator');

  // Comando para mostrar todos los comandos disponibles
  if (msg.content.trim() === '!comandos') {
    const comandos = [
      '`!clear <n>` — Borra los últimos n mensajes del canal.',
      '`!clearall` — Borra todos los mensajes del canal actual.',
      '`!reanunciar-novelas` — Vuelve a anunciar todas las novelas.',
      '`!ping` — Prueba de latencia/respuesta del bot.',
      '`!ban @usuario <motivo>` — Banea a un usuario.',
      '`!kick @usuario <motivo>` — Expulsa a un usuario.',
      '`!anuncio <mensaje>` — Envía un anuncio a todos los canales configurados.'
    ];
    return msg.channel.send({
      embeds: [
        new EmbedBuilder()
          .setTitle('Comandos de administración disponibles')
          .setDescription(comandos.join('\n'))
          .setColor(0x00bfff)
      ]
    });
  }

  if (!isAdmin) return;

  if (command === 'clear' || command === 'purge') {
    const amount = parseInt(args[0], 10);
  // Comando !ban
  if (command === 'ban') {
    if (args.length < 1) return msg.reply('Debes mencionar a un usuario para banear.');
    const user = msg.mentions.members.first();
    const motivo = args.slice(1).join(' ') || 'Sin motivo';
    if (!user) return msg.reply('Usuario no encontrado.');
    if (!user.bannable) return msg.reply('No puedo banear a ese usuario.');
    try {
      await user.ban({ reason: motivo });
      msg.channel.send(`🔨 Usuario ${user.user.tag} baneado. Motivo: ${motivo}`);
    } catch (e) {
      msg.reply('No se pudo banear al usuario.');
    }
  }

  // Comando !kick
  if (command === 'kick') {
    if (args.length < 1) return msg.reply('Debes mencionar a un usuario para expulsar.');
    const user = msg.mentions.members.first();
    const motivo = args.slice(1).join(' ') || 'Sin motivo';
    if (!user) return msg.reply('Usuario no encontrado.');
    if (!user.kickable) return msg.reply('No puedo expulsar a ese usuario.');
    try {
      await user.kick(motivo);
      msg.channel.send(`👢 Usuario ${user.user.tag} expulsado. Motivo: ${motivo}`);
    } catch (e) {
      msg.reply('No se pudo expulsar al usuario.');
    }
  }

  // Comando !anuncio
  if (command === 'anuncio') {
    const mensaje = args.join(' ');
    if (!mensaje) return msg.reply('Debes escribir el mensaje del anuncio.');
    // Puedes personalizar los canales a los que se envía el anuncio
    const canales = [
      DISCORD_CHANNEL_WELCOME,
      DISCORD_CHANNEL_MEMES,
      DISCORD_CHANNEL_JUEGOS_NOPOR
    ].filter(Boolean);
    for (const canalId of canales) {
      try {
        const canal = await client.channels.fetch(canalId);
        if (canal) await canal.send(`📢 **ANUNCIO:** ${mensaje}`);
      } catch {}
    }
    msg.reply('Anuncio enviado.');
  }
    if (isNaN(amount) || amount < 1 || amount > 100) {
      return msg.reply('Debes especificar un número entre 1 y 100. Ejemplo: !clear 10');
    }
    try {
      await msg.channel.bulkDelete(amount, true);
      msg.channel.send(`🧹 Se han borrado ${amount} mensajes.`)
        .then(m => setTimeout(() => m.delete().catch(()=>{}), 3000));
    } catch (err) {
      msg.reply('No pude borrar los mensajes. ¿Tengo permisos suficientes?');
    }
  }

  if (command === 'clearall') {
    // Borra todos los mensajes del canal (en lotes de 100)
    let deleted = 0;
    let lastId;
    try {
      while (true) {
        const messages = await msg.channel.messages.fetch({ limit: 100, ...(lastId && { before: lastId }) });
        if (messages.size === 0) break;
        await msg.channel.bulkDelete(messages, true);
        deleted += messages.size;
        lastId = messages.last().id;
        if (messages.size < 100) break;
      }
      msg.channel.send(`🧹 Se han borrado todos los mensajes del canal (${deleted}).`).then(m => setTimeout(() => m.delete().catch(()=>{}), 3000));
    } catch (err) {
      msg.reply('No pude borrar todos los mensajes. ¿Tengo permisos suficientes?');
    }
  }

  if (command === 'reanunciar-novelas') {
    // Borra el archivo de IDs y vuelve a anunciar todas las novelas
    try {
      novelasAnunciadas = new Set();
      fs.writeFileSync(NOVELAS_ANUNCIADAS_PATH, '[]', 'utf-8');
      // Subir archivo vacío a GitHub
      await updateFileOnGitHub('data/novelasAnunciadas.json', []);
      msg.channel.send('🔄 Se reinició la lista de novelas anunciadas. Se volverán a anunciar todas en el próximo ciclo.').then(m => setTimeout(() => m.delete().catch(()=>{}), 5000));
    } catch (e) {
      msg.reply('No se pudo reiniciar la lista de novelas anunciadas.');
    }
  }

  if (command === 'ping') {
    msg.reply('Pong!');
  }
});

const parser = new RSSParser();
// Log de actividad en canal específico
client.on('messageCreate', async msg => {
  if (!process.env.DISCORD_CHANNEL_ACTIVITY_LOG || msg.author.bot) return;
  try {
    const logChannel = msg.guild?.channels.cache.get(process.env.DISCORD_CHANNEL_ACTIVITY_LOG);
    if (logChannel) {
      logChannel.send(`📝 Mensaje en <#${msg.channel.id}> por ${msg.author.tag}: ${msg.content}`);
    }
  } catch {}
});

client.on('messageDelete', async msg => {
  if (!process.env.DISCORD_CHANNEL_ACTIVITY_LOG || !msg.guild) return;
  try {
    const logChannel = msg.guild.channels.cache.get(process.env.DISCORD_CHANNEL_ACTIVITY_LOG);
    if (logChannel) {
      logChannel.send(`🗑️ Mensaje eliminado en <#${msg.channel.id}> por ${msg.author?.tag || 'desconocido'}: ${msg.content}`);
    }
  } catch {}
});

client.on('messageUpdate', async (oldMsg, newMsg) => {
  if (!process.env.DISCORD_CHANNEL_ACTIVITY_LOG || !oldMsg.guild) return;
  try {
    const logChannel = oldMsg.guild.channels.cache.get(process.env.DISCORD_CHANNEL_ACTIVITY_LOG);
    if (logChannel) {
      logChannel.send(`✏️ Mensaje editado en <#${oldMsg.channel.id}> por ${oldMsg.author?.tag || 'desconocido'}:\nAntes: ${oldMsg.content}\nDespués: ${newMsg.content}`);
    }
  } catch {}
});

// Variables de entorno
const {
  DISCORD_TOKEN,
  DISCORD_CHANNEL_WELCOME,
  DISCORD_CHANNEL_NEW_VIDEOS,
  DISCORD_CHANNEL_MEMES,
  DISCORD_CHANNEL_HENTAI,
  DISCORD_CHANNEL_PORNOLAND,
  DISCORD_CHANNEL_FETICHES,
  DISCORD_CHANNEL_PIES,
  DISCORD_CHANNEL_JUEGOS_NOPOR,
  YOUTUBE_CHANNEL_ID,
  YOUTUBE_API_KEY,
  NITTER_MEMES,
  NITTER_HENTAI,
  NITTER_PORNOLAND,
  NITTER_FETICHES,
  NITTER_PIES
} = process.env;

// 1. Mensaje de bienvenida
client.on('guildMemberAdd', async member => {
  try {
    // Asignar rol miembro automáticamente si existe
    if (process.env.DISCORD_ROLE_MIEMBRO) {
      const role = member.guild.roles.cache.get(process.env.DISCORD_ROLE_MIEMBRO);
      if (role && !member.roles.cache.has(role.id)) {
        await member.roles.add(role).catch(() => {});
      }
    }
    const channel = member.guild.channels.cache.get(DISCORD_CHANNEL_WELCOME);
    if (!channel) return;
    const welcomeMsg = `**Eroverse**\n\n✨ **Bienvenido/a <@${member.id}> a 🌐 Eroverse 🔞**\n\n<:nsfw:1128359642322325634> Disfruta de nuestras novelas visuales, contenido +18 y una comunidad sin censura. ¡Preséntate y empieza tu viaje erótico! 💋`;
    await channel.send({
      content: welcomeMsg,
      allowedMentions: { users: [member.id] }
    });
  } catch (err) {
    console.error('Error enviando mensaje de bienvenida o asignando rol:', err);
  }
// Sistema de niveles por actividad en el chat
const userXP = new Map();
const LEVEL_XP = 100;
function addXP(userId) {
  const data = userXP.get(userId) || { xp: 0, level: 0 };
  data.xp += Math.floor(Math.random() * 10) + 5;
  if (data.xp >= LEVEL_XP) {
    data.xp -= LEVEL_XP;
    data.level++;
    userXP.set(userId, data);
    return { levelUp: true, level: data.level };
  }
  userXP.set(userId, data);
  return { levelUp: false };
}

client.on('messageCreate', async msg => {
  if (msg.author.bot) return;
  // Sistema de niveles
  const res = addXP(msg.author.id);
  if (res.levelUp) {
    try {
      await msg.channel.send(`🎉 Felicidades <@${msg.author.id}>, ¡subiste a nivel ${res.level}!`);
    } catch {}
  }
});
});

// 2. YouTube: Detectar nuevos videos
let lastVideoId = null;
async function checkYouTube() {
  try {
    const url = `https://www.googleapis.com/youtube/v3/search?key=${YOUTUBE_API_KEY}&channelId=${YOUTUBE_CHANNEL_ID}&part=snippet,id&order=date&maxResults=1`;
    const res = await fetch(url);
    const data = await res.json();
    if (!data.items || !data.items.length) return;
    const video = data.items[0];
    if (video.id.kind !== 'youtube#video') return;
    if (lastVideoId === video.id.videoId) return;
    lastVideoId = video.id.videoId;
    const embed = new EmbedBuilder()
      .setTitle(video.snippet.title)
      .setURL(`https://youtu.be/${video.id.videoId}`)
      .setImage(video.snippet.thumbnails.high.url)
      .setColor(0xff0000)
      .setDescription('¡Nuevo video en el canal de YouTube!');
    const channel = await client.channels.fetch(DISCORD_CHANNEL_NEW_VIDEOS);
    await channel.send({ embeds: [embed] });
  } catch (err) {
    console.error('Error comprobando YouTube:', err);
  }
}

// 3. Reenvío de mensajes entre canales de Discord (texto, imágenes y archivos)
const FORWARD_MAP = [
  { origen: NITTER_MEMES, destino: DISCORD_CHANNEL_MEMES },
  { origen: NITTER_HENTAI, destino: DISCORD_CHANNEL_HENTAI },
  { origen: NITTER_PORNOLAND, destino: DISCORD_CHANNEL_PORNOLAND },
  { origen: NITTER_FETICHES, destino: DISCORD_CHANNEL_FETICHES },
  { origen: NITTER_PIES, destino: DISCORD_CHANNEL_PIES }
];

client.on('messageCreate', async msg => {
  if (msg.author.bot) return;
  for (const map of FORWARD_MAP) {
    if (msg.channel.id === map.origen) {
      try {
        const destChannel = await client.channels.fetch(map.destino);
        // Reenviar texto
        let content = msg.content || '';
        // Reenviar archivos adjuntos
        const files = msg.attachments.map(att => att.url);
        await destChannel.send({ content, files });
      } catch (err) {
        console.error('Error reenviando mensaje:', err);
      }
    }
  }
});

// 4. Novelas API
let lastNovelaId = null;
const fs = require('fs');
const NOVELAS_ANUNCIADAS_PATH = './data/novelasAnunciadas.json';
let novelasAnunciadas = new Set();
// Cargar IDs anunciados al iniciar
try {
  if (fs.existsSync(NOVELAS_ANUNCIADAS_PATH)) {
    const data = JSON.parse(fs.readFileSync(NOVELAS_ANUNCIADAS_PATH, 'utf-8'));
    if (Array.isArray(data)) {
      novelasAnunciadas = new Set(data);
    }
  } else {
    // Si no existe local, intentar descargarlo de GitHub
    (async () => {
      try {
        const url = `https://raw.githubusercontent.com/${GITHUB_OWNER}/${GITHUB_REPO}/${GITHUB_BRANCH}/data/novelasAnunciadas.json`;
        const res = await fetch(url);
        if (res.ok) {
          const data = await res.json();
          if (Array.isArray(data)) {
            novelasAnunciadas = new Set(data);
          }
        } else {
          // Si tampoco existe en GitHub, crearlo vacío en GitHub
          await updateFileOnGitHub('data/novelasAnunciadas.json', []);
          novelasAnunciadas = new Set();
        }
      } catch (e) {
        console.error('Error inicializando novelasAnunciadas.json desde GitHub:', e);
      }
    })();
  }
} catch (e) {
  console.error('Error cargando novelasAnunciadas.json:', e);
}
async function checkNovelas() {
  try {
    const res = await fetch('https://raw.githubusercontent.com/MundoEroVisual/MundoEroVisual/refs/heads/main/data/novelas-1.json');
    const data = await res.json();
    if (!Array.isArray(data) || !data.length) return;
    const channel = await client.channels.fetch(DISCORD_CHANNEL_JUEGOS_NOPOR);
    let nuevosAnunciados = false;
    for (const novela of data) {
      const novelaId = novela._id || novela.id;
      if (!novelasAnunciadas.has(novelaId)) {
        novelasAnunciadas.add(novelaId);
        nuevosAnunciados = true;
        const urlNovela = novela.url && novela.url.trim() !== '' ? novela.url : 'https://eroverse.onrender.com/';
        const enlacePublico = `https://eroverse.onrender.com/novela.html?id=${novela.id || novela._id}`;
        const embed = new EmbedBuilder()
          .setTitle(novela.titulo)
          .setURL(enlacePublico)
          .setImage(novela.portada)
          .addFields(
            { name: 'Géneros', value: (novela.generos || []).join(', ') || 'N/A', inline: false },
            { name: 'Estado', value: novela.estado || 'Desconocido', inline: true },
            { name: 'Peso', value: novela.peso || 'N/A', inline: true }
          )
          .setColor(0x00bfff)
          .setDescription((novela.desc || '') + `\n¡Nueva novela subida!`);
        // Botón de descarga público
        const { ButtonBuilder, ActionRowBuilder } = require('discord.js');
        const row = new ActionRowBuilder().addComponents(
          new ButtonBuilder()
            .setLabel('Descargar')
            .setStyle(5)
            .setURL(enlacePublico)
        );
        await channel.send({ embeds: [embed], components: [row] });
      }
    }
    // Guardar los IDs anunciados si hubo alguno nuevo
    if (nuevosAnunciados) {
      try {
        const arr = Array.from(novelasAnunciadas);
        fs.writeFileSync(NOVELAS_ANUNCIADAS_PATH, JSON.stringify(arr, null, 2), 'utf-8');
        // Subir a GitHub
        await updateFileOnGitHub('data/novelasAnunciadas.json', arr);
      } catch (e) {
        console.error('Error guardando o subiendo novelasAnunciadas.json:', e);
      }
    }
  } catch (err) {
    console.error('Error comprobando novelas:', err);
  }
}

// 8. Intervalos periódicos
client.once('ready', () => {
  console.log(`Bot iniciado como ${client.user.tag}`);
  setInterval(checkYouTube, 60 * 1000); // cada minuto
  setInterval(checkNovelas, 120 * 1000); // cada 2 minutos
});

client.login(DISCORD_TOKEN);
