require('dotenv').config();
const { Client, GatewayIntentBits, EmbedBuilder } = require('discord.js');
const fetch = require('node-fetch');
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
let novelasAnunciadas = new Set();
async function checkNovelas() {
  try {
    const res = await fetch('https://raw.githubusercontent.com/MundoEroVisual/MundoEroVisual/refs/heads/main/data/novelas-1.json');
    const data = await res.json();
    if (!Array.isArray(data) || !data.length) return;
    const channel = await client.channels.fetch(DISCORD_CHANNEL_JUEGOS_NOPOR);
    for (const novela of data) {
      const novelaId = novela._id || novela.id;
      if (!novelasAnunciadas.has(novelaId)) {
        novelasAnunciadas.add(novelaId);
        const urlNovela = novela.url && novela.url.trim() !== '' ? novela.url : 'https://eroverse.onrender.com/';
        const embed = new EmbedBuilder()
          .setTitle(novela.titulo)
          .setURL(urlNovela)
          .setImage(novela.portada)
          .addFields(
            { name: 'Géneros', value: (novela.generos || []).join(', ') || 'N/A', inline: false },
            { name: 'Estado', value: novela.estado || 'Desconocido', inline: true },
            { name: 'Peso', value: novela.peso || 'N/A', inline: true }
          )
          .setColor(0x00bfff)
          .setDescription((novela.desc || '') + `\n[Enlace a la novela](${urlNovela})\n¡Nueva novela subida!`);
        await channel.send({ embeds: [embed] });
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
