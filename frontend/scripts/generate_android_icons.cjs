const sharp = require('sharp');
const path = require('path');
const fs = require('fs');

const lightSvgPath = path.resolve(__dirname, '../../docs/icone_aplicativo_light.svg');
const darkSvgPath = path.resolve(__dirname, '../../docs/icone_aplicativo.svg');
const androidResPath = path.resolve(__dirname, '../android/app/src/main/res');

const lightSvgBuffer = fs.readFileSync(lightSvgPath);
const darkSvgBuffer = fs.readFileSync(darkSvgPath);

// Icon sizes needed for each density
// standard: 48dp
// adaptive (foreground/background): 108dp
const mipmapDensities = [
    { densityName: 'mdpi', standard: 48, adaptive: 108 },
    { densityName: 'hdpi', standard: 72, adaptive: 162 },
    { densityName: 'xhdpi', standard: 96, adaptive: 216 },
    { densityName: 'xxhdpi', standard: 144, adaptive: 324 },
    { densityName: 'xxxhdpi', standard: 192, adaptive: 432 },
];

async function generateIcon(svgBuf, outputPath, size, isAdaptiveForeground = false) {
    let process = sharp(svgBuf);

    if (isAdaptiveForeground) {
        const logoSize = Math.floor(size * 0.66);
        process = process.resize(logoSize, logoSize, {
            fit: 'contain',
            background: { r: 0, g: 0, b: 0, alpha: 0 }
        }).extend({
            top: Math.floor((size - logoSize) / 2),
            bottom: Math.ceil((size - logoSize) / 2),
            left: Math.floor((size - logoSize) / 2),
            right: Math.ceil((size - logoSize) / 2),
            background: { r: 0, g: 0, b: 0, alpha: 0 }
        });
    } else {
        process = process.resize(size, size, {
            fit: 'contain',
            background: { r: 0, g: 0, b: 0, alpha: 0 }
        });
    }

    await process.png().toFile(outputPath);
    console.log(`✓  ${path.relative(androidResPath, outputPath)}  (${size}x${size}${isAdaptiveForeground ? ' with padding' : ''})`);
}

async function generateForTheme(svgBuffer, themeFolderSuffix) {
    const tasks = [];
    for (const { densityName, standard, adaptive } of mipmapDensities) {
        const dir = path.join(androidResPath, `mipmap${themeFolderSuffix}-${densityName}`);
        if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });

        // Standard icons (older devices or fallback) -> 48dp
        tasks.push(generateIcon(svgBuffer, path.join(dir, 'ic_launcher.png'), standard));
        tasks.push(generateIcon(svgBuffer, path.join(dir, 'ic_launcher_round.png'), standard));

        // Adaptive layer (Android 8+) -> 108dp
        tasks.push(generateIcon(svgBuffer, path.join(dir, 'ic_launcher_foreground.png'), adaptive, true));

        // Generate specific size named files as requested by legacy code
        tasks.push(generateIcon(svgBuffer, path.join(dir, 'ic_launcher_48.png'), 48));
        tasks.push(generateIcon(svgBuffer, path.join(dir, 'ic_launcher_72.png'), 72));
        tasks.push(generateIcon(svgBuffer, path.join(dir, 'ic_launcher_96.png'), 96));
        tasks.push(generateIcon(svgBuffer, path.join(dir, 'ic_launcher_144.png'), 144));
        tasks.push(generateIcon(svgBuffer, path.join(dir, 'ic_launcher_192.png'), 192));
        tasks.push(generateIcon(svgBuffer, path.join(dir, 'ic_launcher_512.png'), 512));
    }
    return Promise.all(tasks);
}

// Extra legacy anydpi resources that are not directly theme-dependent
async function generateAnydpiLegacy() {
    const tasks = [];
    const anydpiDir = path.join(androidResPath, 'mipmap-anydpi-v26');
    if (!fs.existsSync(anydpiDir)) fs.mkdirSync(anydpiDir, { recursive: true });
    // Note: Do not place PNG files in anydpi folder
    return Promise.all(tasks);
}

async function main() {
    console.log('Generating Android icons from Light & Dark SVGs...\n');

    // Default folders (Light mode) Use light svg
    await generateForTheme(lightSvgBuffer, '');

    // Night folders (Dark mode) Use dark svg
    await generateForTheme(darkSvgBuffer, '-night');

    await generateAnydpiLegacy();

    console.log('\n✅ All Day and Night icons generated successfully!');
}

main().catch(err => {
    console.error('Error:', err);
    process.exit(1);
});
