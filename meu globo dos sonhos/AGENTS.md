# Mural dos Sonhos - Copilot Instructions

## Project Overview
Interactive 3D vision board using Three.js to display goals as draggable Polaroid photos on a cork board. Features a Leaflet map background layer and modal image viewing.

**Deployment Target:** This project is designed to run as a **Lively Wallpaper** (interactive desktop wallpaper). The HTML file serves as the wallpaper entry point with embedded Three.js scene and Leaflet map rendering directly on the desktop background.

## Architecture & Data Flow

**Core Components:**
- `main.js` - Three.js scene setup, Polaroid rendering, drag-and-drop interaction, modal system
- `map.js` - Leaflet background map with vignette overlay (decorative, non-interactive)
- `mapa_dos_sonhos.html` - Entry point with ES module imports via importmap
- `objetivos.json` - Persistent storage for goal metadata (title, image path) AND 3D spatial positioning (x, y, z, rotation, scale)
- `destinations[]` array in `main.js` - Fallback source of truth for goal cards if `objetivos.json` fails to load

**Key Dependencies:**
- Three.js v0.160.0 (via CDN importmap) with OrbitControls addon
- Leaflet.js (local `libs/` folder) for background map rendering

## Critical Patterns

### Polaroid State Management
Each Polaroid has THREE position states:
1. **Default position** - Defined in `destinations[]` array (`position: { x, y }`)
2. **Saved position** - Loaded from `objetivos.json` on startup (takes precedence, overrides default if 3D coords exist)
3. **Runtime state** - Stored in `initialStates` Map for animation reference

Press 'V' key to export current positions and object metadata to console for copying back to `objetivos.json`.

### Interaction System
Uses Three.js Raycaster with invisible hit planes (`visible: false` material):
- `onPointerMove` - Hover detection and scale animation (1.15x on hover)
- `onPointerDown/Up` - Drag-and-drop with plane projection (`dragPlane` at z=0.24)
- `onClick` - Modal trigger (prevented during drag with `dragged` flag check)

**Important:** OrbitControls disabled (`controls.enabled = false`) during drag operations.

### Dynamic Text Rendering
Polaroid labels use Canvas2D text rendering converted to Three.js CanvasTexture:
- `drawPolaroidLabel()` handles text wrapping at 480px width
- Font: 'italic 34px Inter' with multi-line support
- Regenerate texture when updating goal titles

### Lighting Setup
Three-point lighting for realistic cork board appearance:
- `ceilingLight` (SpotLight) - Main light with shadows from (-3, 9, 6)
- `fillLight` (DirectionalLight) - Fill from (3.5, 4, 8) at 40% intensity
- `ambientLight` - Warm base (#ffe0bd) at 35%

Shadow maps enabled: PCFSoftShadowMap at 2048x2048 resolution.

## Development Workflows

### Adding New Goals
1. Add entry to `destinations[]` array with image path, title, position, tilt
2. Place image in `images/` folder
3. Restart - Polaroid auto-generates on load

### Adjusting Visual Properties
- **Cork board dimensions:** `boardFrame` BoxGeometry (20 x 12 x 0.7)
- **Polaroid size:** Variables `w=1.4, h=1.7` (frame), `photoW=1.2, photoH=1.2` (photo)
- **Animation amplitude:** `Math.sin() * 0.04` in animate loop
- **Camera bounds:** `minDistance: 8`, `maxDistance: 18`, limited polar angles

### Testing Drag Behavior
Drag system requires precise z-plane alignment:
- All Polaroids on `dragPlane` at z=0.24
- Hit planes offset at z=0.02 to avoid z-fighting
- Drag offset calculated from initial grab point

## Key Files to Modify

- **`main.js:destinations[]`** - Add/remove/reorder goals (lines 6-27)
- **`objetivos.json`** - Restore saved layout and edit titles (auto-generated via 'V' key)
- **`style.css:.image-modal`** - Customize modal appearance
- **`main.js:drawPolaroidLabel()`** - Change label styling (font, color, wrapping)

## Common Tasks

**Change board texture:** Uncomment wall/map texture loading in `main.js` (lines 62-95)
**Adjust Polaroid materials:** Modify `polaroidFrameMaterial` color (line 117, currently #f6f1e6)
**Disable background map:** Remove Leaflet script tags and `#map-container` div
**Lock Polaroid positions:** Remove pointer event listeners (lines 382-386)

## Gotchas

- Modal must check `dragged` flag before opening (line 297) to prevent click-after-drag
- `initialStates` Map must be updated after drag (line 283) or animation breaks
- Canvas texture requires `THREE.SRGBColorSpace` for color accuracy
- Don't animate Polaroids during drag (`group !== dragged` check in animate loop)
