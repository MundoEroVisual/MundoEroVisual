// Script para generar hash de contraseña con bcrypt
const bcrypt = require('bcrypt');
const password = process.argv[2];
if (!password) {
  console.log('Uso: node hash.js <contraseña>');
  process.exit(1);
}
bcrypt.hash(password, 10, (err, hash) => {
  if (err) throw err;
  console.log('Hash:', hash);
});
