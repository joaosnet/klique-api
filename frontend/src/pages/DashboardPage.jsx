import React, { useState, useEffect } from 'react';
import './DashboardStyles.css';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';
import { domainsAPI } from '../services/api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const CHART_COLORS = [
  'rgba(248, 209, 47, 0.8)',
  'rgba(41, 98, 255, 0.8)',
  'rgba(76, 175, 80, 0.8)',
  'rgba(255, 152, 0, 0.8)',
  'rgba(156, 39, 176, 0.8)',
  'rgba(0, 188, 212, 0.8)',
  'rgba(233, 30, 99, 0.8)',
  'rgba(121, 85, 72, 0.8)',
  'rgba(96, 125, 139, 0.8)',
  'rgba(63, 81, 181, 0.8)',
  'rgba(139, 195, 74, 0.8)',
  'rgba(255, 87, 34, 0.8)',
];

const DOMAIN_ICONS = [
  '📖', '🔢', '🏦', '💼', '💻', '📈', '🤝', '🇬🇧', '📊',
  '🎯', '🧠', '⚡', '🎲', '🗂️', '🌐', '🔬',
];



export default function DashboardPage() {
  const [activeMenu, setActiveMenu] = useState('dashboard');

  const [examDate, setExamDate] = useState(() => {
    return localStorage.getItem('examDate') || '2026-06-15';
  });

  // Dynamic domains fetched from API
  const [domains, setDomains] = useState([]);
  const [domainsLoading, setDomainsLoading] = useState(true);

  // studyData is now keyed by domain id
  const [studyData, setStudyData] = useState(() => {
    const saved = localStorage.getItem('studyData_v2');
    if (saved) return JSON.parse(saved);
    return {};
  });

  const [weeklyHours, setWeeklyHours] = useState(() => {
    const saved = localStorage.getItem('weeklyHours');
    if (saved) return JSON.parse(saved);
    return [0, 0, 0, 0, 0, 0, 0];
  });

  const [timeRemaining, setTimeRemaining] = useState({
    years: 0, months: 0, weeks: 0, days: 0, hours: 0, minutes: 0, seconds: 0, totalDays: 0
  });

  const [logForm, setLogForm] = useState({
    subject: '',
    hours: 1,
    questions: 0,
    correct: 0
  });

  // Fetch domains from API
  useEffect(() => {
    const loadDomains = async () => {
      setDomainsLoading(true);
      try {
        const data = await domainsAPI.list();
        setDomains(data);
        // Initialize studyData for any new domains
        setStudyData(prev => {
          const updated = { ...prev };
          data.forEach(({ domain }) => {
            if (!updated[domain.id]) {
              updated[domain.id] = { hours: 0, questions: 0, correct: 0, progress: 0 };
            }
          });
          return updated;
        });
        // Set default logForm subject to first domain
        if (data.length > 0) {
          setLogForm(prev => prev.subject ? prev : { ...prev, subject: data[0].domain.id });
        }
      } catch (e) {
        console.error('Error fetching domains:', e);
      } finally {
        setDomainsLoading(false);
      }
    };
    loadDomains();
  }, []);

  // Build a map of domain id -> label for easy lookup
  const domainLabels = {};
  domains.forEach(({ domain }) => {
    domainLabels[domain.id] = domain.name;
  });

  // Calculate stats (only for domains that exist)
  const activeDomainIds = domains.map(({ domain }) => domain.id);
  const totalHours = activeDomainIds.reduce((sum, id) => sum + (studyData[id]?.hours || 0), 0);
  const totalQuestions = activeDomainIds.reduce((sum, id) => sum + (studyData[id]?.questions || 0), 0);
  const totalCorrect = activeDomainIds.reduce((sum, id) => sum + (studyData[id]?.correct || 0), 0);
  const avgAccuracy = totalQuestions > 0 ? Math.round((totalCorrect / totalQuestions) * 100) : 0;
  const avgProgress = activeDomainIds.length > 0
    ? Math.round(activeDomainIds.reduce((sum, id) => sum + (studyData[id]?.progress || 0), 0) / activeDomainIds.length)
    : 0;



  useEffect(() => {
    localStorage.setItem('examDate', examDate);
  }, [examDate]);

  useEffect(() => {
    localStorage.setItem('studyData_v2', JSON.stringify(studyData));
    localStorage.setItem('weeklyHours', JSON.stringify(weeklyHours));
  }, [studyData, weeklyHours]);

  // Countdown timer
  useEffect(() => {
    const interval = setInterval(() => {
      const now = new Date();
      const exam = new Date(examDate + 'T00:00:00');
      const diff = exam - now;

      if (diff <= 0) {
        setTimeRemaining({
          years: 0, months: 0, weeks: 0, days: 0, hours: 0, minutes: 0, seconds: 0, totalDays: 0
        });
        return;
      }

      const totalDays = Math.floor(diff / (1000 * 60 * 60 * 24));
      const years = Math.floor(totalDays / 365);
      const remainingAfterYears = totalDays % 365;
      const months = Math.floor(remainingAfterYears / 30);
      const remainingAfterMonths = remainingAfterYears % 30;
      const weeks = Math.floor(remainingAfterMonths / 7);
      const days = remainingAfterMonths % 7;

      const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((diff % (1000 * 60)) / 1000);

      setTimeRemaining({
        years, months, weeks, days, hours, minutes, seconds, totalDays
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [examDate]);

  const handleStudyProgressChange = (domainId, value) => {
    const val = Math.min(100, Math.max(0, parseInt(value, 10) || 0));
    setStudyData(prev => ({
      ...prev,
      [domainId]: { ...prev[domainId], progress: val }
    }));
  };

  const logStudy = () => {
    const hours = parseFloat(logForm.hours) || 0;
    const questions = parseInt(logForm.questions, 10) || 0;
    const correct = parseInt(logForm.correct, 10) || 0;

    if ((hours > 0 || questions > 0) && logForm.subject) {
      setStudyData(prev => ({
        ...prev,
        [logForm.subject]: {
          ...(prev[logForm.subject] || { hours: 0, questions: 0, correct: 0, progress: 0 }),
          hours: (prev[logForm.subject]?.hours || 0) + hours,
          questions: (prev[logForm.subject]?.questions || 0) + questions,
          correct: (prev[logForm.subject]?.correct || 0) + correct,
        }
      }));

      const today = new Date().getDay();
      setWeeklyHours(prev => {
        const next = [...prev];
        next[today] += hours;
        return next;
      });

      setLogForm(prev => ({ ...prev, hours: 1, questions: 0, correct: 0 }));
    }
  };



  // Chart Data — dynamic from domains
  const progressChartData = {
    labels: activeDomainIds.map(id => domainLabels[id] || id),
    datasets: [{
      label: 'Progresso (%)',
      data: activeDomainIds.map(id => studyData[id]?.progress || 0),
      backgroundColor: activeDomainIds.map((_, i) => CHART_COLORS[i % CHART_COLORS.length]),
      borderRadius: 8,
    }]
  };

  const progressChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      y: { beginAtZero: true, max: 100, grid: { color: 'rgba(150,150,150,0.1)' } },
      x: { grid: { display: false } }
    }
  };

  const hoursChartData = {
    labels: ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'],
    datasets: [{
      label: 'Horas',
      data: weeklyHours,
      borderColor: '#f8d12f',
      backgroundColor: 'rgba(248, 209, 47, 0.1)',
      fill: true,
      tension: 0.4,
      pointBackgroundColor: '#f8d12f',
      pointBorderColor: '#fff',
      pointRadius: 6,
    }]
  };

  const hoursChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      y: { beginAtZero: true, grid: { color: 'rgba(150,150,150,0.1)' } },
      x: { grid: { display: false } }
    }
  };

  return (
    <div className="dashboard-container">
      <div className="dash-app-container">
        {/* Header */}
        <header className="dash-header">
          <div className="dash-header-content">
            <div className="dash-logo">
              <div className="dash-logo-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
                </svg>
              </div>
              <div className="dash-logo-text">
                <h1>OmniFlash</h1>
                <span>Meus Estudos</span>
              </div>
            </div>

            <nav className="dash-nav">
              <button
                className={`dash-nav-btn ${activeMenu === 'dashboard' ? 'active' : ''}`}
                onClick={() => setActiveMenu('dashboard')}
              >
                Dashboard
              </button>
              <button
                className={`dash-nav-btn ${activeMenu === 'materias' ? 'active' : ''}`}
                onClick={() => setActiveMenu('materias')}
              >
                Domínios
              </button>
            </nav>

          </div>
        </header>

        <main className="dash-main-content">
          {activeMenu === 'dashboard' && (
            <section className="dash-section active">
              {/* Countdown Timer */}
              <div className="dash-countdown-container">
                <h2 className="dash-section-title justify-center">
                  <span className="dash-title-icon">⏱️</span>
                  Contagem Regressiva
                </h2>
                <p className="dash-countdown-subtitle">Defina sua data-alvo abaixo</p>

                <div className="dash-countdown-grid">
                  <div className="dash-countdown-item">
                    <div className="dash-countdown-value">{timeRemaining.years}</div>
                    <div className="dash-countdown-label">Anos</div>
                  </div>
                  <div className="dash-countdown-separator">:</div>
                  <div className="dash-countdown-item">
                    <div className="dash-countdown-value">{timeRemaining.months}</div>
                    <div className="dash-countdown-label">Meses</div>
                  </div>
                  <div className="dash-countdown-separator">:</div>
                  <div className="dash-countdown-item">
                    <div className="dash-countdown-value">{timeRemaining.weeks}</div>
                    <div className="dash-countdown-label">Semanas</div>
                  </div>
                  <div className="dash-countdown-separator">:</div>
                  <div className="dash-countdown-item">
                    <div className="dash-countdown-value">{timeRemaining.days}</div>
                    <div className="dash-countdown-label">Dias</div>
                  </div>
                  <div className="dash-countdown-separator">:</div>
                  <div className="dash-countdown-item">
                    <div className="dash-countdown-value">{String(timeRemaining.hours).padStart(2, '0')}</div>
                    <div className="dash-countdown-label">Horas</div>
                  </div>
                  <div className="dash-countdown-separator">:</div>
                  <div className="dash-countdown-item">
                    <div className="dash-countdown-value">{String(timeRemaining.minutes).padStart(2, '0')}</div>
                    <div className="dash-countdown-label">Minutos</div>
                  </div>
                  <div className="dash-countdown-separator">:</div>
                  <div className="dash-countdown-item">
                    <div className="dash-countdown-value">{String(timeRemaining.seconds).padStart(2, '0')}</div>
                    <div className="dash-countdown-label">Segundos</div>
                  </div>
                </div>

                <div className="dash-total-days">
                  <span>{timeRemaining.totalDays.toLocaleString()}</span> dias restantes
                </div>

                <div className="dash-exam-date-config">
                  <label>Data-Alvo:</label>
                  <input
                    type="date"
                    value={examDate}
                    onChange={(e) => setExamDate(e.target.value)}
                  />
                </div>
              </div>

              {/* Stats Cards */}
              <div className="dash-stats-grid">
                <div className="dash-stat-card">
                  <div className="dash-stat-icon study">📚</div>
                  <div className="dash-stat-info">
                    <span className="dash-stat-value">{totalHours.toFixed(1)}</span>
                    <span className="dash-stat-label">Horas Estudadas</span>
                  </div>
                  <div className="dash-stat-trend up">Meta: 500h</div>
                </div>
                <div className="dash-stat-card">
                  <div className="dash-stat-icon questions">❓</div>
                  <div className="dash-stat-info">
                    <span className="dash-stat-value">{totalQuestions}</span>
                    <span className="dash-stat-label">Questões Resolvidas</span>
                  </div>
                  <div className="dash-stat-trend up">Meta: 3000</div>
                </div>
                <div className="dash-stat-card">
                  <div className="dash-stat-icon accuracy">🎯</div>
                  <div className="dash-stat-info">
                    <span className="dash-stat-value">{avgAccuracy}%</span>
                    <span className="dash-stat-label">Taxa de Acerto</span>
                  </div>
                  <div className="dash-stat-trend up">Meta: 80%</div>
                </div>
                <div className="dash-stat-card">
                  <div className="dash-stat-icon progress">📈</div>
                  <div className="dash-stat-info">
                    <span className="dash-stat-value">{avgProgress}%</span>
                    <span className="dash-stat-label">Progresso Geral</span>
                  </div>
                  <div className="dash-stat-trend">Conteúdo</div>
                </div>
              </div>

              {/* Charts Section */}
              <div className="dash-charts-grid">
                <div className="dash-chart-container" style={{ height: 350 }}>
                  <h3 className="dash-chart-title">📊 Progresso por Domínio</h3>
                  <div style={{ height: 250 }}>
                    {domainsLoading ? (
                      <p style={{ color: 'var(--dash-text-secondary)', textAlign: 'center', paddingTop: 80 }}>Carregando domínios...</p>
                    ) : activeDomainIds.length === 0 ? (
                      <p style={{ color: 'var(--dash-text-secondary)', textAlign: 'center', paddingTop: 80 }}>Nenhum domínio criado ainda.</p>
                    ) : (
                      <Bar data={progressChartData} options={progressChartOptions} />
                    )}
                  </div>
                </div>
                <div className="dash-chart-container" style={{ height: 350 }}>
                  <h3 className="dash-chart-title">📈 Horas de Estudo (Semana)</h3>
                  <div style={{ height: 250 }}>
                    <Line data={hoursChartData} options={hoursChartOptions} />
                  </div>
                </div>
              </div>

              {/* Study Log */}
              <div className="dash-study-log">
                <h3 className="dash-section-title">
                  <span className="dash-title-icon">📝</span>
                  Registrar Estudo
                </h3>
                <div className="dash-log-form">
                  <div className="dash-form-group">
                    <label>Domínio</label>
                    {domainsLoading ? (
                      <select disabled><option>Carregando...</option></select>
                    ) : (
                      <select
                        value={logForm.subject}
                        onChange={(e) => setLogForm({ ...logForm, subject: e.target.value })}
                      >
                        {domains.map(({ domain }, i) => (
                          <option key={domain.id} value={domain.id}>{domain.name}</option>
                        ))}
                      </select>
                    )}
                  </div>
                  <div className="dash-form-group">
                    <label>Horas</label>
                    <input
                      type="number"
                      min="0.5" step="0.5"
                      value={logForm.hours}
                      onChange={(e) => setLogForm({ ...logForm, hours: e.target.value })}
                    />
                  </div>
                  <div className="dash-form-group">
                    <label>Questões</label>
                    <input
                      type="number" min="0"
                      value={logForm.questions}
                      onChange={(e) => setLogForm({ ...logForm, questions: e.target.value })}
                    />
                  </div>
                  <div className="dash-form-group">
                    <label>Acertos</label>
                    <input
                      type="number" min="0"
                      value={logForm.correct}
                      onChange={(e) => setLogForm({ ...logForm, correct: e.target.value })}
                    />
                  </div>
                  <button onClick={logStudy} className="dash-btn-primary" disabled={domainsLoading || domains.length === 0}>
                    Registrar
                  </button>
                </div>
              </div>
            </section>
          )}

          {activeMenu === 'materias' && (
            <section className="dash-section active">
              <h2 className="dash-section-title justify-center">
                <span className="dash-title-icon">📚</span>
                Progresso por Domínio
              </h2>

              {domainsLoading ? (
                <p style={{ color: 'var(--dash-text-secondary)', textAlign: 'center', paddingTop: 80 }}>Carregando domínios...</p>
              ) : domains.length === 0 ? (
                <div style={{ textAlign: 'center', paddingTop: 80 }}>
                  <p style={{ fontSize: 48, marginBottom: 16 }}>⚡</p>
                  <p style={{ color: 'var(--dash-text-secondary)', fontSize: 16, marginBottom: 8 }}>Nenhum domínio criado ainda.</p>
                  <p style={{ color: 'var(--dash-text-secondary)', fontSize: 13 }}>Crie domínios na página de Domínios para acompanhar seu progresso aqui.</p>
                </div>
              ) : (
                <div className="dash-materias-grid">
                  {domains.map(({ domain }, index) => {
                    const data = studyData[domain.id] || { hours: 0, questions: 0, correct: 0, progress: 0 };
                    const accuracy = data.questions > 0 ? Math.round((data.correct / data.questions) * 100) : 0;
                    const icon = DOMAIN_ICONS[index % DOMAIN_ICONS.length];

                    return (
                      <div className="dash-materia-card" key={domain.id}>
                        <div className="dash-materia-icon">{icon}</div>
                        <h3>{domain.name}</h3>
                        <div className="dash-materia-stats">
                          <div className="dash-materia-stat">
                            <span className="dash-stat-num">{data.hours.toFixed(1)}</span>
                            <span className="dash-stat-txt">horas</span>
                          </div>
                          <div className="dash-materia-stat">
                            <span className="dash-stat-num">{data.questions}</span>
                            <span className="dash-stat-txt">questões</span>
                          </div>
                          <div className="dash-materia-stat">
                            <span className="dash-stat-num">{accuracy}%</span>
                            <span className="dash-stat-txt">acerto</span>
                          </div>
                        </div>
                        <div className="dash-materia-progress">
                          <div className="dash-progress-fill" style={{ width: `${data.progress}%` }}></div>
                        </div>
                        <input
                          type="range"
                          min="0" max="100"
                          value={data.progress}
                          className="dash-progress-slider"
                          onChange={(e) => handleStudyProgressChange(domain.id, e.target.value)}
                        />
                      </div>
                    );
                  })}
                </div>
              )}
            </section>
          )}

        </main>
      </div>
    </div>
  );
}
