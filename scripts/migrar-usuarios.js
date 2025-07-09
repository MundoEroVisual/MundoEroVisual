// Script para migrar usuarios y proteger contraseñas
const fs = require('fs');
const bcrypt = require('bcrypt');
const usuariosPath = './data/usuarios.json';

let usuarios = [
  { usuario: 'admin', password: '12232931', admin: true }
];

(async () => {
  for (const u of usuarios) {
    u.password = await bcrypt.hash(u.password, 10);
  }
  fs.writeFileSync(usuariosPath, JSON.stringify(usuarios, null, 2));
  console.log('Usuarios migrados y protegidos:', usuarios);
})();
