/**
 * Klique Natal - Christmas Avatar App
 * JavaScript para interatividade e integração com API
 */

// ========================================
// Constants & State
// ========================================

const API_BASE_URL = window.location.origin;

let TEMPLATES = {};

const state = {
    uploadedImage: null,
    processedImage: null,
    selectedTemplate: null,
    currentCategory: 'todos',
    carouselPosition: 0,
    isProcessing: false,
    history: [],
    historyIndex: -1,
    // Camera state
    cameraStream: null,
    facingMode: 'user' // 'user' = front camera, 'environment' = back camera
};

// ========================================
// DOM Elements
// ========================================

const elements = {
    // Camera
    cameraZone: document.getElementById('cameraZone'),
    cameraVideo: document.getElementById('cameraVideo'),
    captureBtn: document.getElementById('captureBtn'),
    switchCameraBtn: document.getElementById('switchCameraBtn'),
    galleryBtn: document.getElementById('galleryBtn'),
    galleryInput: document.getElementById('galleryInput'),

    // Upload
    uploadZone: document.getElementById('uploadZone'),
    imageInput: document.getElementById('imageInput'),

    // Comparator
    imageComparator: document.getElementById('imageComparator'),
    beforeImage: document.getElementById('beforeImage'),
    afterImage: document.getElementById('afterImage'),
    comparatorOverlay: document.getElementById('comparatorOverlay'),
    comparatorSlider: document.getElementById('comparatorSlider'),

    // Loading
    loadingState: document.getElementById('loadingState'),

    // Actions
    actionButtons: document.getElementById('actionButtons'),
    replaceBtn: document.getElementById('replaceBtn'),
    redoProcessBtn: document.getElementById('redoProcessBtn'),
    compareBtn: document.getElementById('compareBtn'),
    removeBgToggle: document.getElementById('removeBgToggle'),

    // Templates
    templatesSection: document.getElementById('templatesSection'),
    carouselTrack: document.getElementById('carouselTrack'),
    carouselPrev: document.getElementById('carouselPrev'),
    carouselNext: document.getElementById('carouselNext'),
    categoryTabsContainer: document.getElementById('categoryTabs'),
    categoryTabs: () => document.querySelectorAll('.category-tab'),

    // Download
    downloadSection: document.getElementById('downloadSection'),
    downloadBtn: document.getElementById('downloadBtn'),
    shareWhatsApp: document.getElementById('shareWhatsApp'),
    shareInstagram: document.getElementById('shareInstagram')
};

// ========================================
// Initialization
// ========================================

async function init() {
    await fetchTemplates();
    setupCamera();
    setupUploadZone();
    setupComparator();
    setupTemplates();
    setupActionButtons();
    setupDownload();
    renderTemplates();
}

async function fetchTemplates() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/christmas/templates`);
        if (!response.ok) throw new Error('Falha ao buscar templates');
        TEMPLATES = await response.json();
    } catch (error) {
        console.error('Erro ao carregar templates:', error);
        // Fallback or alert
    }
}

// ========================================
// Camera
// ========================================

async function setupCamera() {
    // Check if camera API is supported
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        console.log('Camera API not supported, showing upload fallback');
        showUploadFallback();
        return;
    }

    try {
        await startCamera();
    } catch (error) {
        console.error('Camera access denied:', error);
        showUploadFallback();
    }
}

async function startCamera() {
    // Stop existing stream if any
    if (state.cameraStream) {
        state.cameraStream.getTracks().forEach(track => track.stop());
    }

    const constraints = {
        video: {
            facingMode: state.facingMode,
            width: { ideal: 1280 },
            height: { ideal: 720 }
        },
        audio: false
    };

    try {
        state.cameraStream = await navigator.mediaDevices.getUserMedia(constraints);
        elements.cameraVideo.srcObject = state.cameraStream;

        // Setup camera buttons
        elements.captureBtn.addEventListener('click', capturePhoto);
        elements.switchCameraBtn.addEventListener('click', switchCamera);

        // Setup gallery button
        elements.galleryBtn.addEventListener('click', () => elements.galleryInput.click());
        elements.galleryInput.addEventListener('change', handleGalleryUpload);
    } catch (error) {
        throw error;
    }
}

// Handle gallery upload
function handleGalleryUpload(e) {
    if (e.target.files.length > 0) {
        const file = e.target.files[0];

        // Stop camera
        if (state.cameraStream) {
            state.cameraStream.getTracks().forEach(track => track.stop());
        }

        // Hide camera zone
        elements.cameraZone.hidden = true;

        // Process the file
        handleImageUpload(file);
    }
}

function capturePhoto() {
    const video = elements.cameraVideo;
    const canvas = document.createElement('canvas');

    // Use video dimensions
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext('2d');

    // Mirror the image for front camera
    if (state.facingMode === 'user') {
        ctx.translate(canvas.width, 0);
        ctx.scale(-1, 1);
    }

    ctx.drawImage(video, 0, 0);

    // Get image as data URL
    state.uploadedImage = canvas.toDataURL('image/jpeg', 0.9);

    // Stop camera
    if (state.cameraStream) {
        state.cameraStream.getTracks().forEach(track => track.stop());
    }

    // Hide camera, show result
    elements.cameraZone.hidden = true;
    showUploadedImage();
}

async function switchCamera() {
    // Toggle facing mode
    state.facingMode = state.facingMode === 'user' ? 'environment' : 'user';

    try {
        await startCamera();
    } catch (error) {
        console.error('Failed to switch camera:', error);
        // Revert to previous mode
        state.facingMode = state.facingMode === 'user' ? 'environment' : 'user';
    }
}

function showUploadFallback() {
    elements.cameraZone.hidden = true;
    elements.uploadZone.hidden = false;
}

// ========================================
// Upload Zone
// ========================================

function setupUploadZone() {
    const { uploadZone, imageInput } = elements;

    // Click to upload
    uploadZone.addEventListener('click', () => imageInput.click());

    // File input change
    imageInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleImageUpload(e.target.files[0]);
        }
    });

    // Drag and drop
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('drag-over');
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('drag-over');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('drag-over');

        const files = e.dataTransfer.files;
        if (files.length > 0 && files[0].type.startsWith('image/')) {
            handleImageUpload(files[0]);
        }
    });
}

async function handleImageUpload(file) {
    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
        alert('A imagem deve ter no máximo 10MB');
        return;
    }

    // Read file as data URL
    const reader = new FileReader();
    reader.onload = (e) => {
        state.uploadedImage = e.target.result;
        showUploadedImage();
    };
    reader.readAsDataURL(file);
}

function showUploadedImage() {
    const { uploadZone, imageComparator, beforeImage, actionButtons } = elements;

    uploadZone.hidden = true;
    imageComparator.hidden = false;
    actionButtons.hidden = false;

    beforeImage.src = state.uploadedImage;

    // If no processed image yet, show same image on both sides
    if (!state.processedImage) {
        elements.afterImage.src = state.uploadedImage;
    }

    // If template selected, process immediately
    if (state.selectedTemplate) {
        processImage();
    }
}

// ========================================
// Image Comparator Slider
// ========================================

function setupComparator() {
    const { comparatorSlider, imageComparator, afterImage, comparatorOverlay } = elements;
    let isDragging = false;

    function updateSliderPosition(x) {
        const rect = imageComparator.getBoundingClientRect();
        let position = ((x - rect.left) / rect.width) * 100;
        position = Math.max(0, Math.min(100, position));

        comparatorSlider.style.left = `${position}%`;
        comparatorOverlay.style.width = `${position}%`;

        // Set the after image width to match the comparator container width
        // This ensures the image doesn't distort when the overlay width changes
        afterImage.style.width = `${rect.width}px`;
    }

    // Update after image width on window resize
    function updateAfterImageWidth() {
        const rect = imageComparator.getBoundingClientRect();
        afterImage.style.width = `${rect.width}px`;
    }

    window.addEventListener('resize', updateAfterImageWidth);

    // Initialize after image is loaded
    afterImage.addEventListener('load', updateAfterImageWidth);

    // Mouse events
    comparatorSlider.addEventListener('mousedown', (e) => {
        isDragging = true;
        e.preventDefault();
    });

    document.addEventListener('mousemove', (e) => {
        if (isDragging) {
            updateSliderPosition(e.clientX);
        }
    });

    document.addEventListener('mouseup', () => {
        isDragging = false;
    });

    // Touch events
    comparatorSlider.addEventListener('touchstart', (e) => {
        isDragging = true;
        e.preventDefault();
    });

    document.addEventListener('touchmove', (e) => {
        if (isDragging && e.touches.length > 0) {
            updateSliderPosition(e.touches[0].clientX);
        }
    });

    document.addEventListener('touchend', () => {
        isDragging = false;
    });

    // Click anywhere on comparator to move slider
    imageComparator.addEventListener('click', (e) => {
        if (e.target !== comparatorSlider && !comparatorSlider.contains(e.target)) {
            updateSliderPosition(e.clientX);
        }
    });
}

// ========================================
// Templates
// ========================================

function setupTemplates() {
    const { carouselPrev, carouselNext } = elements;

    // Carousel navigation
    carouselPrev.addEventListener('click', () => moveCarousel(-1));
    carouselNext.addEventListener('click', () => moveCarousel(1));

    renderCategories();
}

const CATEGORY_LABELS = {
    'populares': 'Populares',
    'classico': 'Clássico',
    'divertido': 'Divertido',
    'papai-noel': 'Papai Noel'
};

function renderCategories() {
    const { categoryTabsContainer } = elements;
    const categories = Object.keys(TEMPLATES);

    let html = `<button class="category-tab ${state.currentCategory === 'todos' ? 'active' : ''}" data-category="todos">Todos</button>`;

    categories.forEach(cat => {
        html += `<button class="category-tab ${state.currentCategory === cat ? 'active' : ''}" data-category="${cat}">${CATEGORY_LABELS[cat] || cat}</button>`;
    });

    categoryTabsContainer.innerHTML = html;

    // Add click handlers
    elements.categoryTabs().forEach(tab => {
        tab.addEventListener('click', () => {
            elements.categoryTabs().forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            state.currentCategory = tab.dataset.category;
            state.carouselPosition = 0;
            renderTemplates();
        });
    });
}

function renderTemplates() {
    const { carouselTrack } = elements;

    // If 'todos', combine all templates from all categories
    let templates;
    if (state.currentCategory === 'todos') {
        templates = Object.values(TEMPLATES).flat();
    } else {
        templates = TEMPLATES[state.currentCategory] || [];
    }

    carouselTrack.innerHTML = templates.map(template => `
        <div class="template-card ${state.selectedTemplate === template.id ? 'selected' : ''}" 
             data-template-id="${template.id}">
            <div class="template-placeholder">${template.emoji}</div>
            <div class="template-name">${template.name}</div>
        </div>
    `).join('');

    // Add click handlers
    carouselTrack.querySelectorAll('.template-card').forEach(card => {
        card.addEventListener('click', () => selectTemplate(card.dataset.templateId));
    });

    updateCarouselPosition();
}

function selectTemplate(templateId) {
    state.selectedTemplate = templateId;
    renderTemplates();

    // If image already uploaded, process it
    if (state.uploadedImage) {
        processImage();
    }
}

function moveCarousel(direction) {
    // Get templates - combine all if 'todos'
    let templates;
    if (state.currentCategory === 'todos') {
        templates = Object.values(TEMPLATES).flat();
    } else {
        templates = TEMPLATES[state.currentCategory] || [];
    }

    const maxPosition = Math.max(0, templates.length - getVisibleCards());

    state.carouselPosition = Math.max(0, Math.min(maxPosition, state.carouselPosition + direction));
    updateCarouselPosition();
}

function getVisibleCards() {
    const containerWidth = elements.carouselTrack.parentElement.offsetWidth;
    const cardWidth = 100 + 16; // width + gap
    return Math.floor(containerWidth / cardWidth);
}

function updateCarouselPosition() {
    const cardWidth = 100 + 16; // width + gap
    const offset = state.carouselPosition * cardWidth;
    elements.carouselTrack.style.transform = `translateX(-${offset}px)`;
}

// ========================================
// Image Processing with SSE Streaming
// ========================================

async function processImage() {
    if (!state.uploadedImage || !state.selectedTemplate || state.isProcessing) {
        return;
    }

    state.isProcessing = true;
    showLoading(true, 'Iniciando processamento...');

    try {
        // Prepare form data
        const formData = new FormData();

        // Convert base64 to blob
        const response = await fetch(state.uploadedImage);
        const blob = await response.blob();
        formData.append('image', blob, 'user-image.jpg');
        formData.append('template', state.selectedTemplate);
        formData.append('remove_bg', elements.removeBgToggle.checked);

        // Use SSE streaming endpoint for progress updates
        const apiResponse = await fetch(`${API_BASE_URL}/api/christmas/swap-stream`, {
            method: 'POST',
            body: formData
        });

        if (!apiResponse.ok) {
            throw new Error('Falha ao processar imagem');
        }

        // Process SSE stream
        const reader = apiResponse.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let eventType = '';
        let eventData = '';

        while (true) {
            const { value, done } = await reader.read();

            if (value) {
                buffer += decoder.decode(value, { stream: true });

                // Parse SSE events from buffer
                const lines = buffer.split('\n');
                buffer = lines.pop() || ''; // Keep incomplete line in buffer

                for (const line of lines) {
                    if (line.startsWith('event: ')) {
                        eventType = line.slice(7).trim();
                    } else if (line.startsWith('data: ')) {
                        eventData += line.slice(6).trim();
                    } else if (line === '' && eventType && eventData) {
                        // Complete event received
                        try {
                            const data = JSON.parse(eventData);
                            handleSSEEvent(eventType, data);
                        } catch (e) {
                            console.error('Error parsing SSE data:', e);
                        }
                        eventType = '';
                        eventData = '';
                    }
                }
            }

            if (done) break;
        }

    } catch (error) {
        console.error('Error processing image:', error);

        // Fallback to non-streaming endpoint
        try {
            await processImageFallback();
        } catch (fallbackError) {
            console.error('Fallback also failed:', fallbackError);
            showLoading(false);
            alert('Erro ao processar imagem. Tente novamente.');
        }
    } finally {
        state.isProcessing = false;
    }
}

function handleSSEEvent(eventType, data) {
    switch (eventType) {
        case 'progress':
            // Update loading message with progress
            const percent = data.percent || 0;
            showLoading(true, data.message || 'Processando...', percent);
            break;

        case 'complete':
            // Image processing complete
            if (data.success && data.processed_image) {
                state.processedImage = data.processed_image;
                addToHistory(state.processedImage);

                elements.afterImage.src = state.processedImage;
                elements.downloadSection.hidden = false;
                showLoading(false);
            }
            break;

        case 'error':
            // Handle error
            console.error('SSE Error:', data.message);
            showLoading(false);
            alert(data.message || 'Erro ao processar imagem');
            break;
    }
}

// Fallback to regular endpoint when SSE fails
async function processImageFallback() {
    const formData = new FormData();
    const response = await fetch(state.uploadedImage);
    const blob = await response.blob();
    formData.append('image', blob, 'user-image.jpg');
    formData.append('template', state.selectedTemplate);
    formData.append('remove_bg', elements.removeBgToggle.checked);

    const apiResponse = await fetch(`${API_BASE_URL}/api/christmas/swap`, {
        method: 'POST',
        body: formData
    });

    if (!apiResponse.ok) {
        throw new Error('Falha ao processar imagem');
    }

    const result = await apiResponse.json();
    state.processedImage = result.processed_image;
    addToHistory(state.processedImage);

    elements.afterImage.src = state.processedImage;
    elements.downloadSection.hidden = false;
    showLoading(false);
}

// Simulated processing for demo when API not available
async function simulateProcessing() {
    await new Promise(resolve => setTimeout(resolve, 1500));

    // For demo, just show the original image with a festive overlay effect
    const canvas = document.createElement('canvas');
    const img = new Image();

    img.onload = () => {
        canvas.width = img.width;
        canvas.height = img.height;
        const ctx = canvas.getContext('2d');

        // Draw original image
        ctx.drawImage(img, 0, 0);

        // Add festive overlay effect (placeholder)
        ctx.fillStyle = 'rgba(196, 30, 58, 0.1)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Add some festive text
        ctx.font = 'bold 48px Outfit';
        ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
        ctx.textAlign = 'center';
        ctx.fillText('🎄', canvas.width / 2, canvas.height / 2);

        state.processedImage = canvas.toDataURL('image/jpeg', 0.9);
        addToHistory(state.processedImage);

        elements.afterImage.src = state.processedImage;
        elements.downloadSection.hidden = false;
    };

    img.src = state.uploadedImage;
}

function showLoading(show, message = 'Processando sua imagem...', percent = 0) {
    elements.loadingState.hidden = !show;
    elements.imageComparator.hidden = show;

    // Update loading message if element exists
    const loadingText = elements.loadingState.querySelector('.loading-text');
    if (loadingText && message) {
        loadingText.textContent = message;
    }

    // Update progress bar if exists
    const progressBar = elements.loadingState.querySelector('.progress-bar-fill');
    if (progressBar && percent > 0) {
        progressBar.style.width = `${percent}%`;
    }
}


// ========================================
// History (Undo/Redo)
// ========================================

function addToHistory(imageData) {
    // Remove any redo states
    state.history = state.history.slice(0, state.historyIndex + 1);

    // Add new state
    state.history.push(imageData);
    state.historyIndex = state.history.length - 1;

    updateHistoryButtons();
}

function undo() {
    if (state.historyIndex > 0) {
        state.historyIndex--;
        state.processedImage = state.history[state.historyIndex];
        elements.afterImage.src = state.processedImage;
        updateHistoryButtons();
    }
}

function redo() {
    if (state.historyIndex < state.history.length - 1) {
        state.historyIndex++;
        state.processedImage = state.history[state.historyIndex];
        elements.afterImage.src = state.processedImage;
        updateHistoryButtons();
    }
}

function updateHistoryButtons() {
    // Buttons removed from UI
}

// ========================================
// Action Buttons
// ========================================

function setupActionButtons() {
    const { replaceBtn, redoProcessBtn, compareBtn } = elements;

    replaceBtn.addEventListener('click', () => {
        elements.imageInput.click();
    });

    redoProcessBtn.addEventListener('click', () => {
        if (state.uploadedImage && state.selectedTemplate) {
            processImage();
        }
    });

    compareBtn.addEventListener('click', () => {
        // Toggle between showing before/after
        const slider = elements.comparatorSlider;
        const currentPos = parseFloat(slider.style.left) || 50;

        if (currentPos > 25) {
            slider.style.left = '0%';
            elements.comparatorOverlay.style.width = '0%';
        } else {
            slider.style.left = '50%';
            elements.comparatorOverlay.style.width = '50%';
        }
    });
}

// ========================================
// Download & Share
// ========================================

function setupDownload() {
    const { downloadBtn, shareWhatsApp, shareInstagram } = elements;

    downloadBtn.addEventListener('click', () => {
        if (!state.processedImage) return;

        const link = document.createElement('a');
        link.download = 'avatar-natal-klique.jpg';
        link.href = state.processedImage;
        link.click();
    });

    shareWhatsApp.addEventListener('click', () => {
        // WhatsApp sharing (opens WhatsApp with message)
        const text = encodeURIComponent('Veja meu avatar de Natal! 🎄 Criado com Klique Natal');
        window.open(`https://wa.me/?text=${text}`, '_blank');
    });

    shareInstagram.addEventListener('click', () => {
        // Instagram doesn't support direct image sharing via web
        // Show instructions
        alert('Para compartilhar no Instagram:\n1. Baixe a imagem\n2. Abra o Instagram\n3. Crie uma nova publicação ou story');
    });
}

// ========================================
// Start App
// ========================================

document.addEventListener('DOMContentLoaded', init);
