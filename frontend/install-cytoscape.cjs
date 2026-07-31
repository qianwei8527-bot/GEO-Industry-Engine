const { execSync } = require('child_process');
try {
  const result = execSync('npm install cytoscape', { cwd: 'D:\\GEO-IE\\frontend', stdio: 'pipe', timeout: 30000 });
  console.log(result.toString());
} catch(e) {
  console.error('FAIL:', e.message);
}
