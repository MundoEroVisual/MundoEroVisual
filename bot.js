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
const CANAL_SORTEO_ID = "1396642489464520776";
const CANAL_ANUNCIOS_ID = "1372061643105898527";

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
  await cargarSorteoActivo();

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

  // Enviar botón al canal de ayuda solo si no existe ya
  const canal = await client.channels.fetch(CANAL_AYUDA_ID).catch(() => null);
  if (canal && canal.isTextBased()) {
    // Buscar si ya existe el mensaje del botón en los últimos 20 mensajes
    const mensajes = await canal.messages.fetch({ limit: 20 }).catch(() => null);
    const yaExiste = mensajes && mensajes.some(m =>
      m.author.id === client.user.id &&
      m.content.includes("¿Necesitas ayuda? Haz clic en el botón para abrir un ticket.") &&
      m.components && m.components.length > 0
    );
    if (!yaExiste) {
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

  // --- SORTEO VIP ---
  if (interaction.isChatInputCommand() && interaction.commandName === "crearsorteo") {
    if (!interaction.member.permissions.has(PermissionFlagsBits.Administrator)) {
      await interaction.reply({ content: "Solo administradores pueden crear sorteos.", ephemeral: true });
      return;
    }
    // Recoge los parámetros
    const tipo = interaction.options.getString("tipo") || "VIP";
    const duracion = interaction.options.getString("duracion") || "45m";
    const canal = interaction.options.getChannel("canal") || await client.channels.fetch(CANAL_SORTEO_ID);
    let msDuracion = 45 * 60 * 1000;
    let duracionTexto = "45 minutos";
    const duracionMatch = duracion.match(/^(\d+)([mhd])$/i);
    if (duracionMatch) {
      const valor = parseInt(duracionMatch[1]);
      const unidad = duracionMatch[2].toLowerCase();
      if (unidad === "m") {
        msDuracion = valor * 60 * 1000;
        duracionTexto = `${valor} minuto${valor === 1 ? '' : 's'}`;
      } else if (unidad === "h") {
        msDuracion = valor * 60 * 60 * 1000;
        duracionTexto = `${valor} hora${valor === 1 ? '' : 's'}`;
      } else if (unidad === "d") {
        msDuracion = valor * 24 * 60 * 60 * 1000;
        duracionTexto = `${valor} día${valor === 1 ? '' : 's'}`;
      }
    }
    const termina = Date.now() + msDuracion;
    sorteoActual = {
      tipo,
      premio: "VIP Gratis",
      ganadores: 1,
      termina,
      canalParticipacion: canal.id,
      participantes: new Set()
    };
    // Guardar sorteo en GitHub
    guardarSorteoEnGitHub({
      tipo,
      premio: "VIP Gratis",
      ganadores: 1,
      termina,
      canalParticipacion: canal.id,
      fechaCreacion: new Date().toISOString(),
      creador: interaction.user ? interaction.user.id : null
    });
    // Mensaje de sorteo
    const mensajeSorteo = `🎉 ¡SORTEO ACTIVO! 🎉\n¿Quieres ganar VIP Gratis?\n\n🎁 Premio: VIP Gratis\n🏆 Ganadores: 1\n⏳ Termina en: ${duracionTexto} (hora estimada)\n\n📌 Requisitos para ganar:\n🔴 Seguirme en YouTube\n💬 Comentar "SORTEO" con tu nombre de Discord en mi último video\n👍 Darle like al video\n\n✨ Beneficios del VIP:\n🔗 Enlaces directos sin publicidad\n🎧 Soporte prioritario\n📥 Actualizaciones anticipadas\n🎁 ¡Y mucho más!\n\n📢 ¿Cómo participar?\nEscribe **/sorteo** en el canal <#${canal.id}>`;
    // Enviar a todos los canales permitidos
    client.guilds.cache.forEach(async (guild) => {
      guild.channels.cache.forEach(async (ch) => {
        if (ch.isTextBased() && ch.permissionsFor(client.user).has(PermissionFlagsBits.SendMessages)) {
          try {
            await ch.send(mensajeSorteo);
          } catch {}
        }
      });
    });
    // Enviar y fijar el mensaje en el canal de sorteos
    const canalSorteo = await client.channels.fetch(CANAL_SORTEO_ID);
    const msgFijado = await canalSorteo.send(mensajeSorteo);
    await msgFijado.pin();
    // Mensaje de reglas
    await canalSorteo.send(`⚠️ En este canal solo se permite escribir /sorteo. Si escribes cualquier otra cosa serás sancionado. Si necesitas ayuda abre un ticket en el canal de ayuda.`);
    await interaction.reply({ content: "✅ Sorteo creado y anunciado.", ephemeral: true });
    // Timer para finalizar sorteo
    setTimeout(async () => {
      if (!sorteoActual) return;
      const participantes = Array.from(sorteoActual.participantes);
      if (participantes.length === 0) {
        await canalSorteo.send("⏰ Sorteo finalizado. No hubo participantes.");
      } else {
        const ganador = participantes[Math.floor(Math.random() * participantes.length)];
        await canalSorteo.send('🎊 ¡SORTEO FINALIZADO!\n\n🏆 Ganador del VIP Gratis: <@' + ganador + '>\n🎉 ¡Felicidades!');
      }
      sorteoActual = null;
    }, msDuracion);
  }
  // Comando para participar
  if (interaction.commandName === "sorteo") {
    if (!sorteoActual || Date.now() > sorteoActual.termina) {
      await interaction.reply({ content: "No hay sorteo activo.", ephemeral: true });
      return;
    }
    if (interaction.channelId !== sorteoActual.canalParticipacion) {
      await interaction.reply({ content: `Debes participar en el canal <#${sorteoActual.canalParticipacion}>.`, ephemeral: true });
      return;
    }
    const userId = interaction.user.id;
    if (sorteoActual.participantes.has(userId)) {
      await interaction.reply({ content: '🛑 Ya estás participando en el sorteo actual.\n\n🧧 Premio: VIP Gratis\n🏆 Ganadores: 1\n⏳ Termina en: ' + Math.ceil((sorteoActual.termina - Date.now())/60000) + ' minutos', ephemeral: true });
      return;
    }
    sorteoActual.participantes.add(userId);
    await interaction.reply({ content: '🎉 ¡Te has registrado en el sorteo!\n\n🧧 Premio: VIP Gratis\n🏆 Ganadores: 1\n⏳ Termina en: ' + Math.ceil((sorteoActual.termina - Date.now())/60000) + ' minutos\n\n📌 REQUISITOS:\nSeguirme en YouTube\nComentar "SORTEO" con tu usuario de Discord en el último video\nDarle like\n\n✨ Beneficios:\nAcceso a enlaces directos de descarga de todas las novelas\nSin publicidad\nSoporte prioritario\nActualizaciones anticipadas\n¡Y mucho más!', ephemeral: true });
  }
});

// --------------------------------
// --- COMANDOS DE TEXTO RESTAURADOS ---
let sorteoActual = null;
client.on("messageCreate", async (msg) => {
  if (msg.author.bot || !msg.guild) return;
  if (!msg.content.startsWith("!")) return;

  const args = msg.content.slice(1).trim().split(/ +/);
  const command = args.shift().toLowerCase();
  const isAdmin = msg.member.permissions.has(PermissionFlagsBits.Administrator);

  // Solo admins pueden usar estos comandos, excepto !anuncio y !sorteo
  if (!isAdmin && !["anuncio", "sorteo"].includes(command)) return;

  // !comandos para mostrar todos los comandos disponibles
  if (command === "comandos") {
    const comandos = [
      "`!crearsorteo tipo: VIP duracion: 1m canal: #sorteo` — Crea un sorteo VIP.",
      "`!sorteo` — Participa en el sorteo VIP.",
      "`!sorteo + @usuario` — Añade manualmente a un usuario al sorteo (solo admins).",
      "`!sorteocantidad` — Muestra la cantidad y lista de usuarios participando en el sorteo VIP.",
      "`!ultimanovela` — Vuelve a anunciar la última novela subida.",
      "`!clear <n>` — Borra los últimos n mensajes del canal.",
      "`!clearall` — Borra todos los mensajes del canal actual.",
      "`!vip + @usuario nombreEnWeb` — Añade un usuario como VIP (Discord y web, asigna rol VIP).",
      "`!vip - @usuario [nombreEnWeb]` — Elimina el VIP de un usuario (Discord y web, quita rol VIP).",
      "`!vip lista` — Muestra la lista de usuarios VIP.",
      "`!reanunciar-novelas` — Vuelve a anunciar todas las novelas (resetea la lista).",
      "`!refrescar-novelas` — Fuerza la relectura del JSON y reanuncia novelas nuevas.",
      "`!ping` — Prueba de latencia/respuesta del bot.",
      "`!ban @usuario <motivo>` — Banea a un usuario.",
      "`!kick @usuario <motivo>` — Expulsa a un usuario.",
      "`!anuncio <mensaje>` — Envía un anuncio a todos los canales configurados.",
      "`!userinfo [@usuario]` — Muestra información de un usuario.",
      "`!serverinfo` — Muestra información del servidor."
    ];
    msg.reply({ content: comandos.join("\n") });
    return;
  }
  // !sorteocantidad para mostrar participantes del sorteo
  if (command === "sorteocantidad") {
    if (!sorteoActual) {
      const replyMsg = await msg.reply("No hay sorteo activo.");
      setTimeout(() => replyMsg.delete().catch(() => {}), 5000);
      return;
    }
    const participantes = Array.from(sorteoActual.participantes);
    if (participantes.length === 0) {
      const replyMsg = await msg.reply("No hay usuarios participando en el sorteo.");
      setTimeout(() => replyMsg.delete().catch(() => {}), 5000);
      return;
    }
    // Obtener los nombres de usuario
    const nombres = await Promise.all(participantes.map(async id => {
      try {
        const miembro = await msg.guild.members.fetch(id);
        return miembro.user.tag;
      } catch {
        return id;
      }
    }));
    const replyMsg = await msg.reply(`👥 Participantes en el sorteo (${participantes.length}):\n${nombres.join("\n")}`);
    setTimeout(() => replyMsg.delete().catch(() => {}), 10000);
    return;
  }

  // !crearsorteo tipo: VIP duracion: 1m canal: #sorteos
  if (isAdmin && command === "crearsorteo") {
    // Impedir crear un sorteo si hay uno activo
    if (sorteoActual && Date.now() < sorteoActual.termina) {
      const replyMsg = await msg.reply("Ya hay un sorteo activo. Espera a que termine antes de crear otro.");
      setTimeout(() => replyMsg.delete().catch(() => {}), 5000);
      return;
    }
    const tipoMatch = msg.content.match(/tipo:\s*(\w+)/i);
    const duracionMatch = msg.content.match(/duracion:\s*(\d+[mhd])/i);
    const canalMatch = msg.content.match(/canal:\s*#?(\w+)/i);
    const tipo = tipoMatch ? tipoMatch[1] : "VIP";
    const duracion = duracionMatch ? duracionMatch[1] : "45m";
    let msDuracion = 45 * 60 * 1000;
    let duracionTexto = "45 minutos";
    if (duracionMatch) {
      const valor = parseInt(duracion.match(/(\d+)/)[1]);
      const unidad = duracion.match(/([mhd])/i)[1].toLowerCase();
      if (unidad === "m") {
        msDuracion = valor * 60 * 1000;
        duracionTexto = `${valor} minuto${valor === 1 ? '' : 's'}`;
      } else if (unidad === "h") {
        msDuracion = valor * 60 * 60 * 1000;
        duracionTexto = `${valor} hora${valor === 1 ? '' : 's'}`;
      } else if (unidad === "d") {
        msDuracion = valor * 24 * 60 * 60 * 1000;
        duracionTexto = `${valor} día${valor === 1 ? '' : 's'}`;
      }
    }
    let canalId = CANAL_SORTEO_ID;
    if (canalMatch) {
      // Buscar canal por nombre
      const canalObj = msg.guild.channels.cache.find(c => c.name === canalMatch[1]);
      if (canalObj) canalId = canalObj.id;
    }
    const termina = Date.now() + msDuracion;
    sorteoActual = {
      tipo,
      premio: "VIP Gratis",
      ganadores: 1,
      termina,
      canalParticipacion: canalId,
      participantes: new Set()
    };
    // Guardar sorteo en GitHub (incluye participantes)
    await guardarSorteoEnGitHub({
      tipo,
      premio: "VIP Gratis",
      ganadores: 1,
      termina,
      canalParticipacion: canalId,
      fechaCreacion: new Date().toISOString(),
      creador: msg.author ? msg.author.id : null,
      participantes: []
    });
    const mensajeReglas = `⚠️ En este canal solo se permite escribir !sorteo. Si escribes cualquier otra cosa serás sancionado. Si necesitas ayuda abre un ticket en el canal de ayuda.`;
    const mensajeSorteo = `🎉 ¡SORTEO ACTIVO! 🎉\n¿Quieres ganar VIP Gratis?\n\n🎁 Premio: VIP Gratis\n🏆 Ganadores: 1\n⏳ Termina en: ${duracionTexto} (hora estimada)\n\n📌 Requisitos para ganar:\n🔴 Seguirme en YouTube\n💬 Comentar "SORTEO" con tu nombre de Discord en mi último video\n👍 Darle like al video\n\n✨ Beneficios del VIP:\n🔗 Enlaces directos sin publicidad\n🎧 Soporte prioritario\n📥 Actualizaciones anticipadas\n🎁 ¡Y mucho más!\n\n📢 ¿Cómo participar?\nEscribe **!sorteo** en el canal <#${canalId}>`;
    // Enviar y fijar el mensaje en el canal de sorteos
    const canalSorteo = await msg.guild.channels.fetch(canalId);
    const msgFijado = await canalSorteo.send(mensajeSorteo);
    await msgFijado.pin();
    // Enviar el mensaje de reglas justo después del sorteo
    await canalSorteo.send(mensajeReglas);
    // Enviar aviso de sorteo creado solo al canal de anuncios (NO se elimina)
    const aviso = `✅ ¡Se ha creado un nuevo sorteo VIP! Participa en el canal <#${canalId}> usando !sorteo.`;
    try {
      const canalAviso = await client.channels.fetch(CANAL_ANUNCIOS_ID);
      if (canalAviso) {
        await canalAviso.send(aviso);
      }
    } catch {}
    setTimeout(async () => {
      if (!sorteoActual) return;
      const participantes = Array.from(sorteoActual.participantes);
      if (participantes.length === 0) {
        await canalSorteo.send("⏰ Sorteo finalizado. No hubo participantes.");
      } else {
        const ganador = participantes[Math.floor(Math.random() * participantes.length)];
        await canalSorteo.send('🎊 ¡SORTEO FINALIZADO!\n\n🏆 Ganador del VIP Gratis: <@' + ganador + '>\n🎉 ¡Felicidades!');
      }
      // Eliminar sorteo del archivo
      await guardarSorteoEnGitHub({
        tipo: sorteoActual.tipo,
        premio: sorteoActual.premio,
        ganadores: sorteoActual.ganadores,
        termina: sorteoActual.termina,
        canalParticipacion: sorteoActual.canalParticipacion,
        fechaCreacion: sorteoActual.fechaCreacion,
        creador: sorteoActual.creador,
        participantes: Array.from(sorteoActual.participantes)
      }, true);
      sorteoActual = null;
    }, msDuracion);
    return;
  }

  // !sorteo para participar
  if (command === "sorteo") {
    // Si el admin usa !sorteo + @usuario para añadir manualmente
    if (isAdmin && args[0] === "+" && args[1]) {
      const userMention = args[1];
      const userIdMatch = userMention.match(/^<@!?([0-9]+)>$/);
      let userId = null;
      if (userIdMatch) {
        userId = userIdMatch[1];
      } else {
        // Si no es mención, intentar buscar por nombre
        const miembro = msg.guild.members.cache.find(m => m.user.tag === userMention || m.user.username === userMention);
        if (miembro) userId = miembro.id;
      }
      if (!userId) {
        const replyMsg = await msg.reply("Usuario no válido o no encontrado.");
        setTimeout(() => replyMsg.delete().catch(() => {}), 5000);
        return;
      }
      if (!sorteoActual) {
        const replyMsg = await msg.reply("No hay sorteo activo.");
        setTimeout(() => replyMsg.delete().catch(() => {}), 5000);
        return;
      }
      if (sorteoActual.participantes.has(userId)) {
        const replyMsg = await msg.reply(`El usuario ya está participando en el sorteo.`);
        setTimeout(() => replyMsg.delete().catch(() => {}), 5000);
        return;
      }
      sorteoActual.participantes.add(userId);
      // Guardar participantes en GitHub
      await guardarSorteoEnGitHub({
        tipo: sorteoActual.tipo,
        premio: sorteoActual.premio,
        ganadores: sorteoActual.ganadores,
        termina: sorteoActual.termina,
        canalParticipacion: sorteoActual.canalParticipacion,
        fechaCreacion: sorteoActual.fechaCreacion,
        creador: sorteoActual.creador,
        participantes: Array.from(sorteoActual.participantes)
      });
      const miembro = await msg.guild.members.fetch(userId).catch(() => null);
      const nombre = miembro ? miembro.user.tag : userId;
      const replyMsg = await msg.reply(`✅ El usuario ${nombre} ha sido añadido al sorteo.`);
      setTimeout(() => replyMsg.delete().catch(() => {}), 5000);
      return;
    }
    // Participación normal
    if (sorteoActual && msg.channelId === sorteoActual.canalParticipacion) {
      const userId = msg.author.id;
      if (sorteoActual.participantes.has(userId)) {
        const replyMsg = await msg.reply('🛑 Ya estás participando en el sorteo actual.\n\n🧧 Premio: VIP Gratis\n🏆 Ganadores: 1\n⏳ Termina en: ' + Math.ceil((sorteoActual.termina - Date.now())/60000) + ' minutos');
        setTimeout(() => replyMsg.delete().catch(() => {}), 5000);
        return;
      }
      sorteoActual.participantes.add(userId);
      // Guardar participantes en GitHub
      await guardarSorteoEnGitHub({
        tipo: sorteoActual.tipo,
        premio: sorteoActual.premio,
        ganadores: sorteoActual.ganadores,
        termina: sorteoActual.termina,
        canalParticipacion: sorteoActual.canalParticipacion,
        fechaCreacion: sorteoActual.fechaCreacion,
        creador: sorteoActual.creador,
        participantes: Array.from(sorteoActual.participantes)
      });
      const replyMsg = await msg.reply('🎉 ¡Te has registrado en el sorteo!\n\n🧧 Premio: VIP Gratis\n🏆 Ganadores: 1\n⏳ Termina en: ' + Math.ceil((sorteoActual.termina - Date.now())/60000) + ' minutos\n\n📌 REQUISITOS:\nSeguirme en YouTube\nComentar "SORTEO" con tu usuario de Discord en el último video\nDarle like\n\n✨ Beneficios:\nAcceso a enlaces directos de descarga de todas las novelas\nSin publicidad\nSoporte prioritario\nActualizaciones anticipadas\n¡Y mucho más!');
      setTimeout(() => replyMsg.delete().catch(() => {}), 5000);
      return;
    }
  }

  // Moderación en canal de sorteos: solo !sorteo permitido para no admins
  if (
    msg.channelId === CANAL_SORTEO_ID &&
    !msg.author.bot &&
    !msg.content.startsWith("!sorteo") &&
    !msg.member.permissions.has(PermissionFlagsBits.Administrator)
  ) {
    await msg.delete();
    const reglasMsg = await msg.channel.send("⚠️ En este canal solo se permite escribir !sorteo. Si escribes cualquier otra cosa serás sancionado. Si necesitas ayuda abre un ticket en el canal de ayuda.");
    setTimeout(() => reglasMsg.delete().catch(() => {}), 5000);
    return;
  }

  // --- Comandos de administración ---
  if (command === "refrescar-novelas") {
    try {
      await checkNovelas();
      msg.reply("✅ Lista de novelas refrescada y anunciadas si hay novedades.");
    } catch (e) {
      msg.reply("Error al refrescar novelas.");
    }
    return;
  }

  // !ultimanovela para volver a anunciar la última novela subida
  if (command === "ultimanovela") {
    try {
      // Leer el JSON de novelas
      const res = await fetch('https://raw.githubusercontent.com/MundoEroVisual/MundoEroVisual/main/data/novelas-1.json');
      const data = await res.json();
      if (!Array.isArray(data) || !data.length) {
        msg.reply("No hay novelas disponibles.");
        return;
      }
      const novela = data[data.length - 1];
      if (!novela) {
        msg.reply("No se encontró la última novela.");
        return;
      }
      // Canal original
      const channel = await client.channels.fetch(DISCORD_CHANNEL_JUEGOS_NOPOR);
      // Canal VIP
      const canalVipId = "1396729794325905479";
      const channelVip = await client.channels.fetch(canalVipId).catch(() => null);

      // Enlace público
      const novelaId = novela._id || novela.id;
      const urlNovela = `https://eroverse.onrender.com/novela.html?id=${novelaId}`;
      // Enlace VIP (android_vip)
      const urlVip = novela.android_vip || urlNovela;

      // Embed para canal público
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
      // Adjuntar imágenes de spoiler si existen
      let filesPublico = [];
      if (Array.isArray(novela.spoiler_imgs) && novela.spoiler_imgs.length) {
        filesPublico = novela.spoiler_imgs.filter(img => typeof img === 'string' && img.trim() !== '');
      }
      await channel.send({ embeds: [embed], files: filesPublico });

      // Embed para canal VIP
      if (channelVip) {
        const embedVip = new EmbedBuilder()
          .setTitle(novela.titulo || "Nueva novela VIP")
          .addFields(
            { name: 'Géneros', value: (novela.generos || []).join(', ') || 'N/A', inline: false },
            { name: 'Estado', value: novela.estado || 'Desconocido', inline: true },
            { name: 'Peso', value: novela.peso || 'N/A', inline: true },
            { name: 'Enlace VIP', value: `[Descargar VIP](${urlVip})`, inline: false }
          )
          .setColor(0xffd700)
          .setDescription((novela.desc || '') + `\n¡Nueva novela subida para VIP!`);
        embedVip.setURL(urlVip);
        if (novela.portada && novela.portada.trim() !== '') {
          embedVip.setImage(novela.portada);
        }
        // Adjuntar imágenes de spoiler si existen
        let files = [];
        if (Array.isArray(novela.spoiler_imgs) && novela.spoiler_imgs.length) {
          files = novela.spoiler_imgs.filter(img => typeof img === 'string' && img.trim() !== '');
        }
        await channelVip.send({ embeds: [embedVip], files });
      }
      msg.reply("✅ Última novela anunciada en ambos canales.");
    } catch (e) {
      msg.reply("Error al anunciar la última novela.");
    }
    return;
  }

  if (command === "userinfo") {
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
    const canales = [
      DISCORD_CHANNEL_WELCOME,
      DISCORD_CHANNEL_MEMES,
      DISCORD_CHANNEL_JUEGOS_NOPOR,
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
// --- SISTEMA VIP DISCORD-WEB ---
async function cargarVipsDesdeGitHub() {
  try {
    const { Octokit } = await import("@octokit/rest");
    const octokit = new Octokit({ auth: GITHUB_TOKEN });
    const owner = GITHUB_OWNER;
    const repo = GITHUB_REPO;
    const path = "data/usuario.json";
    const branch = GITHUB_BRANCH || "main";
    let usuarios = [];
    try {
      const { data: fileData } = await octokit.repos.getContent({ owner, repo, path, ref: branch });
      const content = Buffer.from(fileData.content, 'base64').toString('utf-8');
      usuarios = JSON.parse(content);
      if (!Array.isArray(usuarios)) usuarios = [];
    } catch (e) {
      usuarios = [];
    }
    // Solo los que tienen premium=true
    return usuarios.filter(u => u.premium);
  } catch (error) {
    console.error("❌ Error al cargar VIPs:", error.message);
    return [];
  }
}

async function guardarVipsEnGitHub(vips) {
  try {
    const { Octokit } = await import("@octokit/rest");
    const octokit = new Octokit({ auth: GITHUB_TOKEN });
    const owner = GITHUB_OWNER;
    const repo = GITHUB_REPO;
    const path = "data/usuario.json";
    const branch = GITHUB_BRANCH || "main";
    let usuarios = [];
    let sha = undefined;
    try {
      const { data: fileData } = await octokit.repos.getContent({ owner, repo, path, ref: branch });
      sha = fileData.sha;
      const content = Buffer.from(fileData.content, 'base64').toString('utf-8');
      usuarios = JSON.parse(content);
      if (!Array.isArray(usuarios)) usuarios = [];
    } catch (e) {
      sha = undefined;
      usuarios = [];
    }
    // Actualizar usuarios VIP (premium=true) según vips
    // vips: [{ discordId, webUser }]
    // Si existe usuario con webUser, actualizar discordId y premium=true
    // Si no existe, crear nuevo usuario VIP
    for (const vip of vips) {
      let usuario = usuarios.find(u => u.usuario === vip.webUser);
      if (usuario) {
        usuario.discordId = vip.discordId;
        usuario.premium = true;
        usuario.premium_expira = vip.premium_expira || null;
      } else {
        usuarios.push({
          usuario: vip.webUser || "",
          password: "",
          admin: false,
          premium: true,
          premium_expira: vip.premium_expira || null,
          discordId: vip.discordId
        });
      }
    }
    // Eliminar premium a los que no están en vips
    usuarios.forEach(u => {
      if (!vips.some(v => v.discordId === u.discordId || v.webUser === u.usuario)) {
        u.premium = false;
        u.discordId = undefined;
        u.premium_expira = null;
      }
    });
    await octokit.repos.createOrUpdateFileContents({
      owner,
      repo,
      path,
      message: "Actualizar VIPs desde Discord",
      content: Buffer.from(JSON.stringify(usuarios, null, 2)).toString("base64"),
      branch,
      sha,
    });
    console.log("✅ VIPs guardados en GitHub");
  } catch (error) {
    console.error("❌ Error al guardar VIPs:", error.message);
  }
}

client.on("messageCreate", async (msg) => {
  if (msg.author.bot || !msg.guild) return;
  if (!msg.content.startsWith("!vip")) return;
  const args = msg.content.slice(4).trim().split(/ +/);
  const isAdmin = msg.member.permissions.has(PermissionFlagsBits.Administrator);
  if (!isAdmin) {
    msg.reply("Solo administradores pueden gestionar VIPs.");
    return;
  }
  // !vip + @usuario nombreEnWeb
  if (args[0] === "+" && args[1]) {
    const userMention = args[1];
    const webUser = args[2] || null;
    const userIdMatch = userMention.match(/^<@!?([0-9]+)>$/);
    let discordId = null;
    if (userIdMatch) {
      discordId = userIdMatch[1];
    } else {
      const miembro = msg.guild.members.cache.find(m => m.user.tag === userMention || m.user.username === userMention);
      if (miembro) discordId = miembro.id;
    }
    if (!discordId) {
      msg.reply("Usuario no válido o no encontrado.");
      return;
    }
    let vips = await cargarVipsDesdeGitHub();
    if (vips.some(v => v.discordId === discordId || (webUser && v.usuario === webUser))) {
      msg.reply("Ese usuario ya es VIP.");
      return;
    }
    // Por defecto, VIP 30 días si no se especifica fecha
    let premium_expira = new Date();
    premium_expira.setDate(premium_expira.getDate() + 30);
    let actualizado = false;
    // Buscar si ya existe el usuario por discordId o webUser
    for (let vip of vips) {
      if (vip.discordId === discordId || (webUser && vip.webUser === webUser)) {
        vip.premium_expira = premium_expira.toISOString();
        vip.discordId = discordId;
        if (webUser) vip.webUser = webUser;
        vip.premium = true;
        actualizado = true;
      }
    }
    if (!actualizado) {
      vips.push({ discordId, webUser, premium_expira: premium_expira.toISOString(), premium: true });
    }
    await guardarVipsEnGitHub(vips);
    // Asignar rol VIP en Discord
    try {
      const VIP_ROLE_ID = "1372074678692216842";
      const miembro = await msg.guild.members.fetch(discordId);
      if (miembro && !miembro.roles.cache.has(VIP_ROLE_ID)) {
        await miembro.roles.add(VIP_ROLE_ID);
      }
    } catch (e) {
      // Si ves un error de permisos aquí, asegúrate de que el bot tenga el rol más alto que el rol VIP y permisos de Gestionar roles.
      console.error("Error asignando rol VIP:", e);
    }
    msg.reply(`✅ Usuario <@${discordId}> añadido/renovado como VIP${webUser ? ` (web: ${webUser})` : ''} y rol VIP asignado hasta ${premium_expira.toISOString().slice(0,10)}.`);
    return;
// Tarea periódica para quitar el rol VIP si expiró la membresía
const VIP_ROLE_ID = "1372074678692216842";
setInterval(async () => {
  try {
    const vips = await cargarVipsDesdeGitHub();
    const ahora = new Date();
    for (const guild of client.guilds.cache.values()) {
      for (const vip of vips) {
        if (!vip.discordId || !vip.premium_expira) continue;
        const expira = new Date(vip.premium_expira);
        if (expira < ahora) {
          // Quitar rol VIP si lo tiene
          try {
            const miembro = await guild.members.fetch(vip.discordId).catch(() => null);
            if (miembro && miembro.roles.cache.has(VIP_ROLE_ID)) {
              await miembro.roles.remove(VIP_ROLE_ID);
              console.log(`Rol VIP removido a ${miembro.user.tag} por expiración.`);
            }
          } catch (e) {
            // Puede que el usuario no esté en el servidor
          }
        } else {
          // Si aún es VIP y no tiene el rol, asignarlo
          try {
            const miembro = await guild.members.fetch(vip.discordId).catch(() => null);
            if (miembro && !miembro.roles.cache.has(VIP_ROLE_ID)) {
              await miembro.roles.add(VIP_ROLE_ID);
              console.log(`Rol VIP asignado a ${miembro.user.tag} (verificación periódica).`);
            }
          } catch (e) {}
        }
      }
    }
  } catch (e) {
    console.error("Error en la verificación de expiración de VIPs:", e);
  }
}, 60 * 1000); // Cada minuto
  }
  // !vip - @usuario
  if (args[0] === "-" && args[1]) {
    const userMention = args[1];
    const webUser = args[2] || null;
    const userIdMatch = userMention.match(/^<@!?([0-9]+)>$/);
    let discordId = null;
    if (userIdMatch) {
      discordId = userIdMatch[1];
    } else {
      const miembro = msg.guild.members.cache.find(m => m.user.tag === userMention || m.user.username === userMention);
      if (miembro) discordId = miembro.id;
    }
    let vips = await cargarVipsDesdeGitHub();
    const antes = vips.length;
    vips = vips.filter(v => {
      if (discordId && v.discordId === discordId) return false;
      if (webUser && v.webUser === webUser) return false;
      return true;
    });
    if (vips.length === antes) {
      msg.reply("No se encontró ese VIP.");
      return;
    }
    await guardarVipsEnGitHub(vips);
    msg.reply("✅ VIP eliminado.");
    return;
  }
  // !vip lista
  if (args[0] === "lista") {
    let vips = await cargarVipsDesdeGitHub();
    if (!vips.length) {
      msg.reply("No hay usuarios VIP.");
      return;
    }
    const lines = vips.map(v => `Discord: <@${v.discordId}>${v.usuario ? ` | Web: ${v.usuario}` : ''}`);
    msg.reply(`👑 Lista de VIPs:\n${lines.join('\n')}`);
    return;
  }
});
});
// 2. COMANDOS DE ADMINISTRACIÓN
// --------------------------------

// --- El bloque de comandos de texto ha sido eliminado. Usa solo comandos slash (/).
// --- El bloque de comandos de texto ha sido eliminado. Usa solo comandos slash (/).

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

    // Canal original
    const channel = await client.channels.fetch(DISCORD_CHANNEL_JUEGOS_NOPOR);
    if (!channel) {
      console.error("Canal para anuncios no encontrado");
      return;
    }
    // Canal VIP
    const canalVipId = "1396729794325905479";
    const channelVip = await client.channels.fetch(canalVipId).catch(() => null);

    let huboNovedad = false;

    for (const novela of data) {
      const novelaId = novela._id || novela.id;
      if (!novelasAnunciadas.has(novelaId)) {
        novelasAnunciadas.add(novelaId);
        huboNovedad = true;

        // Enlace público
        const urlNovela = `https://eroverse.onrender.com/novela.html?id=${novelaId}`;
        // Enlace VIP (android_vip)
        const urlVip = novela.android_vip || urlNovela;

        // Embed para canal público
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
        // Adjuntar imágenes de spoiler si existen
        let filesPublico = [];
        if (Array.isArray(novela.spoiler_imgs) && novela.spoiler_imgs.length) {
          filesPublico = novela.spoiler_imgs.filter(img => typeof img === 'string' && img.trim() !== '');
        }
        await channel.send({ embeds: [embed], files: filesPublico });

        // Embed para canal VIP
        if (channelVip) {
          const embedVip = new EmbedBuilder()
            .setTitle(novela.titulo || "Nueva novela VIP")
            .addFields(
              { name: 'Géneros', value: (novela.generos || []).join(', ') || 'N/A', inline: false },
              { name: 'Estado', value: novela.estado || 'Desconocido', inline: true },
              { name: 'Peso', value: novela.peso || 'N/A', inline: true },
              { name: 'Enlace VIP', value: `[Descargar VIP](${urlVip})`, inline: false }
            )
            .setColor(0xffd700)
            .setDescription((novela.desc || '') + `\n¡Nueva novela subida para VIP!`);
          embedVip.setURL(urlVip);
          if (novela.portada && novela.portada.trim() !== '') {
            embedVip.setImage(novela.portada);
          }

          // Adjuntar imágenes de spoiler si existen
          let files = [];
          if (Array.isArray(novela.spoiler_imgs) && novela.spoiler_imgs.length) {
            files = novela.spoiler_imgs.filter(img => typeof img === 'string' && img.trim() !== '');
          }
          // Enviar embed y archivos juntos
          await channelVip.send({ embeds: [embedVip], files });
        }
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

  // Revisar cada minuto que todos los usuarios tengan el rol miembro
  const MIEMBRO_ROLE_ID = "1372066618749751417";
  setInterval(async () => {
    try {
      for (const [guildId, guild] of client.guilds.cache) {
        // Obtener todos los miembros
        const miembros = await guild.members.fetch();
        for (const miembro of miembros.values()) {
          if (!miembro.user.bot && !miembro.roles.cache.has(MIEMBRO_ROLE_ID)) {
            await miembro.roles.add(MIEMBRO_ROLE_ID).catch(() => {});
          }
        }
      }
    } catch (e) {
      console.error("Error asignando rol miembro automáticamente:", e);
    }
  }, 60 * 1000);
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

    const channel = await client.channels.fetch(CANAL_ANUNCIOS_ID);
    await channel.send({ embeds: [embed] });
  } catch (err) {
    console.error('Error comprobando YouTube:', err);
  }
}

// Inicio sesión del bot
client.login(DISCORD_TOKEN);

// Registro de comandos slash personalizados
client.once("ready", async () => {
  // Registrar /crearsorteo
  try {
    await client.application.commands.create({
      name: "crearsorteo",
      description: "Crear un sorteo VIP",
      options: [
        {
          name: "tipo",
          type: 3, // STRING
          description: "Tipo de sorteo",
          required: false
        },
        {
          name: "duracion",
          type: 3, // STRING
          description: "Duración (ejemplo: 1m, 45m)",
          required: false
        },
        {
          name: "canal",
          type: 7, // CHANNEL
          description: "Canal de participación",
          required: false
        }
      ]
    });
    await client.application.commands.create({
      name: "sorteo",
      description: "Participa en el sorteo VIP"
    });
    console.log("Comandos /crearsorteo y /sorteo registrados");
  } catch (err) {
    console.error("Error al registrar comandos de sorteo:", err);
  }
});

// Guardar sorteos en GitHub
// Cargar sorteo activo al iniciar el bot
async function cargarSorteoActivo() {
  try {
    const { Octokit } = await import("@octokit/rest");
    const octokit = new Octokit({ auth: GITHUB_TOKEN });
    const owner = GITHUB_OWNER;
    const repo = GITHUB_REPO;
    const path = "data/sorteos.json";
    const branch = GITHUB_BRANCH || "main";
    let sorteos = [];
    try {
      const { data: fileData } = await octokit.repos.getContent({
        owner,
        repo,
        path,
        ref: branch,
      });
      const content = Buffer.from(fileData.content, 'base64').toString('utf-8');
      sorteos = JSON.parse(content);
      if (!Array.isArray(sorteos)) sorteos = [];
    } catch (e) {
      sorteos = [];
    }
    // Solo cargar el sorteo que no ha terminado
    const ahora = Date.now();
    const activo = sorteos.find(s => s.termina > ahora);
    if (activo) {
      sorteoActual = {
        ...activo,
        participantes: new Set(activo.participantes || [])
      };
      console.log("✅ Sorteo activo cargado desde GitHub");
    }
  } catch (error) {
    console.error("❌ Error al cargar sorteo activo:", error.message);
  }
}
async function guardarSorteoEnGitHub(sorteo, eliminar = false) {
  try {
    const { Octokit } = await import("@octokit/rest");
    const octokit = new Octokit({ auth: GITHUB_TOKEN });
    const owner = GITHUB_OWNER;
    const repo = GITHUB_REPO;
    const path = "data/sorteos.json";
    const branch = GITHUB_BRANCH || "main";
    let sorteos = [];
    let sha = undefined;
    try {
      const { data: fileData } = await octokit.repos.getContent({
        owner,
        repo,
        path,
        ref: branch,
      });
      sha = fileData.sha;
      const content = Buffer.from(fileData.content, 'base64').toString('utf-8');
      sorteos = JSON.parse(content);
      if (!Array.isArray(sorteos)) sorteos = [];
    } catch (e) {
      sha = undefined;
      sorteos = [];
    }
    if (eliminar) {
      // Eliminar el sorteo por id (usa termina como id único)
      sorteos = sorteos.filter(s => s.termina !== sorteo.termina);
    } else {
      // Si ya existe, actualizar; si no, agregar
      const idx = sorteos.findIndex(s => s.termina === sorteo.termina);
      if (idx >= 0) sorteos[idx] = sorteo;
      else sorteos.push(sorteo);
    }
    await octokit.repos.createOrUpdateFileContents({
      owner,
      repo,
      path,
      message: eliminar ? "Eliminar sorteo finalizado" : "Guardar/actualizar sorteo desde el bot",
      content: Buffer.from(JSON.stringify(sorteos, null, 2)).toString("base64"),
      branch,
      sha,
    });
    console.log(eliminar ? "✅ Sorteo eliminado de GitHub" : "✅ Sorteo guardado/actualizado en GitHub");
  } catch (error) {
    console.error("❌ Error al guardar/eliminar sorteo en GitHub:", error.message);
  }
}
