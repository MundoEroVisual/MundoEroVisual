const archiver = require('archiver');
const fetch = require('node-fetch');
const stream = require('stream');
const { promisify } = require('util');
const pipeline = promisify(stream.pipeline);

async function fetchImageToStream(url, destStream) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`No se pudo descargar la imagen: ${url}`);
  await pipeline(response.body, destStream);
}

module.exports = { fetchImageToStream, archiver };
