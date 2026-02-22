// ===== Dashboard BB 2026 - Main App =====

// ===== State Management =====
const state = {
    examDate: localStorage.getItem('examDate') || '2026-06-15',
    studyData: JSON.parse(localStorage.getItem('studyData')) || {
        portugues: { hours: 0, questions: 0, correct: 0, progress: 0 },
        matematica: { hours: 0, questions: 0, correct: 0, progress: 0 },
        bancarios: { hours: 0, questions: 0, correct: 0, progress: 0 },
        vendas: { hours: 0, questions: 0, correct: 0, progress: 0 },
        informatica: { hours: 0, questions: 0, correct: 0, progress: 0 },
        atualidades: { hours: 0, questions: 0, correct: 0, progress: 0 },
        atendimento: { hours: 0, questions: 0, correct: 0, progress: 0 },
        ingles: { hours: 0, questions: 0, correct: 0, progress: 0 },
        estatistica: { hours: 0, questions: 0, correct: 0, progress: 0 }
    },
    weeklyHours: JSON.parse(localStorage.getItem('weeklyHours')) || [0, 0, 0, 0, 0, 0, 0],
    checklist: JSON.parse(localStorage.getItem('checklist')) || {}
};

// Subject labels
const subjectLabels = {
    portugues: 'Português',
    matematica: 'Matemática',
    bancarios: 'Bancários',
    vendas: 'Vendas',
    informatica: 'Informática',
    atualidades: 'Atualidades',
    atendimento: 'Atendimento',
    ingles: 'Inglês',
    estatistica: 'Estatística'
};

// ===== Theme Management =====
function initTheme() {
    const themeToggle = document.getElementById('themeToggle');
    
    // Verifica se o usuário já definiu manualmente um tema
    const savedTheme = localStorage.getItem('dashboardTheme');
    
    if (savedTheme) {
        // Se o usuário já definiu manualmente, usa o tema salvo
        applyTheme(savedTheme);
        updateThemeToggleVisual(savedTheme);
    } else {
        // Caso contrário, aplica o tema baseado no horário
        applyTimeBasedTheme();
    }
    
    // Adiciona evento de clique ao toggle
    themeToggle.addEventListener('click', () => {
        // Quando o usuário clica manualmente, registramos isso e não usamos mais o tema baseado no tempo
        let currentTheme = localStorage.getItem('dashboardTheme') || getTimeBasedTheme();
        let newTheme;
        
        // Alterna entre os temas
        if (currentTheme === 'light') {
            newTheme = 'dark';
        } else if (currentTheme === 'dark') {
            newTheme = 'manual-system';
        } else if (currentTheme === 'manual-system') {
            newTheme = 'time-based';
        } else { // time-based or undefined
            newTheme = 'light';
        }
        
        localStorage.setItem('dashboardTheme', newTheme);
        applyTheme(newTheme);
        updateThemeToggleVisual(newTheme);
    });
    
    // Também adiciona suporte para teclado
    themeToggle.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            themeToggle.click();
        }
    });
    
    // Atualiza o tema com base no horário a cada hora
    setInterval(checkAndApplyTimeBasedTheme, 60 * 60 * 1000); // A cada hora
}

// Função para determinar o tema com base no horário
function getTimeBasedTheme() {
    const hour = new Date().getHours();
    
    // Define o tema com base na hora do dia
    // 6h às 18h = claro (manhã/tarde)
    // 18h às 6h = escuro (tarde/noite)
    if (hour >= 6 && hour < 18) {
        return 'light';
    } else {
        return 'dark';
    }
}

// Função para aplicar o tema baseado no horário
function applyTimeBasedTheme() {
    const timeBasedTheme = getTimeBasedTheme();
    applyTheme('time-based'); // Usamos 'time-based' para indicar que é uma transição automática
    updateThemeToggleVisual(timeBasedTheme);
}

// Função para verificar e aplicar o tema baseado no horário se estiver no modo automático
function checkAndApplyTimeBasedTheme() {
    const currentStoredTheme = localStorage.getItem('dashboardTheme');
    
    // Apenas aplica o tema baseado no tempo se o usuário tiver deixado no modo automático
    if (!currentStoredTheme || currentStoredTheme === 'time-based') {
        // Verificamos se o tema baseado no tempo é diferente do tema atual para evitar animações desnecessárias
        const currentTimeBasedTheme = getTimeBasedTheme();
        const currentAppliedTheme = document.body.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
        
        if (currentTimeBasedTheme !== currentAppliedTheme) {
            // Adiciona um pequeno delay para garantir que o usuário possa perceber a transição
            // Isso é especialmente útil se o usuário estiver usando o dashboard no momento da transição
            setTimeout(() => {
                applyTimeBasedTheme();
            }, 100); // Pequeno delay para garantir visibilidade
        }
    }
}

function updateThemeToggleVisual(theme) {
    const themeToggle = document.getElementById('themeToggle');
    const body = document.body;
    
    // Remove qualquer classe de tema anterior
    body.classList.remove('light-theme', 'dark-theme', 'system-theme');
    
    // Atualiza o estado do toggle com base no tema
    if (theme === 'dark' || theme === 'manual-system') {
        body.setAttribute('data-theme', 'dark');
        // O CSS já lida com a transição visual do toggle
    } else if (theme === 'system') {
        // Detecta a preferência do sistema
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            body.setAttribute('data-theme', 'dark');
        } else {
            body.removeAttribute('data-theme');
        }
        // O CSS já lida com a transição visual do toggle
    } else { // light or time-based
        body.removeAttribute('data-theme');
    }
}

function applyTheme(theme) {
    const body = document.body;
    const themeWipe = document.getElementById('themeWipe');
    
    // Determine the actual theme to apply
    let actualTheme = theme;
    if (theme === 'time-based') {
        actualTheme = getTimeBasedTheme();
    } else if (theme === 'manual-system') {
        // Manual system mode - detect system preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            actualTheme = 'dark';
        } else {
            actualTheme = 'light';
        }
    }
    
    // Get the current theme to determine the wipe color
    const currentThemeIsDark = body.hasAttribute('data-theme') && body.getAttribute('data-theme') === 'dark';
    let startWipeColor;
    
    // If switching FROM dark TO light, start with dark color
    // If switching FROM light TO dark, start with light color
    if (currentThemeIsDark && actualTheme !== 'dark') {
        // Dark to Light - use dark as starting color
        startWipeColor = '#0b1116'; // Dark theme background color
    } else if (!currentThemeIsDark && actualTheme === 'dark') {
        // Light to Dark - use light as starting color
        startWipeColor = '#f7f5f2'; // Light theme background color
    } else {
        // Same theme or fallback - use the opposite of the target theme
        startWipeColor = actualTheme === 'dark' ? '#f7f5f2' : '#0b1116';
    }
    
    // Set the wipe color to the appropriate color for the transition
    themeWipe.style.setProperty('--wipe-color', startWipeColor);
    
    // Set the wipe position to the center of the screen
    themeWipe.style.setProperty('--wipe-x', '50vw');
    themeWipe.style.setProperty('--wipe-y', '50vh');
    
    // Trigger the wipe animation FIRST
    themeWipe.classList.add('is-active');
    
    // Apply the theme after a delay to allow the wipe to be visible
    setTimeout(() => {
        body.removeAttribute('data-theme'); // Remove any existing data-theme attribute
        
        switch(actualTheme) {
            case 'dark':
                body.setAttribute('data-theme', 'dark');
                break;
            case 'light':
            default:
                // Light theme is default, no attribute needed
                break;
        }
        
        // Remove the wipe animation class after it completes
        setTimeout(() => {
            themeWipe.classList.remove('is-active');
        }, 700); // Match the duration of the CSS animation
    }, 50); // Delay to allow wipe animation to start
}

// ===== Initialization =====
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initTheme(); // Initialize theme selection
    initCountdown();
    initCharts();
    initStudyLog();
    initChecklist();
    initMaterias();
    updateStats();
    
    // Set exam date input
    document.getElementById('examDate').value = state.examDate;
});

// ===== Navigation =====
function initNavigation() {
    const navBtns = document.querySelectorAll('.nav-btn');
    const sections = document.querySelectorAll('.section');
    
    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.dataset.section;
            
            navBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            sections.forEach(s => {
                s.classList.remove('active');
                if (s.id === target) {
                    s.classList.add('active');
                }
            });
        });
    });
}

// ===== Countdown Timer =====
function initCountdown() {
    updateCountdown();
    setInterval(updateCountdown, 10); // Atualiza a cada 10ms para mostrar centésimos
    
    document.getElementById('updateDate').addEventListener('click', () => {
        const newDate = document.getElementById('examDate').value;
        if (newDate) {
            state.examDate = newDate;
            localStorage.setItem('examDate', newDate);
            updateCountdown();
            showToast('Data da prova atualizada!');
        }
    });
}

function updateCountdown() {
    const now = new Date();
    const examDate = new Date(state.examDate + 'T00:00:00');
    const diff = examDate - now;
    
    if (diff <= 0) {
        document.getElementById('years').textContent = '0';
        document.getElementById('months').textContent = '0';
        document.getElementById('weeks').textContent = '0';
        document.getElementById('days').textContent = '0';
        document.getElementById('hours').textContent = '0';
        document.getElementById('minutes').textContent = '0';
        document.getElementById('seconds').textContent = '0';
        document.getElementById('centiseconds').textContent = '0';
        document.getElementById('totalDays').textContent = '0';
        return;
    }
    
    const totalDays = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    // Calculate years, months, weeks, days, hours, minutes, seconds, centiseconds
    const years = Math.floor(totalDays / 365);
    const remainingAfterYears = totalDays % 365;
    const months = Math.floor(remainingAfterYears / 30);
    const remainingAfterMonths = remainingAfterYears % 30;
    const weeks = Math.floor(remainingAfterMonths / 7);
    const days = remainingAfterMonths % 7;
    
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);
    const centiseconds = Math.floor((diff % 1000) / 10);
    
    // Animate number updates
    animateNumber('years', years);
    animateNumber('months', months);
    animateNumber('weeks', weeks);
    animateNumber('days', days);
    animateNumber('hours', hours);
    animateNumber('minutes', minutes);
    animateNumber('seconds', seconds);
    animateNumber('centiseconds', centiseconds);
    
    document.getElementById('totalDays').textContent = totalDays.toLocaleString();
}

function animateNumber(elementId, newValue) {
    const el = document.getElementById(elementId);
    // Formata com zero à esquerda para valores menores que 10 (exceto anos)
    let formattedValue;
    if (elementId !== 'years' && elementId !== 'months' && elementId !== 'totalDays') {
        formattedValue = String(newValue).padStart(2, '0');
    } else {
        formattedValue = String(newValue);
    }
    
    if (el.textContent !== formattedValue) {
        el.style.transform = 'scale(1.1)';
        el.textContent = formattedValue;
        setTimeout(() => {
            el.style.transform = 'scale(1)';
        }, 150);
    }
}

// ===== Charts =====
let progressChart, hoursChart;

function initCharts() {
    const progressCtx = document.getElementById('progressChart').getContext('2d');
    const hoursCtx = document.getElementById('hoursChart').getContext('2d');
    
    // Progress Chart
    progressChart = new Chart(progressCtx, {
        type: 'bar',
        data: {
            labels: Object.values(subjectLabels),
            datasets: [{
                label: 'Progresso (%)',
                data: Object.keys(subjectLabels).map(k => state.studyData[k].progress),
                backgroundColor: [
                    'rgba(248, 209, 47, 0.8)',
                    'rgba(41, 98, 255, 0.8)',
                    'rgba(76, 175, 80, 0.8)',
                    'rgba(255, 152, 0, 0.8)',
                    'rgba(156, 39, 176, 0.8)',
                    'rgba(0, 188, 212, 0.8)',
                    'rgba(233, 30, 99, 0.8)',
                    'rgba(121, 85, 72, 0.8)',
                    'rgba(96, 125, 139, 0.8)'
                ],
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#a0a0b0' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#a0a0b0', maxRotation: 45, minRotation: 45 }
                }
            }
        }
    });
    
    // Hours Chart
    const dayLabels = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];
    
    hoursChart = new Chart(hoursCtx, {
        type: 'line',
        data: {
            labels: dayLabels,
            datasets: [{
                label: 'Horas',
                data: state.weeklyHours,
                borderColor: '#f8d12f',
                backgroundColor: 'rgba(248, 209, 47, 0.1)',
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#f8d12f',
                pointBorderColor: '#fff',
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#a0a0b0' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#a0a0b0' }
                }
            }
        }
    });
}

function updateCharts() {
    if (progressChart) {
        progressChart.data.datasets[0].data = Object.keys(subjectLabels).map(k => state.studyData[k].progress);
        progressChart.update();
    }
    
    if (hoursChart) {
        hoursChart.data.datasets[0].data = state.weeklyHours;
        hoursChart.update();
    }
}

// ===== Study Log =====
function initStudyLog() {
    document.getElementById('logStudy').addEventListener('click', () => {
        const subject = document.getElementById('studySubject').value;
        const hours = parseFloat(document.getElementById('studyHours').value) || 0;
        const questions = parseInt(document.getElementById('questionsCount').value) || 0;
        const correct = parseInt(document.getElementById('correctCount').value) || 0;
        
        if (hours > 0 || questions > 0) {
            state.studyData[subject].hours += hours;
            state.studyData[subject].questions += questions;
            state.studyData[subject].correct += correct;
            
            // Update weekly hours (current day)
            const today = new Date().getDay();
            state.weeklyHours[today] += hours;
            
            saveState();
            updateStats();
            updateCharts();
            updateMaterias();
            
            // Reset form
            document.getElementById('studyHours').value = 1;
            document.getElementById('questionsCount').value = 0;
            document.getElementById('correctCount').value = 0;
            
            showToast(`${hours}h de ${subjectLabels[subject]} registradas!`);
        }
    });
}

// ===== Stats =====
function updateStats() {
    const totalHours = Object.values(state.studyData).reduce((sum, s) => sum + s.hours, 0);
    const totalQuestions = Object.values(state.studyData).reduce((sum, s) => sum + s.questions, 0);
    const totalCorrect = Object.values(state.studyData).reduce((sum, s) => sum + s.correct, 0);
    const avgAccuracy = totalQuestions > 0 ? Math.round((totalCorrect / totalQuestions) * 100) : 0;
    const avgProgress = Math.round(Object.values(state.studyData).reduce((sum, s) => sum + s.progress, 0) / 9);
    
    document.getElementById('totalHours').textContent = totalHours.toFixed(1);
    document.getElementById('totalQuestions').textContent = totalQuestions;
    document.getElementById('avgAccuracy').textContent = avgAccuracy + '%';
    document.getElementById('overallProgress').textContent = avgProgress + '%';
}

// ===== Checklist =====
function initChecklist() {
    const checkboxes = document.querySelectorAll('.checklist-item input[type="checkbox"]');
    const phaseHeaders = document.querySelectorAll('.phase-header');
    
    // Load saved state
    checkboxes.forEach(cb => {
        if (state.checklist[cb.id]) {
            cb.checked = true;
        }
        
        cb.addEventListener('change', () => {
            state.checklist[cb.id] = cb.checked;
            saveState();
            updateChecklistProgress();
            updatePhaseCount(cb.dataset.phase);
        });
    });
    
    // Toggle phases
    phaseHeaders.forEach(header => {
        header.addEventListener('click', () => {
            const phaseId = header.dataset.phase;
            const content = document.getElementById(phaseId);
            content.classList.toggle('hidden');
            header.classList.toggle('collapsed');
        });
    });
    
    updateChecklistProgress();
    updateAllPhaseCounts();
}

function updateChecklistProgress() {
    const total = document.querySelectorAll('.checklist-item input[type="checkbox"]').length;
    const checked = Object.values(state.checklist).filter(v => v).length;
    const percentage = Math.round((checked / total) * 100);
    
    document.getElementById('checklistProgress').style.width = percentage + '%';
    document.getElementById('checklistPercentage').textContent = percentage + '%';
}

function updatePhaseCount(phaseId) {
    const phase = document.querySelector(`[data-phase="${phaseId}"]`).closest('.checklist-phase');
    const checkboxes = phase.querySelectorAll('.checklist-item input[type="checkbox"]');
    const checked = Array.from(checkboxes).filter(cb => cb.checked).length;
    const total = checkboxes.length;
    
    phase.querySelector('.phase-count').textContent = `${checked}/${total}`;
}

function updateAllPhaseCounts() {
    const phases = ['fase1', 'fase2', 'fase3', 'fase4', 'fase5', 'fase6'];
    phases.forEach(updatePhaseCount);
}

// ===== Materias =====
function initMaterias() {
    const sliders = document.querySelectorAll('.progress-slider');
    
    sliders.forEach(slider => {
        const subject = slider.dataset.subject;
        slider.value = state.studyData[subject].progress;
        
        slider.addEventListener('input', () => {
            const value = parseInt(slider.value);
            state.studyData[subject].progress = value;
            document.getElementById(`${subject}-progress`).style.width = value + '%';
        });
        
        slider.addEventListener('change', () => {
            saveState();
            updateStats();
            updateCharts();
        });
    });
    
    updateMaterias();
}

function updateMaterias() {
    Object.keys(state.studyData).forEach(subject => {
        const data = state.studyData[subject];
        const accuracy = data.questions > 0 ? Math.round((data.correct / data.questions) * 100) : 0;
        
        const hoursEl = document.getElementById(`${subject}-hours`);
        const questionsEl = document.getElementById(`${subject}-questions`);
        const accuracyEl = document.getElementById(`${subject}-accuracy`);
        const progressEl = document.getElementById(`${subject}-progress`);
        const sliderEl = document.querySelector(`.progress-slider[data-subject="${subject}"]`);
        
        if (hoursEl) hoursEl.textContent = data.hours.toFixed(1);
        if (questionsEl) questionsEl.textContent = data.questions;
        if (accuracyEl) accuracyEl.textContent = accuracy + '%';
        if (progressEl) progressEl.style.width = data.progress + '%';
        if (sliderEl) sliderEl.value = data.progress;
    });
}

// ===== Utilities =====
function saveState() {
    localStorage.setItem('studyData', JSON.stringify(state.studyData));
    localStorage.setItem('weeklyHours', JSON.stringify(state.weeklyHours));
    localStorage.setItem('checklist', JSON.stringify(state.checklist));
}

function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ===== Reset functionality (for debugging) =====
window.resetDashboard = function() {
    if (confirm('Tem certeza que deseja resetar todos os dados?')) {
        localStorage.clear();
        location.reload();
    }
};
