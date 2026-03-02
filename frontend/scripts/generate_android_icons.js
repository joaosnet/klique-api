/* global require, __dirname, process */
const sharp = require('sharp');
const path = require('path');
const fs = require('fs');

const svgPath = path.resolve(__dirname, '../../docs/icone_aplicativo.svg');
const androidResPath = path.resolve(__dirname, '../android/app/src/main/res');

const svgBuffer = fs.readFileSync(svgPath);

// Icon sizes needed for each density
const mipmapSizes = [
    { folder: 'mipmap-mdpi', size: 48 },
    { folder: 'mipmap-hdpi', size: 72 },
    { folder: 'mipmap-xhdpi', size: 96 },
    { folder: 'mipmap-xxhdpi', size: 144 },
    { folder: 'mipmap-xxxhdpi', size: 192 },
];

// Extra sizes used in the project
const extraSizes = [
    { folder: 'mipmap-anydpi-v26', filename: 'ic_launcher_48.png', size: 48 },
    { folder: 'mipmap-anydpi-v26', filename: 'ic_launcher_72.png', size: 72 },
    { folder: 'mipmap-anydpi-v26', filename: 'ic_launcher_96.png', size: 96 },
    { folder: 'mipmap-anydpi-v26', filename: 'ic_launcher_144.png', size: 144 },
    { folder: 'mipmap-anydpi-v26', filename: 'ic_launcher_192.png', size: 192 },
    { folder: 'mipmap-anydpi-v26', filename: 'ic_launcher_512.png', size: 512 },
    { folder: 'mipmap-anydpi-v26', filename: 'ic_launcher_full.png', size: 512 },
    { folder: 'mipmap-anydpi-v26', filename: 'ic_launcher_foreground.png', size: 192 },
];

async function generateIcon(svgBuf, outputPath, size) {
    await sharp(svgBuf)
        .resize(size, size)
        .png()
        .toFile(outputPath);
    console.log(`✓ Generated: ${outputPath} (${size}x${size})`);
}

async function main() {
    console.log('Generating Android icons from SVG...\n');

    const tasks = [];

    // Generate standard mipmap icons
    for (const { folder, size } of mipmapSizes) {
        const dir = path.join(androidResPath, folder);
        if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });

        // ic_launcher.png
        tasks.push(generateIcon(svgBuffer, path.join(dir, 'ic_launcher.png'), size));
        // ic_launcher_round.png
        tasks.push(generateIcon(svgBuffer, path.join(dir, 'ic_launcher_round.png'), size));
        // ic_launcher_foreground.png
        tasks.push(generateIcon(svgBuffer, path.join(dir, 'ic_launcher_foreground.png'), size));
        // Extra sizes copied to each folder
        tasks.push(generateIcon(svgBuffer, path.join(dir, 'ic_launcher_48.png'), 48));
        tasks.push(generateIcon(svgBuffer, path.join(dir, 'ic_launcher_72.png'), 72));
        tasks.push(generateIcon(svgBuffer, path.join(dir, 'ic_launcher_96.png'), 96));
        tasks.push(generateIcon(svgBuffer, path.join(dir, 'ic_launcher_144.png'), 144));
        tasks.push(generateIcon(svgBuffer, path.join(dir, 'ic_launcher_192.png'), 192));
        tasks.push(generateIcon(svgBuffer, path.join(dir, 'ic_launcher_512.png'), 512));
    }

    // Generate extra sizes for mipmap-anydpi-v26
    const anydpiDir = path.join(androidResPath, 'mipmap-anydpi-v26');
    for (const { filename, size } of extraSizes) {
        tasks.push(generateIcon(svgBuffer, path.join(anydpiDir, filename), size));
    }
    // Also place the main ic_launcher.png in anydpi folder for legacy support
    tasks.push(generateIcon(svgBuffer, path.join(anydpiDir, 'ic_launcher_transparent.png'), 512));

    await Promise.all(tasks);
    console.log('\n✅ All icons generated successfully!');
}

main().catch(err => {
    console.error('Error:', err);
    process.exit(1);
});
