const sharp = require('sharp');
const path = require('path');
const fs = require('fs');

const svgPath = path.resolve(__dirname, '../../docs/icone_aplicativo.svg');
const androidResPath = path.resolve(__dirname, '../android/app/src/main/res');

const svgBuffer = fs.readFileSync(svgPath);

// Icon sizes needed for each density
// standard: 48dp
// adaptive (foreground/background): 108dp
const mipmapDensities = [
    { folder: 'mipmap-mdpi', standard: 48, adaptive: 108 },
    { folder: 'mipmap-hdpi', standard: 72, adaptive: 162 },
    { folder: 'mipmap-xhdpi', standard: 96, adaptive: 216 },
    { folder: 'mipmap-xxhdpi', standard: 144, adaptive: 324 },
    { folder: 'mipmap-xxxhdpi', standard: 192, adaptive: 432 },
];

// Extra sizes in mipmap-anydpi-v26
const extraFiles = [
    { filename: 'ic_launcher_48.png', size: 48 },
    { filename: 'ic_launcher_72.png', size: 72 },
    { filename: 'ic_launcher_96.png', size: 96 },
    { filename: 'ic_launcher_144.png', size: 144 },
    { filename: 'ic_launcher_192.png', size: 192 },
    // for adaptive anydpi, the foreground can be a high-res fallback
    { filename: 'ic_launcher_foreground.png', size: 432 },
    { filename: 'ic_launcher_512.png', size: 512 },
    { filename: 'ic_launcher_full.png', size: 512 },
    { filename: 'ic_launcher_transparent.png', size: 512 },
];

async function generateIcon(svgBuf, outputPath, size, isAdaptiveForeground = false) {
    // For adaptive foreground (108dp base), the safe zone is the inner 72dp.
    // This implies that the logo should be scaled down to about 66% (72/108) of the image size.
    // We achieve this by resizing the logo to 66% of the target size, and extending it with transparent padding to reach the full size.

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

async function main() {
    console.log('Generating Android icons from SVG...\n');

    const tasks = [];

    // Generate standard mipmap icons per density
    for (const { folder, standard, adaptive } of mipmapDensities) {
        const dir = path.join(androidResPath, folder);
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

    // removed the invalid PNG generation for mipmap-anydpi-v26

    await Promise.all(tasks);
    console.log('\n✅ All icons generated successfully!');
}

main().catch(err => {
    console.error('Error:', err);
    process.exit(1);
});
