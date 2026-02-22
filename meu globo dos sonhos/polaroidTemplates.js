const wrapText = (text, maxLength = 16) => {
    const words = text.split(' ');
    const lines = [];
    let currentLine = '';
    words.forEach(word => {
        if ((currentLine + word).length > maxLength) {
            if (currentLine) lines.push(currentLine.trim());
            currentLine = word + ' ';
        } else {
            currentLine += word + ' ';
        }
    });
    if (currentLine) lines.push(currentLine.trim());
    return lines;
};

export const polaroidTemplates = [
    {
        title: '1. Formato Clássico',
        photoBox: { x: 35, y: 35, w: 180, h: 170 },
        render: (img, title) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 250 300" width="100%" height="100%">
  <defs>
    <filter id="shadow1" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="5" stdDeviation="5" flood-opacity="0.15"/>
    </filter>
  </defs>
  <g filter="url(#shadow1)">
    <rect x="25" y="25" width="200" height="240" fill="#ffffff" rx="2" />
    ${img ? `<image href="${img}" x="35" y="35" width="180" height="170" preserveAspectRatio="xMidYMid slice" />` : ''}
    <text x="125" y="235" font-family="'Caveat', cursive, sans-serif" font-size="26" text-anchor="middle" fill="#333">
       ${wrapText(title, 16).map((line, i) => `<tspan x="125" dy="${i === 0 ? 0 : 26}">${line}</tspan>`).join('')}
    </text>
  </g>
</svg>`
    },
    {
        title: '2. Colada com Fita Adesiva',
        photoBox: { x: 35, y: 45, w: 180, h: 175 },
        render: (img, title) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 250 300" width="100%" height="100%">
  <defs>
    <filter id="shadow2">
      <feDropShadow dx="2" dy="4" stdDeviation="3" flood-opacity="0.2"/>
    </filter>
  </defs>
  <g filter="url(#shadow2)">
    <rect x="25" y="35" width="200" height="240" fill="#FDF5E6" rx="2" />
    ${img ? `<image href="${img}" x="35" y="45" width="180" height="175" preserveAspectRatio="xMidYMid slice" />` : ''}
    <text x="125" y="245" font-family="'Caveat', cursive, sans-serif" font-size="24" text-anchor="middle" fill="#5c4a3d">
        ${wrapText(title, 18).map((line, i) => `<tspan x="125" dy="${i === 0 ? 0 : 24}">${line}</tspan>`).join('')}
    </text>
  </g>
  <polygon points="100,15 160,10 165,35 105,40" fill="rgba(210, 180, 140, 0.8)" />
</svg>`
    },
    {
        title: '3. Alfinetada e Torta',
        photoBox: { x: 35, y: 40, w: 180, h: 175, rot: -4, px: 125, py: 40 },
        render: (img, title) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 250 300" width="100%" height="100%">
  <defs>
    <filter id="shadow3"><feDropShadow dx="2" dy="6" stdDeviation="4" flood-opacity="0.25"/></filter>
  </defs>
  <g transform="rotate(-4 125 40)">
    <g filter="url(#shadow3)">
      <rect x="25" y="30" width="200" height="240" fill="#fff" rx="1" />
      ${img ? `<image href="${img}" x="35" y="40" width="180" height="175" preserveAspectRatio="xMidYMid slice" />` : ''}
      <text x="125" y="240" font-family="'Caveat', cursive, sans-serif" font-size="22" text-anchor="middle" fill="#444">
          ${wrapText(title, 20).map((line, i) => `<tspan x="125" dy="${i === 0 ? 0 : 22}">${line}</tspan>`).join('')}
      </text>
    </g>
    <circle cx="125" cy="38" r="7" fill="#DC143C" />
    <circle cx="123" cy="36" r="2.5" fill="#fff" opacity="0.6" />
  </g>
</svg>`
    },
    {
        title: '4. Formato Wide (Panorâmico)',
        photoBox: { x: 20, y: 70, w: 160, h: 130 },
        render: (img, title) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 250 300" width="100%" height="100%">
  <defs>
    <filter id="shadow4"><feDropShadow dx="0" dy="3" stdDeviation="3" flood-opacity="0.15"/></filter>
  </defs>
  <g filter="url(#shadow4)" transform="translate(0, 40)">
    <rect x="10" y="20" width="230" height="150" fill="#fafafa" rx="3" />
    ${img ? `<image href="${img}" x="20" y="30" width="160" height="130" preserveAspectRatio="xMidYMid slice" />` : ''}
    <text x="205" y="55" transform="rotate(90 205 55)" font-family="'Caveat', cursive, sans-serif" font-size="16" fill="#555">
        ${wrapText(title, 14).map((line, i) => `<tspan x="205" dy="${i === 0 ? 0 : 16}">${line}</tspan>`).join('')}
    </text>
  </g>
</svg>`
    },
    {
        title: '5. Formato Mini Square',
        photoBox: { x: 50, y: 40, w: 150, h: 150 },
        render: (img, title) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 250 300" width="100%" height="100%">
  <defs>
    <filter id="shadow5"><feDropShadow dx="0" dy="4" stdDeviation="4" flood-opacity="0.1"/></filter>
  </defs>
  <g filter="url(#shadow5)">
    <rect x="40" y="30" width="170" height="230" fill="#fff" rx="4" />
    ${img ? `<image href="${img}" x="50" y="40" width="150" height="150" preserveAspectRatio="xMidYMid slice" />` : ''}
    <text x="125" y="215" font-family="'Caveat', cursive, sans-serif" font-size="24" text-anchor="middle" fill="#333">
        ${wrapText(title, 14).map((line, i) => `<tspan x="125" dy="${i === 0 ? 0 : 24}">${line}</tspan>`).join('')}
    </text>
  </g>
</svg>`
    },
    {
        title: '6. Pendurada em Movimento',
        photoBox: { x: 45, y: 50, w: 160, h: 150 },
        render: (img, title) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 250 300" width="100%" height="100%">
  <defs>
    <filter id="shadow6"><feDropShadow dx="0" dy="4" stdDeviation="3" flood-opacity="0.2"/></filter>
  </defs>
  <line x1="125" y1="0" x2="125" y2="40" stroke="#888" stroke-width="1.5" stroke-dasharray="4" />
  <g>
    <animateTransform attributeName="transform" type="rotate" values="-6 125 0; 6 125 0; -6 125 0" dur="3s" repeatCount="indefinite" />
    <g filter="url(#shadow6)">
      <rect x="35" y="40" width="180" height="210" fill="#fff" />
      ${img ? `<image href="${img}" x="45" y="50" width="160" height="150" preserveAspectRatio="xMidYMid slice" />` : ''}
      <text x="125" y="225" font-family="'Caveat', cursive, sans-serif" font-size="22" text-anchor="middle" fill="#333">
          ${wrapText(title, 16).map((line, i) => `<tspan x="125" dy="${i === 0 ? 0 : 22}">${line}</tspan>`).join('')}
      </text>
    </g>
    <rect x="110" y="30" width="30" height="15" fill="rgba(200,200,200,0.8)" transform="rotate(5 125 35)" />
  </g>
</svg>`
    },
    {
        title: '7. Levitando com Sombra Dinâmica',
        photoBox: { x: 45, y: 40, w: 160, h: 160, dyPulse: -15 },
        render: (img, title) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 250 300" width="100%" height="100%">
  <ellipse cx="125" cy="285" rx="80" ry="8" fill="rgba(0,0,0,0.15)">
     <animate attributeName="rx" values="80; 50; 80" dur="4s" repeatCount="indefinite" />
     <animate attributeName="opacity" values="1; 0.4; 1" dur="4s" repeatCount="indefinite" />
  </ellipse>
  <g>
    <animateTransform attributeName="transform" type="translate" values="0 0; 0 -15; 0 0" dur="4s" repeatCount="indefinite" />
    <rect x="35" y="30" width="180" height="220" fill="#fff" />
    ${img ? `<image href="${img}" x="45" y="40" width="160" height="160" preserveAspectRatio="xMidYMid slice" />` : ''}
    <text x="125" y="225" font-family="'Caveat', cursive, sans-serif" font-size="20" text-anchor="middle" fill="#333">
        ${wrapText(title, 16).map((line, i) => `<tspan x="125" dy="${i === 0 ? 0 : 20}">${line}</tspan>`).join('')}
    </text>
  </g>
</svg>`
    },
    {
        title: '8. Filme Revelando (Aparecendo)',
        photoBox: { x: 35, y: 35, w: 180, h: 180 },
        render: (img, title, is3D = false) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 250 300" width="100%" height="100%">
  <defs>
    <filter id="shadow8"><feDropShadow dx="0" dy="4" stdDeviation="4" flood-opacity="0.15"/></filter>
  </defs>
  <g filter="url(#shadow8)">
    <rect x="25" y="25" width="200" height="240" fill="#fff" />
    <rect x="35" y="35" width="180" height="180" fill="#111">
       ${!is3D ? `<animate attributeName="fill" values="#111; #2F4F4F; #3CB371" dur="6s" fill="freeze" />` : ''}
    </rect>
    ${img ? `<image href="${img}" x="35" y="35" width="180" height="180" preserveAspectRatio="xMidYMid slice" ${!is3D ? 'opacity="0"' : 'opacity="1"'}>
       ${!is3D ? `<animate attributeName="opacity" values="0; 1" dur="6s" fill="freeze" />` : ''}
    </image>` : ''}
    <text x="125" y="235" font-family="'Caveat', cursive, sans-serif" font-size="20" text-anchor="middle" fill="#333">
        ${wrapText(title, 18).map((line, i) => `<tspan x="125" dy="${i === 0 ? 0 : 20}">${line}</tspan>`).join('')}
    </text>
  </g>
</svg>`
    },
    {
        title: '9. Papel Fotográfico Neon',
        photoBox: { x: 35, y: 35, w: 180, h: 170 },
        render: (img, title) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 250 300" width="100%" height="100%">
  <rect x="25" y="25" width="200" height="240" fill="#1a1a1a" rx="5" stroke="#0ff" stroke-width="3">
     <animate attributeName="stroke" values="#0ff; #f0f; #0f0; #0ff" dur="5s" repeatCount="indefinite" />
  </rect>
  ${img ? `<image href="${img}" x="35" y="35" width="180" height="170" preserveAspectRatio="xMidYMid slice" />` : '<rect x="35" y="35" width="180" height="170" fill="#000" />'}
  <text x="125" y="235" font-family="'Courier New', Courier, monospace" font-size="16" text-anchor="middle" fill="#fff">
     <animate attributeName="fill" values="#0ff; #f0f; #0f0; #0ff" dur="5s" repeatCount="indefinite" />
     ${wrapText(title, 16).map((line, i) => `<tspan x="125" dy="${i === 0 ? 0 : 16}">${line}</tspan>`).join('')}
  </text>
</svg>`
    },
    {
        title: '10. Dupla Exposição e Flash',
        photoBox: { x: 45, y: 35, w: 180, h: 180 },
        render: (img, title, is3D = false) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 250 300" width="100%" height="100%">
  <defs>
    <filter id="shadow10"><feDropShadow dx="2" dy="2" stdDeviation="2" flood-opacity="0.1"/></filter>
  </defs>
  <g filter="url(#shadow10)">
    <rect x="15" y="45" width="200" height="230" fill="#eee" transform="rotate(-6 115 165)" />
  </g>
  <g filter="url(#shadow10)">
    <rect x="35" y="25" width="200" height="240" fill="#fff" />
    ${img ? `<image href="${img}" x="45" y="35" width="180" height="180" preserveAspectRatio="xMidYMid slice" />` : ''}
    ${!is3D ? `<rect x="45" y="35" width="180" height="180" fill="#ffffff" opacity="0">
       <animate attributeName="opacity" values="1; 0; 0" dur="4s" repeatCount="indefinite" keyTimes="0; 0.15; 1" />
    </rect>` : ''}
    <text x="135" y="235" font-family="'Caveat', cursive, sans-serif" font-size="20" text-anchor="middle" fill="#333">
        ${wrapText(title, 18).map((line, i) => `<tspan x="135" dy="${i === 0 ? 0 : 20}">${line}</tspan>`).join('')}
    </text>
  </g>
</svg>`
    },
    {
        title: '11. O Super Mix',
        photoBox: { x: 45, y: 35, w: 180, h: 180, rot: -5, px: 125, py: 30, swing: true },
        render: (img, title, is3D = false) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 250 300" width="100%" height="100%">
  <defs>
    <filter id="shadowMix"><feDropShadow dx="2" dy="4" stdDeviation="3" flood-opacity="0.25"/></filter>
  </defs>
  <g>
    ${!is3D ? `<animateTransform attributeName="transform" type="rotate" values="-5 125 30; 5 125 30; -5 125 30" dur="3.5s" repeatCount="indefinite" />` : ''}
    <g filter="url(#shadowMix)">
      <rect x="15" y="45" width="200" height="230" fill="#FDF5E6" transform="rotate(-8 115 165)" />
    </g>
    <g filter="url(#shadowMix)">
      <rect x="35" y="25" width="200" height="240" fill="#fff" />
      ${img ? `<image href="${img}" x="45" y="35" width="180" height="180" preserveAspectRatio="xMidYMid slice" />` : ''}
      ${!is3D ? `<rect x="45" y="35" width="180" height="180" fill="#ffffff" opacity="0">
         <animate attributeName="opacity" values="1; 0; 0" dur="4s" repeatCount="indefinite" keyTimes="0; 0.15; 1" />
      </rect>` : ''}
      <text x="135" y="235" font-family="'Caveat', cursive, sans-serif" font-size="20" text-anchor="middle" fill="#333">
          ${wrapText(title, 18).map((line, i) => `<tspan x="135" dy="${i === 0 ? 0 : 20}">${line}</tspan>`).join('')}
      </text>
    </g>
  </g>
  <circle cx="125" cy="30" r="7" fill="#DC143C" />
  <circle cx="123" cy="28" r="2.5" fill="#fff" opacity="0.6" />
</svg>`
    }
];
