const fs = require('fs');
const path = require('path');

function findFiles(dir) {
  let files = [];
  for (const f of fs.readdirSync(dir, {withFileTypes: true})) {
    const fp = path.join(dir, f.name);
    if (f.isDirectory() && f.name !== 'node_modules' && f.name !== 'dist') files.push(...findFiles(fp));
    else if (f.name.endsWith('.jsx')) files.push(fp);
  }
  return files;
}

for (const file of findFiles('src')) {
  const lines = fs.readFileSync(file, 'utf8').split('\n');
  for (let i = 0; i < lines.length - 1; i++) {
    const cur = lines[i].trim();
    const nxt = lines[i+1].trim();
    if (!cur || !nxt) continue;
    
    // REAL duplicate: same className, one has hardcoded text, next has t()
    const curClass = (cur.match(/className=['"]([^'"]+)['"]/)||[])[1];
    const nxtClass = (nxt.match(/className=['"]([^'"]+)['"]/)||[])[1];
    
    if (curClass && nxtClass && curClass === nxtClass && nxt.includes('t(') && !cur.includes('t(')) {
      console.log(path.relative('src',file) + ':' + (i+1) + ' REAL DUP (same class: ' + curClass + ')');
      console.log('  OLD: ' + cur.substring(0,120));
      console.log('  NEW: ' + nxt.substring(0,120));
      console.log();
    }
  }
}
console.log('Done');
