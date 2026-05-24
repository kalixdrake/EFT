const MIN_MAJOR = 20;
const MIN_MINOR = 19;
const MIN_PATCH = 4;

const match = process.version.match(/^v(\d+)\.(\d+)\.(\d+)/);
if (!match) {
  console.error('No se pudo detectar la versión de Node.js.');
  process.exit(1);
}

const [, major, minor, patch] = match.map(Number);
const ok =
  major > MIN_MAJOR ||
  (major === MIN_MAJOR && minor > MIN_MINOR) ||
  (major === MIN_MAJOR && minor === MIN_MINOR && patch >= MIN_PATCH);

if (!ok) {
  console.error(`
Expo SDK 56 requiere Node.js >= ${MIN_MAJOR}.${MIN_MINOR}.${MIN_PATCH}.
Versión actual: ${process.version}

Tu terminal está usando el Node del sistema. Activa nvm y vuelve a intentar:

  source ~/.nvm/nvm.sh
  nvm use
  npm start

O abre una terminal nueva (ya debería cargar Node 24 automáticamente).
`);
  process.exit(1);
}
