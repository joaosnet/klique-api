import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { oracleAPI } from '../services/api';
import GamifiedLoader from '../components/Layout/GamifiedLoader';

function StatCard({ label, value, color, suffix = '' }) {
  return (
    <div style={{
      background: '#1a1a2e', border: '1px solid #2d2d44', borderRadius: 12,
      padding: '1.25rem', flex: 1, minWidth: 120,
    }}>
      <div style={{ color: '#6b7280', fontSize: 10, letterSpacing: 1, textTransform: 'uppercase', marginBottom: 8 }}>{label}</div>
      <div style={{ color: color || '#e9d5ff', fontSize: 32, fontWeight: 800 }}>{value}{suffix}</div>
    </div>
  );
}

function RadarChart({ entries }) {
  if (!entries || entries.length === 0) return null;

  const SIZE = 220;
  const CENTER = SIZE / 2;
  const MAX_R = 80;
  const count = entries.length;

  const angleStep = (2 * Math.PI) / count;
  const getPoint = (i, r) => {
    const angle = -Math.PI / 2 + i * angleStep;
    return {
      x: CENTER + r * Math.cos(angle),
      y: CENTER + r * Math.sin(angle),
    };
  };

  // Grid circles
  const gridLevels = [0.25, 0.5, 0.75, 1.0];

  // Data polygon
  const dataPoints = entries.map((e, i) => getPoint(i, e.accuracy * MAX_R));
  const dataPath = dataPoints.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ') + ' Z';

  return (
    <div style={{ display: 'flex', justifyContent: 'center', position: 'relative' }}>
      <svg width={SIZE} height={SIZE} viewBox={`0 0 ${SIZE} ${SIZE}`}>
        {/* Grid */}
        {gridLevels.map((level) => {
          const pts = Array.from({ length: count }, (_, i) => getPoint(i, level * MAX_R));
          const path = pts.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ') + ' Z';
          return <path key={level} d={path} fill="none" stroke="#2d2d44" strokeWidth="1" />;
        })}
        {/* Spokes */}
        {Array.from({ length: count }, (_, i) => {
          const outer = getPoint(i, MAX_R);
          return <line key={i} x1={CENTER} y1={CENTER} x2={outer.x} y2={outer.y} stroke="#2d2d44" strokeWidth="1" />;
        })}
        {/* Data area */}
        <path d={dataPath} fill="#7c3aed33" stroke="#7c3aed" strokeWidth="2" />
        {/* Data points */}
        {dataPoints.map((p, i) => (
          <circle key={i} cx={p.x} cy={p.y} r="4" fill="#7c3aed" />
        ))}
        {/* Labels */}
        {entries.map((e, i) => {
          const labelR = MAX_R + 22;
          const pt = getPoint(i, labelR);
          return (
            <text
              key={i}
              x={pt.x}
              y={pt.y}
              textAnchor="middle"
              dominantBaseline="middle"
              fill="#9ca3af"
              fontSize="9"
            >
              {e.domain_name.length > 12 ? e.domain_name.slice(0, 11) + '…' : e.domain_name}
            </text>
          );
        })}
      </svg>
    </div>
  );
}

function ActivityBar({ entries }) {
  if (!entries || entries.length === 0) return null;
  const maxCount = Math.max(...entries.map((e) => e.count), 1);

  return (
    <div style={{ display: 'flex', gap: 6, alignItems: 'flex-end', height: 80 }}>
      {entries.map((entry) => {
        const heightPct = (entry.count / maxCount) * 100;
        const day = entry.date.slice(5);
        return (
          <div key={entry.date} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
            <div
              style={{
                width: '100%', borderRadius: '3px 3px 0 0',
                background: entry.count > 0 ? '#7c3aed' : '#1f2937',
                height: `${heightPct}%`, minHeight: 4,
                transition: 'height 0.5s ease',
              }}
            />
            <span style={{ color: '#6b7280', fontSize: 9 }}>{day}</span>
          </div>
        );
      })}
    </div>
  );
}

export default function OracleDashboardPage() {
  const navigate = useNavigate();
  const [overview, setOverview] = useState(null);
  const [radar, setRadar] = useState([]);
  const [activity, setActivity] = useState([]);
  const [loading, setLoading] = useState(true);
    const { t } = useTranslation();

  useEffect(() => {
    const load = async () => {
      try {
        const [ov, rd, ac] = await Promise.all([
          oracleAPI.getDashboard(),
          oracleAPI.getRadar(),
          oracleAPI.getActivity(),
        ]);
        setOverview(ov);
        setRadar(rd);
        setActivity(ac);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) {
    return <GamifiedLoader label={t('oracle.loading')} />;
  }

  return (
    <div style={{ minHeight: 'calc(100vh - 56px)', background: '#12121a', padding: '2rem 1rem' }}>
      <div style={{ maxWidth: 900, margin: '0 auto' }}>
        {/* Header */}
        <div style={{ marginBottom: '2rem' }}>
          <h1 style={{ color: '#e9d5ff', fontSize: 24, fontWeight: 800, letterSpacing: 3, textTransform: 'uppercase', margin: 0 }}>
            {t('oracle.title')}
          </h1>
          <p style={{ color: '#6b7280', fontSize: 13, marginTop: 4 }}>
            {t('oracle.subtitle')}
          </p>
        </div>

        {/* Stats row */}
        {overview && (
          <div style={{ display: 'flex', gap: 12, marginBottom: '2rem', flexWrap: 'wrap' }}>
            <StatCard label={t('oracle.stats.domains')} value={overview.total_domains} color="#a78bfa" />
            <StatCard label={t('oracle.stats.total_cards')} value={overview.total_cards} color="#7c3aed" />
            <StatCard label={t('oracle.stats.due_today')} value={overview.due_today} color={overview.due_today > 0 ? '#f59e0b' : '#6b7280'} />
            <StatCard label={t('oracle.stats.week')} value={overview.weekly_trained} color="#22c55e" suffix={t('oracle.stats.trainings_suffix')} />
            <StatCard label={t('oracle.stats.streak')} value={overview.streak_days} color="#f97316" suffix={t('oracle.stats.days_suffix')} />
          </div>
        )}

        {/* Action button */}
        {overview?.due_today > 0 && (
          <button
            onClick={() => navigate('/treinar')}
            style={{
              display: 'block', width: '100%', padding: '13px 0', borderRadius: 10,
              background: '#7c3aed', color: '#fff', border: 'none', cursor: 'pointer',
              fontSize: 14, fontWeight: 800, letterSpacing: 2, textTransform: 'uppercase',
              marginBottom: '2rem',
            }}
          >
            {t('oracle.analyze', { count: overview.due_today })}
          </button>
        )}

        {/* Charts row */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
          {/* Radar */}
          <div style={{ background: '#1a1a2e', border: '1px solid #2d2d44', borderRadius: 12, padding: '1.25rem' }}>
            <h3 style={{ color: '#e9d5ff', fontSize: 14, fontWeight: 700, letterSpacing: 1, textTransform: 'uppercase', marginBottom: 16, margin: '0 0 1rem 0' }}>
              {t('oracle.radar')}
            </h3>
            {radar.length > 0 ? (
              <RadarChart entries={radar} />
            ) : (
              <p style={{ color: '#4b5563', fontSize: 13, textAlign: 'center', padding: '2rem 0' }}>
                {t('oracle.no_data')}
              </p>
            )}
          </div>

          {/* Activity */}
          <div style={{ background: '#1a1a2e', border: '1px solid #2d2d44', borderRadius: 12, padding: '1.25rem' }}>
            <h3 style={{ color: '#e9d5ff', fontSize: 14, fontWeight: 700, letterSpacing: 1, textTransform: 'uppercase', margin: '0 0 1rem 0' }}>
              {t('oracle.activity_7days')}
            </h3>
            {activity.some((e) => e.count > 0) ? (
              <ActivityBar entries={activity} />
            ) : (
              <p style={{ color: '#4b5563', fontSize: 13, textAlign: 'center', padding: '2rem 0' }}>
                {t('oracle.no_activity')}
              </p>
            )}
          </div>

          {/* Per-domain table */}
          {radar.length > 0 && (
            <div style={{ background: '#1a1a2e', border: '1px solid #2d2d44', borderRadius: 12, padding: '1.25rem', gridColumn: '1 / -1' }}>
              <h3 style={{ color: '#e9d5ff', fontSize: 14, fontWeight: 700, letterSpacing: 1, textTransform: 'uppercase', margin: '0 0 1rem 0' }}>
                {t('oracle.per_domain')}
              </h3>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid #2d2d44' }}>
                      {['Domínio', 'Treinos', 'Precisão', ''].map((h) => (
                        <th key={h} style={{ color: '#6b7280', fontSize: 10, letterSpacing: 1, textTransform: 'uppercase', padding: '0 8px 8px', textAlign: 'left' }}>
                          {h === 'Domínio' ? t('oracle.domain') : h === 'Treinos' ? t('oracle.trainings') : h === 'Precisão' ? t('oracle.accuracy') : ''}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {radar.map((r) => (
                      <tr key={r.domain_id} style={{ borderBottom: '1px solid #1f2937' }}>
                        <td style={{ color: '#d1d5db', padding: '8px', fontWeight: 600 }}>{r.domain_name}</td>
                        <td style={{ color: '#9ca3af', padding: '8px' }}>{r.trained_count}</td>
                        <td style={{ color: '#22c55e', padding: '8px', fontWeight: 700 }}>
                          {r.trained_count > 0 ? `${Math.round(r.accuracy * 100)}%` : '—'}
                        </td>
                        <td style={{ padding: '8px' }}>
                          <button
                            onClick={() => navigate(`/criar/${r.domain_id}`)}
                            style={{
                              background: 'none', border: '1px solid #374151', borderRadius: 4,
                              color: '#7c3aed', cursor: 'pointer', fontSize: 11, padding: '3px 8px',
                            }}
                          >
                            {t('oracle.add_cards')}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
