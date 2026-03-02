const fs = require('fs');
const path = require('path');

function findFiles(dir) {
  let files = [];
  for (const f of fs.readdirSync(dir, {withFileTypes: true})) {
    const full = path.join(dir, f.name);
    if (f.isDirectory() && f.name !== 'node_modules' && f.name !== 'dist') files.push(...findFiles(full));
    else if (f.name.endsWith('.jsx')) files.push(full);
  }
  return files;
}

const files = findFiles('src');
for (const file of files) {
  const content = fs.readFileSync(file, 'utf8');
  const lines = content.split(/\n/);
  
  for (let i = 0; i < lines.length - 1; i++) {
    const curr = lines[i].trimStart();
    const next = lines[i+1].trimStart();
    
    // Pattern: old Portuguese line kept + new translated line added right after
    if (next.includes("t(") && !curr.includes("t(") && curr.length > 15 && next.length > 15) {
      const cTag = (curr.match(/^<(\w+)/) || [])[1];
      const nTag = (next.match(/^<(\w+)/) || [])[1];
      if (cTag && nTag && cTag === nTag) {
        console.log(path.relative('src', file) + ':' + (i+1) + ' DUPLICATE TAG');
        console.log('  OLD: ' + curr.substring(0, 90));
        console.log('  NEW: ' + next.substring(0, 90));
        console.log();
      }
    }
  }
  
  // Check remaining hardcoded Portuguese strings (common patterns)
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    // Skip comments and import lines
    if (line.trim().startsWith('//') || line.trim().startsWith('*') || line.trim().startsWith('import')) continue;
    // Check for Portuguese in JSX text content or string props
    const ptPatterns = [
      />[^<]*[àáâãéêíóôõúç][^<]*</i,
      /['"][^'"]*[àáâãéêíóôõúç][^'"]*['"]/,
    ];
    for (const pat of ptPatterns) {
      if (pat.test(line) && !line.includes('t(') && !line.includes('//') && !line.includes('console.')) {
        // ignore CSS/style lines
        if (line.includes('style=') || line.includes('className=') || line.includes('animation')) continue;
        console.log(path.relative('src', file) + ':' + (i+1) + ' HARDCODED PT: ' + line.trim().substring(0, 100));
      }
    }
  }
}
console.log('\nDone scanning');
