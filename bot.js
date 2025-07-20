require("dotenv").config();
const fs = require("fs");
const RSSParser = require("rss-parser");
// Si usas Node.js v18+, fetch es global. Si no, descomenta la siguiente línea:
// const fetch = require("node-fetch");
const {
  Client,
  GatewayIntentBits,
  SlashCommandBuilder,
  ButtonBuilder,
  ActionRowBuilder,
  PermissionFlagsBits,
  ChannelType,
  EmbedBuilder,
} = require("discord.js");

// IDs configurables (cambia según tu servidor)
const CANAL_AYUDA_ID = "1391222796453019749";
const CATEGORIA_TICKETS_ID = "1391222553799954442";
const STAFF_ROLE_ID = "1372066132957331587";

// Variables para anuncios de novelas y YouTube
const NOVELAS_ANUNCIADAS_PATH = "./data/novelasAnunciadas.json";
let novelasAnunciadas = new Set();

// Carga inicial de novelas anunciadas (si existe)
(() => {
  try {
    if (fs.existsSync(NOVELAS_ANUNCIADAS_PATH)) {
      const data = JSON.parse(fs.readFileSync(NOVELAS_ANUNCIADAS_PATH, "utf-8"));
      if (Array.isArray(data)) novelasAnunciadas = new Set(data);
    }
  } catch (e) {
    console.error("Error cargando novelas anunciadas:", e);
  }
})();

// Variables de entorno para GitHub y YouTube
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
  GITHUB_TOKEN,
  GITHUB_OWNER,
  GITHUB_REPO,
  GITHUB_BRANCH = "main",
  DISCORD_ROLE_MIEMBRO,
  DISCORD_CHANNEL_ACTIVITY_LOG,
} = process.env;

// Validación de variables críticas
if (!DISCORD_TOKEN) throw new Error("Falta DISCORD_TOKEN en .env");
if (!YOUTUBE_API_KEY) throw new Error("Falta YOUTUBE_API_KEY en .env");
if (!YOUTUBE_CHANNEL_ID) throw new Error("Falta YOUTUBE_CHANNEL_ID en .env");
if (!DISCORD_CHANNEL_NEW_VIDEOS) throw new Error("Falta DISCORD_CHANNEL_NEW_VIDEOS en .env");

// --- Cliente Discord ---
const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMembers,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
  ],
});

// ---------------------
// 1. SISTEMA DE TICKETS
// ---------------------
client.once("ready", async () => {
  console.log(`✅ Bot conectado como ${client.user.tag}`);

  // Registrar comando /ticket
  try {
    await client.application.commands.create({
      name: "ticket",
      description: "Solicita ayuda y abre un ticket privado",
    });
    console.log("Comando /ticket registrado");
  } catch (err) {
    console.error("Error al registrar el comando:", err);
  }

  // Enviar botón al canal de ayuda (solo al iniciar)
  const canal = await client.channels.fetch(CANAL_AYUDA_ID).catch(() => null);
  if (canal && canal.isTextBased()) {
    const row = new ActionRowBuilder().addComponents(
      new ButtonBuilder()
        .setCustomId("abrir_ticket")
        .setLabel("📩 Abrir Ticket")
        .setStyle(1)
    );
    canal.send({
      content: "¿Necesitas ayuda? Haz clic en el botón para abrir un ticket.",
      components: [row],
    });
  }

  // Ejecutar checkNovelas cada 2 minutos
  setInterval(checkNovelas, 2 * 60 * 1000);

  // Ejecutar checkYouTube cada 5 minutos
  setInterval(checkYouTube, 5 * 60 * 1000);
});

client.on("interactionCreate", async (interaction) => {
  if (interaction.isChatInputCommand() && interaction.commandName === "ticket") {
    // Comando /ticket
    const row = new ActionRowBuilder().addComponents(
      new ButtonBuilder()
        .setCustomId("abrir_ticket")
        .setLabel("📩 Abrir Ticket")
        .setStyle(1)
    );
    await interaction.reply({
      content: "Haz clic en el botón para abrir tu ticket privado.",
      components: [row],
      ephemeral: true,
    });
  }

  if (interaction.isButton()) {
    if (interaction.customId === "abrir_ticket") {
      // Crear canal de ticket privado
      const { guild, user } = interaction;
      if (!guild) {
        await interaction.reply({ content: "Este comando solo puede usarse en un servidor.", ephemeral: true });
        return;
      }
      const nombreCanal = `ticket-${user.id}`;
      const canalExistente = guild.channels.cache.find((c) => c.name === nombreCanal);
      if (canalExistente) {
        await interaction.reply({ content: "Ya tienes un ticket abierto.", ephemeral: true });
        return;
      }
      try {
        const canal = await guild.channels.create({
          name: nombreCanal,
          type: ChannelType.GuildText,
          parent: CATEGORIA_TICKETS_ID,
          permissionOverwrites: [
            { id: guild.id, deny: [PermissionFlagsBits.ViewChannel] },
            { id: user.id, allow: [PermissionFlagsBits.ViewChannel, PermissionFlagsBits.SendMessages] },
            { id: STAFF_ROLE_ID, allow: [PermissionFlagsBits.ViewChannel, PermissionFlagsBits.SendMessages] },
          ],
        });
        const rowClose = new ActionRowBuilder().addComponents(
          new ButtonBuilder()
            .setCustomId("cerrar_ticket")
            .setLabel("🔒 Cerrar Ticket")
            .setStyle(4)
        );
        await canal.send({
          content: `¡Bienvenido <@${user.id}>! Describe tu problema y el staff te atenderá.`,
          components: [rowClose],
        });
        await interaction.reply({ content: `🎫 Ticket creado: <#${canal.id}>`, ephemeral: true });
      } catch (e) {
        console.error("Error creando canal de ticket:", e);
        await interaction.reply({ content: "Error al crear el ticket. Contacta al staff.", ephemeral: true });
      }
    } else if (interaction.customId === "cerrar_ticket") {
      // Cerrar ticket con delay
      await interaction.reply({ content: "🔒 Cerrando el ticket en 5 segundos...", ephemeral: true });
      setTimeout(() => {
        interaction.channel.delete().catch(() => {});
      }, 5000);
    }
  }
});

// --------------------------------
// 2. COMANDOS DE ADMINISTRACIÓN
// --------------------------------

client.on("messageCreate", async (msg) => {
  if (msg.author.bot || !msg.guild) return;
  if (!msg.content.startsWith("!")) return;

  const args = msg.content.slice(1).trim().split(/ +/);
  const command = args.shift().toLowerCase();

  const isAdmin = msg.member.permissions.has(PermissionFlagsBits.Administrator);

  // Solo admins pueden usar estos comandos, excepto !anuncio
  if (!isAdmin && command !== "anuncio") return;

  // Comando para mostrar todos los comandos disponibles (solo admins)
  if (command === "comandos") {
    if (!isAdmin) return;
    const comandos = [
      "`!clear <n>` — Borra los últimos n mensajes del canal.",
      "`!clearall` — Borra todos los mensajes del canal actual.",
      "`!reanunciar-novelas` — Vuelve a anunciar todas las novelas (resetea la lista).",
      "`!refrescar-novelas` — Fuerza la relectura del JSON y reanuncia novelas nuevas.",
      "`!ping` — Prueba de latencia/respuesta del bot.",
      "`!ban @usuario <motivo>` — Banea a un usuario.",
      "`!kick @usuario <motivo>` — Expulsa a un usuario.",
      "`!anuncio <mensaje>` — Envía un anuncio a todos los canales configurados.",
      "`!userinfo [@usuario]` — Muestra información de un usuario.",
      "`!serverinfo` — Muestra información del servidor.",
    ];
    const adminMsg = await msg.reply({
      embeds: [
        new EmbedBuilder()
          .setTitle("Comandos de administración disponibles")
          .setDescription(comandos.join("\n"))
          .setColor(0x00bfff),
      ],
    });
    setTimeout(() => adminMsg.delete().catch(() => {}), 10000);
    return;
  }

  if (command === "refrescar-novelas") {
    try {
      // Actualiza la lista de novelas desde GitHub y anuncia las nuevas
      await checkNovelas();
      msg.reply("✅ Lista de novelas refrescada y anunciadas si hay novedades.");
    } catch (e) {
      msg.reply("Error al refrescar novelas.");
    }
    return;
  }

  if (command === "userinfo") {
    if (!isAdmin) return;
    const user = msg.mentions.users.first() || msg.author;
    const member = msg.guild.members.cache.get(user.id);
    const embed = new EmbedBuilder()
      .setTitle(`Información de ${user.tag}`)
      .setThumbnail(user.displayAvatarURL())
      .addFields(
        { name: "ID", value: user.id, inline: true },
        {
          name: "Cuenta creada",
          value: `<t:${Math.floor(user.createdTimestamp / 1000)}:F>`,
          inline: true,
        },
        {
          name: "Se unió",
          value: member ? `<t:${Math.floor(member.joinedTimestamp / 1000)}:F>` : "N/A",
          inline: true,
        },
        { name: "Roles", value: member ? member.roles.cache.map((r) => r.name).join(", ") : "N/A", inline: false }
      )
      .setColor(0x00bfff);
    const adminMsg = await msg.reply({ embeds: [embed] });
    setTimeout(() => adminMsg.delete().catch(() => {}), 10000);
    return;
  }

  if (command === "serverinfo") {
    if (!isAdmin) return;
    const { guild } = msg;
    const embed = new EmbedBuilder()
      .setTitle(`Información del servidor: ${guild.name}`)
      .setThumbnail(guild.iconURL())
      .addFields(
        { name: "ID", value: guild.id, inline: true },
        { name: "Miembros", value: `${guild.memberCount}`, inline: true },
        { name: "Creado", value: `<t:${Math.floor(guild.createdTimestamp / 1000)}:F>`, inline: true },
        { name: "Dueño", value: `<@${guild.ownerId}>`, inline: true }
      )
      .setColor(0x00bfff);
    const adminMsg = await msg.reply({ embeds: [embed] });
    setTimeout(() => adminMsg.delete().catch(() => {}), 10000);
    return;
  }

  if (command === "clear" || command === "purge") {
    if (!isAdmin) return;
    const amount = parseInt(args[0], 10);
    if (isNaN(amount) || amount < 1 || amount > 100) {
      return msg.reply("Debes especificar un número entre 1 y 100. Ejemplo: !clear 10");
    }
    try {
      await msg.channel.bulkDelete(amount, true);
      const m = await msg.channel.send(`🧹 Se han borrado ${amount} mensajes.`);
      setTimeout(() => m.delete().catch(() => {}), 3000);
    } catch (err) {
      msg.reply("No pude borrar los mensajes. ¿Tengo permisos suficientes?");
    }
    return;
  }

  if (command === "clearall") {
    if (!isAdmin) return;
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
      const m = await msg.channel.send(`🧹 Se han borrado todos los mensajes del canal (${deleted}).`);
      setTimeout(() => m.delete().catch(() => {}), 3000);
    } catch (err) {
      msg.reply("No pude borrar todos los mensajes. ¿Tengo permisos suficientes?");
    }
    return;
  }

  if (command === "ban") {
    if (!isAdmin) return;
    if (args.length < 1) return msg.reply("Debes mencionar a un usuario para banear.");
    const userToBan = msg.mentions.members.first();
    const motivo = args.slice(1).join(" ") || "Sin motivo";
    if (!userToBan) return msg.reply("Usuario no encontrado.");
    if (!userToBan.bannable) return msg.reply("No puedo banear a ese usuario.");
    try {
      await userToBan.ban({ reason: motivo });
      msg.channel.send(`🔨 Usuario ${userToBan.user.tag} baneado. Motivo: ${motivo}`);
    } catch (e) {
      msg.reply("No se pudo banear al usuario.");
    }
    return;
  }

  if (command === "kick") {
    if (!isAdmin) return;
    if (args.length < 1) return msg.reply("Debes mencionar a un usuario para expulsar.");
    const userToKick = msg.mentions.members.first();
    const motivo = args.slice(1).join(" ") || "Sin motivo";
    if (!userToKick) return msg.reply("Usuario no encontrado.");
    if (!userToKick.kickable) return msg.reply("No puedo expulsar a ese usuario.");
    try {
      await userToKick.kick(motivo);
      msg.channel.send(`👢 Usuario ${userToKick.user.tag} expulsado. Motivo: ${motivo}`);
    } catch (e) {
      msg.reply("No se pudo expulsar al usuario.");
    }
    return;
  }

  if (command === "anuncio") {
    const mensaje = args.join(" ");
    if (!mensaje) return msg.reply("Debes escribir el mensaje del anuncio.");
    // Canales configurados para anuncios
    const canales = [
      DISCORD_CHANNEL_WELCOME,
      DISCORD_CHANNEL_MEMES,
      DISCORD_CHANNEL_JUEGOS_NOPOR,
      // Puedes agregar más aquí
    ].filter(Boolean);

    for (const canalId of canales) {
      try {
        const canal = await client.channels.fetch(canalId);
        if (canal) await canal.send(`📢 **ANUNCIO:** ${mensaje}`);
      } catch {}
    }
    msg.reply("Anuncio enviado.");
    return;
  }

  // Otros comandos aquí...
});

// --------------------
// 3. MENSAJE DE BIENVENIDA Y ROL
// --------------------
client.on("guildMemberAdd", async (member) => {
  try {
    if (DISCORD_ROLE_MIEMBRO) {
      // Buscar el rol en caché o en la API
      let role = member.guild.roles.cache.get(DISCORD_ROLE_MIEMBRO);
      if (!role) {
        const roles = await member.guild.roles.fetch();
        role = roles.get(DISCORD_ROLE_MIEMBRO);
      }
      if (role && !member.roles.cache.has(role.id)) {
        await member.roles.add(role);
        console.log(`Rol miembro asignado a ${member.user.tag}`);
      } else if (!role) {
        console.warn(`No se encontró el rol miembro (${DISCORD_ROLE_MIEMBRO}) en el servidor.`);
      }
    } else {
      console.warn("DISCORD_ROLE_MIEMBRO no está definido en .env");
    }
    const channel = member.guild.channels.cache.get(DISCORD_CHANNEL_WELCOME);
    if (!channel) return;
    const welcomeMsg = `**Eroverse**\n\n✨ **Bienvenido/a <@${member.id}> a 🌐 Eroverse 🔞**\n\n<:nsfw:1128359642322325634> Disfruta de nuestras novelas visuales, contenido +18 y una comunidad sin censura. ¡Preséntate y empieza tu viaje erótico! 💋`;
    await channel.send({ content: welcomeMsg, allowedMentions: { users: [member.id] } });
  } catch (err) {
    console.error("Error enviando mensaje de bienvenida o asignando rol:", err);
  }
});

// ------------------------
// 4. SISTEMA DE NIVELES XP
// ------------------------
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

client.on("messageCreate", async (msg) => {
  if (msg.author.bot || !msg.guild) return;
  const resultado = addXP(msg.author.id);
  if (resultado.levelUp) {
    msg.channel.send(`🎉 ¡Felicidades <@${msg.author.id}>! Has subido al nivel ${resultado.level}.`);
  }
});

// ----------------------------------------
// 5. LOGS DE MENSAJES (creación, edición, eliminación)
// ----------------------------------------
client.on("messageCreate", async (msg) => {
  if (msg.author.bot) return;
  const canalLog = client.channels.cache.get(DISCORD_CHANNEL_ACTIVITY_LOG);
  if (!canalLog) return;
  const embed = new EmbedBuilder()
    .setColor(0x00ff00)
    .setAuthor({ name: msg.author.tag, iconURL: msg.author.displayAvatarURL() })
    .setDescription(`Mensaje enviado en <#${msg.channel.id}>`)
    .addFields({ name: "Contenido", value: msg.content || "(sin contenido)" })
    .setTimestamp();

  canalLog.send({ embeds: [embed] });
});

client.on("messageUpdate", async (oldMsg, newMsg) => {
  if (oldMsg.author?.bot) return;
  const canalLog = client.channels.cache.get(DISCORD_CHANNEL_ACTIVITY_LOG);
  if (!canalLog) return;
  if (oldMsg.content === newMsg.content) return; // evitar logs si no cambia el texto

  const embed = new EmbedBuilder()
    .setColor(0xffff00)
    .setAuthor({ name: oldMsg.author.tag, iconURL: oldMsg.author.displayAvatarURL() })
    .setDescription(`Mensaje editado en <#${oldMsg.channel.id}>`)
    .addFields(
      { name: "Antes", value: oldMsg.content || "(sin contenido)" },
      { name: "Después", value: newMsg.content || "(sin contenido)" }
    )
    .setTimestamp();

  canalLog.send({ embeds: [embed] });
});

client.on("messageDelete", async (msg) => {
  if (msg.author?.bot) return;
  const canalLog = client.channels.cache.get(DISCORD_CHANNEL_ACTIVITY_LOG);
  if (!canalLog) return;

  const embed = new EmbedBuilder()
    .setColor(0xff0000)
    .setAuthor({ name: msg.author.tag, iconURL: msg.author.displayAvatarURL() })
    .setDescription(`Mensaje eliminado en <#${msg.channel.id}>`)
    .addFields({ name: "Contenido eliminado", value: msg.content || "(sin contenido)" })
    .setTimestamp();

  canalLog.send({ embeds: [embed] });
});

// --------------------------------------------
// 6. ANUNCIOS AUTOMÁTICOS DE NOVELAS Y YOUTUBE
// --------------------------------------------
async function guardarNovelasEnGitHub(novelas) {
  try {
    const { Octokit } = await import("@octokit/rest");
    const octokit = new Octokit({ auth: GITHUB_TOKEN });

    // Parámetros
    const owner = GITHUB_OWNER;
    const repo = GITHUB_REPO;
    const path = "data/novelasAnunciadas.json";
    const branch = GITHUB_BRANCH || "main";
    const content = JSON.stringify(novelas, null, 2);
    let sha = undefined;

    // Obtener SHA del archivo actual si existe
    try {
      const { data: fileData } = await octokit.repos.getContent({
        owner,
        repo,
        path,
        ref: branch,
      });
      sha = fileData.sha;
    } catch (e) {
      // Si no existe, lo creamos nuevo
      sha = undefined;
    }

    // Subir el archivo
    await octokit.repos.createOrUpdateFileContents({
      owner,
      repo,
      path,
      message: "Actualizar novelas anunciadas desde el bot",
      content: Buffer.from(content).toString("base64"),
      branch,
      sha,
    });
    console.log("✅ Novelas anunciadas guardadas en GitHub");
  } catch (error) {
    console.error("❌ Error al guardar en GitHub:", error.message);
  }
}


async function checkNovelas() {
  try {
    const res = await fetch('https://raw.githubusercontent.com/MundoEroVisual/MundoEroVisual/main/data/novelas-1.json');
    const data = await res.json();
    if (!Array.isArray(data) || !data.length) return;

    const channel = await client.channels.fetch(DISCORD_CHANNEL_JUEGOS_NOPOR);
    if (!channel) {
      console.error("Canal para anuncios no encontrado");
      return;
    }

    let huboNovedad = false;

    for (const novela of data) {
      const novelaId = novela._id || novela.id;
      if (!novelasAnunciadas.has(novelaId)) {
        novelasAnunciadas.add(novelaId);
        huboNovedad = true;

        // Construir el enlace usando el id
        const urlNovela = `https://eroverse.onrender.com/novela.html?id=${novelaId}`;

        const embed = new EmbedBuilder()
          .setTitle(novela.titulo || "Nueva novela")
          .addFields(
            { name: 'Géneros', value: (novela.generos || []).join(', ') || 'N/A', inline: false },
            { name: 'Estado', value: novela.estado || 'Desconocido', inline: true },
            { name: 'Peso', value: novela.peso || 'N/A', inline: true }
          )
          .setColor(0x00bfff)
          .setDescription((novela.desc || '') + `\n[Enlace a la novela](${urlNovela})\n¡Nueva novela subida!`);

        embed.setURL(urlNovela);

        if (novela.portada && novela.portada.trim() !== '') {
          embed.setImage(novela.portada);
        }

        await channel.send({ embeds: [embed] });
      }
    }

    if (huboNovedad) {
      // Solo guardar en GitHub, no localmente
      await guardarNovelasEnGitHub([...novelasAnunciadas]);
    }
  } catch (err) {
    console.error("Error al chequear novelas:", err);
  }
}


client.once('ready', () => {
  console.log(`Bot iniciado como ${client.user.tag}`);

  // Ejecutar checkNovelas cada 2 minutos
  setInterval(checkNovelas, 2 * 60 * 1000);

  // Ejecutar checkYouTube cada 5 minutos
  setInterval(checkYouTube, 5 * 60 * 1000);
});

// 2. YouTube: Detectar nuevos videos
const LAST_VIDEO_PATH = './data/lastVideoId.txt';
let lastVideoId = null;

// Cargar el último video anunciado al iniciar
try {
  if (fs.existsSync(LAST_VIDEO_PATH)) {
    lastVideoId = fs.readFileSync(LAST_VIDEO_PATH, 'utf-8').trim() || null;
  }
} catch (e) {
  lastVideoId = null;
}

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
    // Guardar el último ID en archivo
    try {
      fs.writeFileSync(LAST_VIDEO_PATH, lastVideoId, 'utf-8');
    } catch {}

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

// Inicio sesión del bot
client.login(DISCORD_TOKEN);
