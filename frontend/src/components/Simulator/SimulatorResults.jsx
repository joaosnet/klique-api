
import { useTranslation } from 'react-i18next';
import EntityCard from './EntityCard';

function computeMatch(p1, p2, t) {
  if (p1.strategy === 'withdraw' || p2.strategy === 'withdraw') {
    return { type: 'neutral', synergyDelta: 0, msg: t('simulatorResults.match_isolation') };
  }
  if (p1.strategy === 'cooperate' && p2.strategy === 'cooperate') {
    return { type: 'win', synergyDelta: 2, msg: t('simulatorResults.match_synergy') };
  }
  if (p1.strategy === 'defect' && p2.strategy === 'defect') {
    return { type: 'lose', synergyDelta: -2, msg: t('simulatorResults.match_war') };
  }
  const exploiter = p1.strategy === 'defect' ? p1.name : p2.name;
  const victim = p1.strategy === 'cooperate' ? p1.name : p2.name;
  return {
    type: 'exploit',
    synergyDelta: -1,
    msg: t('simulatorResults.match_exploit', { exploiter, victim }),
  };
}

const TYPE_STYLE = {
  win: { border: 'border-blue-800', tag: 'bg-blue-900 text-blue-400 border-blue-500', label: 'simulatorResults.match_win' },
  lose: { border: 'border-red-800', tag: 'bg-red-900 text-red-400 border-red-500', label: 'simulatorResults.match_lose' },
  exploit: { border: 'border-orange-800', tag: 'bg-orange-900 text-orange-400 border-orange-500', label: 'simulatorResults.match_exploit_label' },
  neutral: { border: 'border-gray-700', tag: 'bg-gray-800 text-gray-400 border-gray-600', label: 'simulatorResults.match_neutral' },
};


export default function SimulatorResults({ population, onReset }) {
  const { t } = useTranslation();
  // Build matches via round-robin shuffle
  // eslint-disable-next-line react-hooks/purity
  const pool = [...population].sort(() => Math.random() - 0.5);
  const matches = [];
  let totalSynergy = 0;
  let matchCount = 0;

  const poolCopy = [...pool];
  while (poolCopy.length >= 2) {
    const p1 = poolCopy.pop();
    const p2 = poolCopy.pop();
    const result = computeMatch(p1, p2, t);
    totalSynergy += result.synergyDelta;
    matchCount++;
    matches.push({ p1, p2, ...result });
  }
  if (poolCopy.length === 1) {
    matches.push({ p1: poolCopy[0], p2: null, type: 'neutral', msg: t('simulatorResults.match_no_pair') });
  }

  const avgSynergy = matchCount > 0 ? totalSynergy / matchCount : 0;
  const synergyScore = Math.round(((avgSynergy + 2) / 4) * 100);

  const scoreColor = synergyScore >= 70 ? '#60a5fa' : synergyScore >= 40 ? '#facc15' : '#ef4444';
  const scoreLabel =
    synergyScore >= 70 ? t('simulatorResults.ecosystem_prosperous') :
      synergyScore >= 40 ? t('simulatorResults.environment_unstable') :
        t('simulatorResults.system_collapse');

  return (
    <div className="flex flex-col h-full">
      {/* Header / HUD */}
      <div className="flex items-center justify-between mb-4 flex-shrink-0 pb-3"
        style={{ borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
        <div>
          <h2 className="font-title text-xl text-yellow-500 tracking-wider">{t('simulatorResults.title')}</h2>
          <p className="text-xs text-gray-400 uppercase tracking-widest mt-0.5">
            {t('simulatorResults.matches_simulated', { count: matches.length })}
          </p>
        </div>

        <div className="text-center">
          <div className="font-title text-3xl" style={{ color: scoreColor }}>{synergyScore}%</div>
          <div className="text-xs mt-0.5" style={{ color: scoreColor }}>{scoreLabel}</div>
        </div>

        <button
          onClick={onReset}
          className="px-4 py-2 rounded-lg text-xs uppercase tracking-wider text-gray-300 hover:text-white hover:bg-gray-800 transition-colors flex-shrink-0"
          style={{ border: '1px solid rgba(255,255,255,0.1)' }}
        >
          ← {t('simulatorResults.back')}
        </button>
      </div>

      {/* Score explanation */}
      <div
        className="rounded-xl p-4 mb-4 flex-shrink-0"
        style={{ background: `${scoreColor}10`, border: `1px solid ${scoreColor}40` }}
      >
        <p className="text-xs text-gray-300 leading-relaxed">
          <span className="font-bold" style={{ color: scoreColor }}>{t('simulatorResults.synergy_index', { score: synergyScore })}</span>
          {' — '}{t('simulatorResults.score_explanation')}
        </p>
      </div>

      {/* Matches grid */}
      <div className="flex-1 overflow-y-auto no-scrollbar space-y-4 pb-4">
        {matches.map((res, i) => {
          const s = TYPE_STYLE[res.type];
          return (
            <div
              key={i}
              className={`rounded-xl p-3 relative shadow-lg border ${s.border}`}
              style={{ background: 'rgba(17,24,39,0.5)' }}
            >
              {/* Match tag */}
              <div
                className={`absolute top-[-10px] left-1/2 -translate-x-1/2 ${s.tag} text-[10px] px-3 py-0.5 rounded-full border uppercase tracking-widest z-10 font-bold whitespace-nowrap`}
              >
                {t('simulatorResults.match_label', { number: i + 1 })}: {t(s.label)}
              </div>

              <div className="flex justify-center items-center gap-3 mt-2">
                <EntityCard entity={res.p1} showDelete={false} small />

                <div className="flex flex-col items-center">
                  <div
                    className="w-8 h-8 rounded-full flex items-center justify-center shadow-lg"
                    style={{ background: '#000', border: '2px solid #a855f7', boxShadow: '0 0 10px rgba(168,85,247,0.5)' }}
                  >
                    <span className="font-title text-xs text-purple-400">VS</span>
                  </div>
                </div>

                {res.p2 ? (
                  <EntityCard entity={res.p2} showDelete={false} small />
                ) : (
                  <div
                    className="w-32 rounded-lg flex items-center justify-center text-gray-600 font-bold uppercase text-xs"
                    style={{ aspectRatio: '2.5/3.5', border: '2px dashed rgba(75,85,99,0.5)' }}
                  >
                    {t('simulatorResults.empty')}
                  </div>
                )}
              </div>

              <p className="text-center text-xs text-gray-300 mt-3 px-4 font-bold leading-relaxed">
                {res.msg}
              </p>
            </div>
          );
        })}
      </div>

      {/* Reset button */}
      <div className="flex-shrink-0 pt-4">
        <button
          onClick={onReset}
          className="w-full py-3 rounded-xl font-title tracking-widest text-sm uppercase text-white transition-all hover:opacity-90"
          style={{ background: 'linear-gradient(135deg, #374151, #4b5563)' }}
        >
          {t('simulatorResults.play_again')}
        </button>
      </div>
    </div>
  );
}
