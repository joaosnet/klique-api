import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

// ============ CARREGAMENTO DE OBJETIVOS ============
// Os objetivos são carregados do arquivo objetivos.json
// Para adicionar/editar objetivos, modifique o arquivo objetivos.json
let destinations = [];

async function loadObjectives() {
    try {
        const response = await fetch('./objetivos.json');
        if (response.ok) {
            destinations = await response.json();
            console.log(`✓ ${destinations.length} objetivos carregados`);
        } else {
            console.error('Erro ao carregar objetivos.json');
            destinations = getDefaultObjectives();
        }
    } catch (error) {
        console.error('Erro ao carregar objetivos:', error);
        destinations = getDefaultObjectives();
    }
}

function getDefaultObjectives() {
    return [
        {
            title: 'Reserva de Emergência: R$ 4k até dezembro',
            image: './images/reservaemergencia.png',
            position: { x: -2.5, y: 1.5 },
            tilt: -0.04
        },
        {
            title: 'Projeto Grana: Validar e faturar R$ 22k/mês',
            image: './images/Projeto Grana.png',
            position: { x: 2.5, y: 1.5 },
            tilt: 0.16
        },
        {
            title: 'Faculdade 2025.4: Aprovação nas 5 disciplinas',
            image: './images/resultadosacademicos.png',
            position: { x: -2.5, y: -1.5 },
            tilt: -0.18
        },
        {
            title: 'Projeto Coração: Convidar a Iria para um encontro',
            image: './images/iria_e_eu.png',
            position: { x: 2.5, y: -1.5 },
            tilt: 0.08
        }
    ];
}

// ============ CENA ============
const scene = new THREE.Scene();
scene.background = null;

const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 500);
const defaultCameraPosition = new THREE.Vector3(0, 1, 17);
camera.position.copy(defaultCameraPosition);

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
renderer.setClearColor(0x000000, 1);
document.body.appendChild(renderer.domElement);

// ============ PÓS-PROCESSAMENTO ============
const composer = new EffectComposer(renderer);
const renderPass = new RenderPass(scene, camera);
composer.addPass(renderPass);

const bloomPass = new UnrealBloomPass(
    new THREE.Vector2(window.innerWidth, window.innerHeight),
    0.6,   // strength
    0.5,   // radius
    0.85   // threshold
);
composer.addPass(bloomPass);

const outputPass = new OutputPass();
composer.addPass(outputPass);

// ============ CONTROLES ============
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.minPolarAngle = Math.PI / 5;
controls.maxPolarAngle = (4 * Math.PI) / 5;
controls.minDistance = 8;
controls.maxDistance = 30;
controls.enablePan = false;
controls.enableRotate = true;
const defaultControlsTarget = controls.target.clone();

// ============ ILUMINAÇÃO ============
const ambientLight = new THREE.AmbientLight(0xffffff, 0.03);
scene.add(ambientLight);

// Luz solar para o globo (dia/noite)
const sunLight = new THREE.DirectionalLight(0xffffff, 1.8);
scene.add(sunLight);

// Luz de preenchimento para os polaroids (sempre visíveis para a câmera)
const fillLight = new THREE.DirectionalLight(0xffffff, 0.9);
fillLight.position.set(0, 3, 15);
scene.add(fillLight);

// ============ GLOBO TERRESTRE ============
const EARTH_RADIUS = 5;
const textureLoader = new THREE.TextureLoader();

const earthGroup = new THREE.Group();
scene.add(earthGroup);

const tDay = textureLoader.load('https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg');
const tNight = textureLoader.load('https://unpkg.com/three-globe/example/img/earth-night.jpg');
const tWater = textureLoader.load('https://unpkg.com/three-globe/example/img/earth-water.png');
const tBump = textureLoader.load('https://unpkg.com/three-globe/example/img/earth-topology.png');

const earthGeom = new THREE.SphereGeometry(EARTH_RADIUS, 64, 64);
const earthMat = new THREE.MeshStandardMaterial({
    map: tDay,
    roughnessMap: tWater,
    bumpMap: tBump,
    bumpScale: 0.1,
    roughness: 0.8,
    metalness: 0.1
});

// Shader de mistura dia/noite
earthMat.onBeforeCompile = (shader) => {
    shader.uniforms.tNight = { value: tNight };
    shader.uniforms.sunDirection = { value: new THREE.Vector3(1, 0, 0) };

    shader.vertexShader = shader.vertexShader.replace(
        '#include <common>',
        `#include <common>
        varying vec3 vWorldNormal;`
    );
    shader.vertexShader = shader.vertexShader.replace(
        '#include <worldpos_vertex>',
        `#include <worldpos_vertex>
        vWorldNormal = normalize((modelMatrix * vec4(normal, 0.0)).xyz);`
    );
    shader.fragmentShader = shader.fragmentShader.replace(
        '#include <common>',
        `#include <common>
        uniform sampler2D tNight;
        uniform vec3 sunDirection;
        varying vec3 vWorldNormal;`
    );
    shader.fragmentShader = shader.fragmentShader.replace(
        '#include <emissivemap_fragment>',
        `#include <emissivemap_fragment>
        vec3 nightColor = texture2D(tNight, vMapUv).rgb;
        float sunDot = dot(vWorldNormal, normalize(sunDirection));
        float blend = smoothstep(-0.2, 0.2, sunDot);
        vec3 finalNightLights = nightColor * (1.0 - blend) * 1.5;
        totalEmissiveRadiance += finalNightLights;`
    );
    earthMat.userData.shader = shader;
};

const earthMesh = new THREE.Mesh(earthGeom, earthMat);
earthGroup.add(earthMesh);

// Atmosfera
const atmosGeom = new THREE.SphereGeometry(EARTH_RADIUS * 1.05, 64, 64);
const atmosMat = new THREE.ShaderMaterial({
    vertexShader: `
        varying vec3 vNormal;
        void main() {
            vNormal = normalize(normalMatrix * normal);
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
    `,
    fragmentShader: `
        varying vec3 vNormal;
        void main() {
            float intensity = pow(0.65 - dot(vNormal, vec3(0, 0, 1.0)), 4.0);
            gl_FragColor = vec4(0.3, 0.6, 1.0, 1.0) * intensity;
        }
    `,
    blending: THREE.AdditiveBlending,
    side: THREE.BackSide,
    transparent: true,
    depthWrite: false
});
const atmosMesh = new THREE.Mesh(atmosGeom, atmosMat);
earthGroup.add(atmosMesh);

// Estrelas
const starsGeom = new THREE.BufferGeometry();
const starsCount = 3000;
const starPositions = new Float32Array(starsCount * 3);
for (let i = 0; i < starsCount * 3; i++) {
    starPositions[i] = (Math.random() - 0.5) * 400;
}
starsGeom.setAttribute('position', new THREE.BufferAttribute(starPositions, 3));
const starsMat = new THREE.PointsMaterial({
    size: 0.5,
    color: 0xffffff,
    transparent: true,
    opacity: 0.8,
    sizeAttenuation: true
});
const starMesh = new THREE.Points(starsGeom, starsMat);
scene.add(starMesh);

// ============ EFEMÉRIDES DO SOL ============
function latLonToVector3(lat, lon, radius) {
    const phi = (90 - lat) * (Math.PI / 180);
    const theta = (lon + 180) * (Math.PI / 180);
    const x = -(radius * Math.sin(phi) * Math.cos(theta));
    const z = (radius * Math.sin(phi) * Math.sin(theta));
    const y = (radius * Math.cos(phi));
    return new THREE.Vector3(x, y, z);
}

function updateSunPosition() {
    const date = new Date();
    const jd = (date.getTime() / 86400000) + 2440587.5;
    const d = jd - 2451545.0;

    const g = (357.529 + 0.98560028 * d) % 360;
    const gRad = g * Math.PI / 180;
    const q = (280.459 + 0.98564736 * d) % 360;
    const L = q + 1.915 * Math.sin(gRad) + 0.020 * Math.sin(2 * gRad);
    const LRad = L * Math.PI / 180;

    const e = 23.439 - 0.00000036 * d;
    const eRad = e * Math.PI / 180;

    const declination = Math.asin(Math.sin(eRad) * Math.sin(LRad)) * 180 / Math.PI;
    let ra = Math.atan2(Math.cos(eRad) * Math.sin(LRad), Math.cos(LRad)) * 180 / Math.PI;
    if (ra < 0) ra += 360;

    let gmst = (18.697374558 + 24.06570982441908 * d) % 24;
    let gha = (gmst * 15 - ra) % 360;
    if (gha < 0) gha += 360;
    let longitude = -gha;
    if (longitude < -180) longitude += 360;

    const sunVec = latLonToVector3(declination, longitude, 100);
    sunLight.position.copy(sunVec);
    if (earthMat.userData.shader) {
        earthMat.userData.shader.uniforms.sunDirection.value.copy(sunVec).normalize();
    }
}

updateSunPosition();
setInterval(updateSunPosition, 60000);

// ============ POLAROIDS ============
const POLAROID_Z = 7;

const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();
const polaroidGroups = [];
const initialStates = new Map();

function getPolaroidHitPlane(group) {
    return group.children.find(child => child.isMesh && child.material && child.material.visible === false);
}

function getPolaroidHitTargets() {
    return polaroidGroups.map(getPolaroidHitPlane).filter(Boolean);
}

function detectTransformHandle(localPoint) {
    const halfW = w / 2;
    const halfH = h / 2;
    const absX = Math.abs(localPoint.x);
    const absY = Math.abs(localPoint.y);

    if (absX > halfW || absY > halfH) return null;

    const distanceToVerticalEdge = halfW - absX;
    const distanceToHorizontalEdge = halfH - absY;
    const nearVertical = distanceToVerticalEdge <= edgeHandleThreshold;
    const nearHorizontal = distanceToHorizontalEdge <= edgeHandleThreshold;
    const nearCorner = nearVertical && nearHorizontal &&
        distanceToVerticalEdge <= cornerHandleThreshold &&
        distanceToHorizontalEdge <= cornerHandleThreshold;

    if (nearCorner) return { mode: 'rotate', cursor: 'grab', cursorActive: 'grabbing' };
    if (nearVertical) return { mode: 'scale', axis: 'x', cursor: 'ew-resize', cursorActive: 'ew-resize' };
    if (nearHorizontal) return { mode: 'scale', axis: 'y', cursor: 'ns-resize', cursorActive: 'ns-resize' };

    return null;
}

function updateHoverScaleVisual(group) {
    if (!group) return;
    const state = initialStates.get(group);
    if (!state || !state.scale) return;
    const base = state.scale.x;
    group.scale.setScalar(base * 1.15);
}

function drawPolaroidLabel(text, ctx, textCanvas) {
    ctx.fillStyle = 'rgba(0,0,0,0)';
    ctx.clearRect(0, 0, textCanvas.width, textCanvas.height);
    ctx.fillStyle = '#3a352f';
    ctx.textAlign = 'center';
    ctx.font = '32px "Caveat", cursive, "Arial"';
    const words = text.split(' ');
    const lines = [];
    let currentLine = '';
    const maxWidth = 480;
    words.forEach((word) => {
        const candidate = currentLine ? `${currentLine} ${word}` : word;
        if (ctx.measureText(candidate).width > maxWidth && currentLine) {
            lines.push(currentLine);
            currentLine = word;
        } else {
            currentLine = candidate;
        }
    });
    if (currentLine) lines.push(currentLine);
    const lineHeight = 40;
    let y = (textCanvas.height / 2) - ((lines.length - 1) * lineHeight / 2);
    lines.forEach((line) => {
        ctx.fillText(line, textCanvas.width / 2, y);
        y += lineHeight;
    });
}

import { polaroidTemplates } from './polaroidTemplates.js';

async function getBase64Image(url) {
    try {
        const response = await fetch(url);
        const blob = await response.blob();
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => {
                if (reader.result) resolve(reader.result);
                else reject(new Error('Failed base64 conversion'));
            };
            reader.onerror = reject;
            reader.readAsDataURL(blob);
        });
    } catch (e) {
        console.error('Error loading image', url, e);
        // Fallback transparent 1x1 base64
        return 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=';
    }
}

window.addEventListener('storage', (e) => {
    if (e.key === 'selectedPolaroidModel') {
        location.reload();
    }
});

const polaroidFrameMaterial = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.58, metalness: 0.04 });
const h = 1.9;
const w = h * (250 / 300); // Base logical hit size matching SVG aspect ratio (1.583)
const polaroidFrameGeometry = new THREE.PlaneGeometry(w, h);

async function initializePolaroids() {
    let savedCameraState = null;

    await document.fonts.ready;

    let selectedModelIndex = 0;
    const storedModel = localStorage.getItem('selectedPolaroidModel');
    if (storedModel !== null) {
        selectedModelIndex = parseInt(storedModel, 10);
        if (isNaN(selectedModelIndex) || selectedModelIndex < 0 || selectedModelIndex >= polaroidTemplates.length) {
            selectedModelIndex = 0;
        }
    }
    const template = polaroidTemplates[selectedModelIndex];

    for (let index = 0; index < destinations.length; index++) {
        const destination = destinations[index];
        const group = new THREE.Group();
        const base64Img = await getBase64Image(destination.image);

        // Pass base64 properly to render it directly into the SVG structure (required for filters and correct layout)
        // We pass true for `is3D` to disable SVG <animate> tags that clash with static HTML5 Canvas rendering.
        let svgString = template.render(base64Img, destination.title, true);
        // Ensure text renders somewhat nicely if Caveat fails to load in the SVG context
        svgString = svgString.replace(/font-family="[^"]*"/g, 'font-family="Caveat, Comic Sans MS, cursive, sans-serif"');

        const svgBlob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
        const svgUrl = URL.createObjectURL(svgBlob);

        const texture = await new Promise((resolve) => {
            textureLoader.load(svgUrl, (tex) => {
                tex.colorSpace = THREE.SRGBColorSpace;
                tex.generateMipmaps = true;
                tex.minFilter = THREE.LinearMipmapLinearFilter;
                resolve(tex);
            });
        });

        const aspect = 250 / 300;
        const planeHeight = 1.9;
        const planeWidth = planeHeight * aspect;
        const material = new THREE.MeshStandardMaterial({
            map: texture,
            transparent: true,
            alphaTest: 0.01,
            roughness: 0.6,
            metalness: 0.04,
            side: THREE.DoubleSide
        });

        const polaroidMesh = new THREE.Mesh(new THREE.PlaneGeometry(planeWidth, planeHeight), material);
        polaroidMesh.castShadow = true;
        group.add(polaroidMesh);

        const hitPlane = new THREE.Mesh(
            new THREE.PlaneGeometry(planeWidth, planeHeight),
            new THREE.MeshBasicMaterial({ visible: false })
        );
        hitPlane.position.z = 0.02;
        group.add(hitPlane);

        const isOnSphere = destination.z !== 7.0 && destination.z !== undefined;
        let startPos;
        if (isOnSphere) {
            startPos = new THREE.Vector3(destination.x || destination.position.x, destination.y || destination.position.y, destination.z);
        } else {
            startPos = new THREE.Vector3(destination.position.x, destination.position.y + 0.5, EARTH_RADIUS);
        }

        const baseScale = typeof destination.scale === 'number' ? destination.scale : 0.85;
        const baseRotation = typeof destination.rotation === 'number' ? destination.rotation : destination.tilt;

        const clampedScale = THREE.MathUtils.clamp(baseScale, polaroidScaleRange.min, polaroidScaleRange.max);
        group.scale.setScalar(clampedScale);

        if (!isOnSphere) {
            const radius = EARTH_RADIUS + 0.05;
            startPos.normalize().multiplyScalar(radius);
        }
        group.position.copy(startPos);

        const normal = startPos.clone().normalize();
        let tiltX = (destination.tiltX !== undefined) ? destination.tiltX : (-0.07 + Math.random() * 0.06);

        const quat = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 0, 1), normal);
        group.quaternion.copy(quat);

        const clampedRotation = THREE.MathUtils.clamp(baseRotation, polaroidRotationRange.min, polaroidRotationRange.max);
        group.rotateZ(clampedRotation);
        group.rotateX(tiltX);

        initialStates.set(group, {
            position: group.position.clone(),
            quaternion: group.quaternion.clone(),
            baseNormal: normal,
            tiltX: tiltX,
            scale: group.scale.clone(),
            rotation: clampedRotation
        });

        earthGroup.add(group);
        polaroidGroups.push(group);
        group.userData = {
            index,
            destination,
            photoMesh: polaroidMesh, // flash effect falls back to the entire polaroid
            flashOffset: index * 1.7,
            transform: {
                scale: clampedScale,
                rotation: group.rotation.z
            },
            photoBox: template.photoBox
        };
    }

    if (savedCameraState) {
        applyCameraState(savedCameraState);
    }
}

let hovered = null;
let dragged = null;
let hasMoved = false;
const dragPoint = new THREE.Vector3();
const dragOffset = new THREE.Vector3();
const keyboardZoomStep = 0.8;
const cameraPanStep = 0.6;
const cameraPanLimits = {
    x: { min: -6, max: 6 },
    y: { min: -2, max: 5 }
};
const polaroidScaleStep = 0.05;
const polaroidRotationStep = THREE.MathUtils.degToRad(3);
const polaroidScaleRange = { min: 0.3, max: 2.0 };
const polaroidRotationRange = {
    min: THREE.MathUtils.degToRad(-35),
    max: THREE.MathUtils.degToRad(35)
};
const edgeHandleThreshold = 0.12;
const cornerHandleThreshold = 0.2;

let transformMode = null;
let transformTarget = null;
let transformState = null;

function getActivePolaroid() {
    if (transformTarget) return transformTarget;
    if (dragged) return dragged;
    if (hovered) return hovered;
    return null;
}

function setPolaroidScale(group, targetScale, { applyHoverScale = true } = {}) {
    if (!group) return;
    const clampedScale = THREE.MathUtils.clamp(targetScale, polaroidScaleRange.min, polaroidScaleRange.max);
    const state = initialStates.get(group);
    if (state && state.scale) state.scale.setScalar(clampedScale);
    const shouldApplyHover = applyHoverScale && !transformMode && group === hovered;
    if (shouldApplyHover) {
        group.scale.setScalar(clampedScale * 1.15);
    } else {
        group.scale.setScalar(clampedScale);
    }
    if (group.userData && group.userData.transform) {
        group.userData.transform.scale = clampedScale;
    }
}

function adjustActivePolaroidScale(delta) {
    const group = getActivePolaroid();
    if (!group) return;
    const state = initialStates.get(group);
    const baseScale = state && state.scale ? state.scale.x : group.scale.x;
    setPolaroidScale(group, baseScale + delta);
}

function setPolaroidRotation(group, targetRotation) {
    if (!group) return;
    const clampedRotation = THREE.MathUtils.clamp(targetRotation, polaroidRotationRange.min, polaroidRotationRange.max);

    const state = initialStates.get(group);
    if (state && state.baseNormal) {
        const baseQuat = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 0, 1), state.baseNormal);
        group.quaternion.copy(baseQuat);
        group.rotateZ(clampedRotation);
        group.rotateX(state.tiltX);
        state.quaternion = group.quaternion.clone();
        state.rotation = clampedRotation;
    } else {
        group.rotation.z = clampedRotation;
        if (state) state.rotation = clampedRotation;
    }

    if (group.userData && group.userData.transform) {
        group.userData.transform.rotation = clampedRotation;
    }
}

function adjustActivePolaroidRotation(delta) {
    const group = getActivePolaroid();
    if (!group) return;
    const state = initialStates.get(group);
    const baseRotation = state && typeof state.rotation === 'number' ? state.rotation : group.rotation.z;
    setPolaroidRotation(group, baseRotation + delta);
}

// Inicializar após carregar objetivos
loadObjectives().then(() => {
    initializePolaroids();
});

function adjustCameraZoom(delta) {
    const offset = new THREE.Vector3().subVectors(camera.position, controls.target);
    const currentDistance = offset.length();
    const newDistance = THREE.MathUtils.clamp(currentDistance + delta, controls.minDistance, controls.maxDistance);
    offset.setLength(newDistance);
    camera.position.copy(controls.target).add(offset);
    controls.update();
}

function translateCamera(deltaX, deltaY) {
    const clampedTargetX = THREE.MathUtils.clamp(controls.target.x + deltaX, cameraPanLimits.x.min, cameraPanLimits.x.max);
    const clampedTargetY = THREE.MathUtils.clamp(controls.target.y + deltaY, cameraPanLimits.y.min, cameraPanLimits.y.max);

    const moveX = clampedTargetX - controls.target.x;
    const moveY = clampedTargetY - controls.target.y;

    if (moveX === 0 && moveY === 0) {
        controls.update();
        return;
    }

    controls.target.x = clampedTargetX;
    controls.target.y = clampedTargetY;
    camera.position.x += moveX;
    camera.position.y += moveY;
    controls.update();
}

function applyCameraState(state) {
    if (!state) return;

    if (state.target) {
        controls.target.set(
            state.target.x ?? controls.target.x,
            state.target.y ?? controls.target.y,
            state.target.z ?? controls.target.z
        );
    }

    if (state.position) {
        camera.position.set(
            state.position.x ?? camera.position.x,
            state.position.y ?? camera.position.y,
            state.position.z ?? camera.position.z
        );
    }

    const clampedTargetX = THREE.MathUtils.clamp(controls.target.x, cameraPanLimits.x.min, cameraPanLimits.x.max);
    const clampedTargetY = THREE.MathUtils.clamp(controls.target.y, cameraPanLimits.y.min, cameraPanLimits.y.max);
    const deltaX = clampedTargetX - controls.target.x;
    const deltaY = clampedTargetY - controls.target.y;
    controls.target.x = clampedTargetX;
    controls.target.y = clampedTargetY;
    camera.position.x += deltaX;
    camera.position.y += deltaY;

    if (!state.position && typeof state.distance === 'number') {
        const currentDistance = camera.position.distanceTo(controls.target);
        adjustCameraZoom(state.distance - currentDistance);
        return;
    }

    const offset = new THREE.Vector3().subVectors(camera.position, controls.target);
    const distance = offset.length();
    const clampedDistance = THREE.MathUtils.clamp(distance, controls.minDistance, controls.maxDistance);
    if (!Number.isFinite(clampedDistance)) {
        controls.update();
        return;
    }
    if (Math.abs(clampedDistance - distance) > 1e-5) {
        offset.setLength(clampedDistance);
        camera.position.copy(controls.target).add(offset);
    }

    controls.update();
}

function resetCameraPosition() {
    camera.position.copy(defaultCameraPosition);
    controls.target.copy(defaultControlsTarget);
    controls.update();
}

// ============ LOOP DE ANIMAÇÃO ============
function animate() {
    requestAnimationFrame(animate);
    const time = performance.now() * 0.0006;

    // Rotação lenta do globo
    earthGroup.rotation.y += 0.00015;

    // Rotação muito lenta das estrelas
    starMesh.rotation.y -= 0.00003;

    polaroidGroups.forEach((group, idx) => {
        const state = initialStates.get(group);
        if (!state) return;

        const isActive = group === hovered || group === dragged || group === transformTarget;
        const isDragging = group === dragged || group === transformTarget;

        if (!isActive) {
            group.scale.lerp(state.scale, 0.12);
        }

        // Pêndulo com pivô no alfinete
        if (!isDragging) {
            const baseRot = group.userData.transform ? group.userData.transform.rotation : (state.rotation || 0);
            const swingDelta = Math.sin(3.0 * time + idx * 1.1) * (5 * Math.PI / 180);
            const angle = baseRot + swingDelta;
            const pinOffset = h / 2 - 0.1; // distância do centro do grupo ao alfinete

            // Restaura orientação base na esfera
            if (state.quaternion) {
                group.quaternion.copy(state.quaternion);
            }

            // Aplica o swingDelta no Z local
            group.rotateZ(swingDelta);

            // Mantém o alfinete fixo calcullando o offset no espaço local da foto
            const floatY = isActive ? 0 : Math.sin(time * 1.6 + idx) * 0.04;
            const dx = pinOffset * (Math.sin(angle) - Math.sin(baseRot));
            const dy = pinOffset * (Math.cos(baseRot) - Math.cos(angle)) + floatY;

            const xAxis = new THREE.Vector3(1, 0, 0).applyQuaternion(state.quaternion);
            const yAxis = new THREE.Vector3(0, 1, 0).applyQuaternion(state.quaternion);

            group.position.copy(state.position)
                .add(xAxis.multiplyScalar(dx))
                .add(yAxis.multiplyScalar(dy));
        }

        // Flash de câmera (ciclo de 4s, estouro branco no início)
        const photo = group.userData.photoMesh;
        if (photo && photo.material) {
            const flashPeriod = 2.4;
            const flashDuration = 0.36;
            const phase = (time + (group.userData.flashOffset || 0)) % flashPeriod;
            photo.material.emissiveIntensity = phase < flashDuration
                ? (1 - phase / flashDuration) * 2.0
                : 0.08;
        }
    });

    controls.update();
    composer.render();
}

animate();

// ============ INTERAÇÃO COM MOUSE ============
function onPointerDown(event) {
    hasMoved = false;
    pointer.x = (event.clientX / window.innerWidth) * 2 - 1;
    pointer.y = (event.clientY / window.innerHeight) * -2 + 1;
    raycaster.setFromCamera(pointer, camera);

    const intersects = raycaster.intersectObjects(getPolaroidHitTargets(), false);

    if (intersects.length > 0) {
        const intersection = intersects[0];
        const group = intersection.object.parent;
        if (group) {
            const localPoint = group.worldToLocal(intersection.point.clone());
            const handleInfo = detectTransformHandle(localPoint);

            if (handleInfo) {
                transformMode = handleInfo.mode;
                transformTarget = group;
                const state = initialStates.get(group);
                transformState = {
                    cursorHover: handleInfo.cursor,
                    cursorActive: handleInfo.cursorActive || handleInfo.cursor
                };
                hasMoved = true;

                if (transformMode === 'scale') {
                    const initialScale = state && state.scale ? state.scale.x : group.scale.x;
                    transformState.initialScale = initialScale;
                    transformState.startRadius = Math.max(0.05, Math.hypot(localPoint.x, localPoint.y));
                } else if (transformMode === 'rotate') {
                    const initialRotation = state && typeof state.rotation === 'number' ? state.rotation : group.rotation.z;
                    transformState.initialRotation = initialRotation;
                    transformState.startAngle = Math.atan2(localPoint.y, localPoint.x);
                }

                if (state && state.scale) group.scale.copy(state.scale);

                controls.enabled = false;
                document.body.style.cursor = transformState.cursorActive;
                return;
            }

            dragged = group;
            hasMoved = false;
            const earthIntersects = raycaster.intersectObject(earthMesh);
            if (earthIntersects.length > 0) {
                const localHit = earthGroup.worldToLocal(earthIntersects[0].point.clone());
                dragPoint.copy(localHit);
                dragOffset.copy(dragPoint).sub(dragged.position);
            }
            controls.enabled = false;
            document.body.style.cursor = 'grabbing';
            return;
        }
    }
}

function onPointerMove(event) {
    pointer.x = (event.clientX / window.innerWidth) * 2 - 1;
    pointer.y = (event.clientY / window.innerHeight) * -2 + 1;
    raycaster.setFromCamera(pointer, camera);

    if (transformMode && transformTarget && transformState) {
        hasMoved = true;
        const hitPlane = getPolaroidHitPlane(transformTarget);
        if (hitPlane) {
            const intersections = raycaster.intersectObject(hitPlane, false);
            if (intersections.length > 0) {
                const localPoint = transformTarget.worldToLocal(intersections[0].point.clone());
                if (transformMode === 'scale' && transformState.startRadius) {
                    const currentRadius = Math.max(0.05, Math.hypot(localPoint.x, localPoint.y));
                    const ratio = currentRadius / transformState.startRadius;
                    const newScale = transformState.initialScale * ratio;
                    setPolaroidScale(transformTarget, newScale, { applyHoverScale: false });
                } else if (transformMode === 'rotate' && typeof transformState.startAngle === 'number') {
                    const currentAngle = Math.atan2(localPoint.y, localPoint.x);
                    let deltaAngle = currentAngle - transformState.startAngle;
                    deltaAngle = THREE.MathUtils.euclideanModulo(deltaAngle + Math.PI, Math.PI * 2) - Math.PI;
                    setPolaroidRotation(transformTarget, transformState.initialRotation + deltaAngle);
                }
            }
        }
        document.body.style.cursor = transformState.cursorActive || 'grabbing';
        return;
    }

    if (dragged) {
        hasMoved = true;
        const earthIntersects = raycaster.intersectObject(earthMesh);
        if (earthIntersects.length > 0) {
            const localHit = earthGroup.worldToLocal(earthIntersects[0].point.clone());

            const targetPos = localHit.sub(dragOffset);

            const radius = EARTH_RADIUS + 0.05;
            targetPos.normalize().multiplyScalar(radius);
            dragged.position.copy(targetPos);

            const state = initialStates.get(dragged);
            const normal = targetPos.clone().normalize();
            if (state) state.baseNormal = normal;

            const baseQuat = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 0, 1), normal);
            dragged.quaternion.copy(baseQuat);

            const rotZ = state ? state.rotation : dragged.userData.transform.rotation;
            const tiltX = state ? state.tiltX : -0.07;
            dragged.rotateZ(rotZ);
            dragged.rotateX(tiltX);

            if (state) state.quaternion = dragged.quaternion.clone();
            if (state) state.position.copy(dragged.position);
        }
        return;
    }

    const intersects = raycaster.intersectObjects(getPolaroidHitTargets(), false);
    if (intersects.length > 0) {
        const intersection = intersects[0];
        const group = intersection.object.parent;
        if (group && hovered !== group) {
            if (hovered) {
                const beforeState = initialStates.get(hovered);
                if (beforeState && beforeState.scale) hovered.scale.copy(beforeState.scale);
            }
            hovered = group;
            updateHoverScaleVisual(group);
        } else if (hovered === group && !transformMode) {
            updateHoverScaleVisual(group);
        }
        const localPoint = group.worldToLocal(intersection.point.clone());
        const handleInfo = detectTransformHandle(localPoint);
        document.body.style.cursor = handleInfo ? handleInfo.cursor : 'pointer';
        return;
    } else if (hovered) {
        const state = initialStates.get(hovered);
        if (state && state.scale) hovered.scale.copy(state.scale);
        hovered = null;
        document.body.style.cursor = 'default';
        return;
    }

    document.body.style.cursor = 'default';
}

function onPointerUp() {
    if (dragged) {
        const state = initialStates.get(dragged);
        if (state) state.position.copy(dragged.position);
        dragged = null;
    }

    if (transformMode && transformTarget && transformState) {
        const state = initialStates.get(transformTarget);
        if (state && state.scale) {
            if (hovered === transformTarget) {
                updateHoverScaleVisual(transformTarget);
            } else {
                transformTarget.scale.copy(state.scale);
            }
        }
        transformMode = null;
        transformTarget = null;
        transformState = null;
    }

    controls.enabled = true;
    document.body.style.cursor = hovered ? 'pointer' : 'default';
}

function onClick(event) {
    if (hasMoved) {
        hasMoved = false;
        return;
    }
    pointer.x = (event.clientX / window.innerWidth) * 2 - 1;
    pointer.y = (event.clientY / window.innerHeight) * -2 + 1;
    raycaster.setFromCamera(pointer, camera);

    const polaroidIntersects = raycaster.intersectObjects(getPolaroidHitTargets(), false);
    if (polaroidIntersects.length > 0) {
        const group = polaroidIntersects[0].object.parent;
        if (group) {
            openModal(group.userData.destination);
            return;
        }
    }
}

function onResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
    composer.setSize(window.innerWidth, window.innerHeight);
    bloomPass.resolution.set(window.innerWidth, window.innerHeight);
}

// ============ MODAL ============
function openModal(destination) {
    const existingModal = document.querySelector('.image-modal');
    if (existingModal) existingModal.remove();

    const modal = document.createElement('div');
    modal.className = 'image-modal active';

    const modalContent = document.createElement('div');
    modalContent.className = 'modal-content';

    const img = document.createElement('img');
    img.src = destination.image;
    img.alt = destination.title;
    img.className = 'modal-image';

    const closeBtn = document.createElement('button');
    closeBtn.className = 'modal-close';
    closeBtn.innerHTML = '&times;';
    closeBtn.setAttribute('aria-label', 'Fechar');

    closeBtn.addEventListener('click', () => closeModal(modal));
    modal.addEventListener('click', (event) => {
        if (event.target === modal) closeModal(modal);
    });

    modalContent.appendChild(img);
    modalContent.appendChild(closeBtn);
    modal.appendChild(modalContent);
    document.body.appendChild(modal);

    const handleEscape = (event) => {
        if (event.key === 'Escape') {
            closeModal(modal);
            document.removeEventListener('keydown', handleEscape);
        }
    };
    document.addEventListener('keydown', handleEscape);
}

function closeModal(modal) {
    modal.classList.remove('active');
    setTimeout(() => {
        if (modal && modal.parentNode) modal.parentNode.removeChild(modal);
    }, 300);
}

// ============ EXPORTAR POSIÇÕES (V) ============
function generatePositionsFile() {
    const newObjectives = polaroidGroups.map(group => {
        const state = initialStates.get(group);
        const baseScale = state && state.scale ? state.scale.x : group.scale.x;
        const baseRotation = state && typeof state.rotation === 'number' ? state.rotation : group.rotation.z;
        const tiltX = state ? state.tiltX : -0.07;

        return {
            title: group.userData.destination.title,
            image: group.userData.destination.image,
            position: { x: group.position.x, y: group.position.y }, // Backend compatibility
            x: group.position.x,
            y: group.position.y,
            z: group.position.z,
            tilt: baseRotation, // Backend compatibility
            tiltX: tiltX,
            scale: baseScale,
            rotation: baseRotation
        };
    });

    const jsonString = JSON.stringify(newObjectives, null, 2);
    console.log("--- COPIE E COLE O CONTEÚDO ABAIXO EM 'objetivos.json' ---");
    console.log(jsonString);
    console.log("---------------------------------------------------------");
    alert('Conteúdo do objetivos.json gerado no console (pressione F12). Substitua o original.');
}

// ============ ATALHOS DE TECLADO ============
window.addEventListener('keydown', (event) => {
    const key = event.key;
    const lowerKey = key ? key.toLowerCase() : '';

    if (lowerKey === 'v') { event.preventDefault(); generatePositionsFile(); return; }

    if (key === '+' || key === '=' || key === 'Add') { event.preventDefault(); adjustCameraZoom(-keyboardZoomStep); return; }
    if (key === '-' || key === '_' || key === 'Subtract') { event.preventDefault(); adjustCameraZoom(keyboardZoomStep); return; }

    if (key === '[' || key === '{') { event.preventDefault(); adjustActivePolaroidScale(-polaroidScaleStep); return; }
    if (key === ']' || key === '}') { event.preventDefault(); adjustActivePolaroidScale(polaroidScaleStep); return; }

    if (key === ',' || key === '<') { event.preventDefault(); adjustActivePolaroidRotation(-polaroidRotationStep); return; }
    if (key === '.' || key === '>') { event.preventDefault(); adjustActivePolaroidRotation(polaroidRotationStep); return; }

    if (key === 'ArrowUp' || lowerKey === 'w') { event.preventDefault(); translateCamera(0, cameraPanStep); return; }
    if (key === 'ArrowDown' || lowerKey === 's') { event.preventDefault(); translateCamera(0, -cameraPanStep); return; }
    if (key === 'ArrowLeft' || lowerKey === 'a') { event.preventDefault(); translateCamera(-cameraPanStep, 0); return; }
    if (key === 'ArrowRight' || lowerKey === 'd') { event.preventDefault(); translateCamera(cameraPanStep, 0); return; }

    if (key === '0' || lowerKey === 'r') { event.preventDefault(); resetCameraPosition(); return; }

    if (lowerKey === 'e') { event.preventDefault(); renderer.toneMappingExposure = Math.min(renderer.toneMappingExposure + 0.1, 3.0); return; }
    if (lowerKey === 't') { event.preventDefault(); renderer.toneMappingExposure = Math.max(renderer.toneMappingExposure - 0.1, 0.2); return; }
});

window.addEventListener('pointerdown', onPointerDown);
window.addEventListener('pointermove', onPointerMove);
window.addEventListener('pointerup', onPointerUp);
window.addEventListener('click', onClick);
window.addEventListener('resize', onResize);
