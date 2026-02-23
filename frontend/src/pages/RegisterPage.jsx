import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authAPI } from '../services/api';

// ── Step 1: Basic Data ───────────────────────────────────────────────────────
function StepBasicData({ data, onChange, onNext }) {
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (data.password.length < 6) {
      setError('A senha deve ter pelo menos 6 caracteres.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      await authAPI.register(data.name, data.email, data.password);
      await login(data.email, data.password);
      onNext();
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao cadastrar. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const inputStyle = {
    background: 'rgba(255,255,255,0.05)',
    border: '1px solid rgba(255,255,255,0.1)',
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {['name', 'email', 'password'].map((field) => (
        <div key={field}>
          <label className="block text-xs uppercase tracking-widest text-gray-400 mb-2">
            {field === 'name' ? 'Nome' : field === 'email' ? 'Email' : 'Senha'}
          </label>
          <input
            type={field === 'password' ? 'password' : field === 'email' ? 'email' : 'text'}
            value={data[field]}
            onChange={(e) => onChange(field, e.target.value)}
            placeholder={field === 'email' ? 'seu@email.com' : field === 'password' ? 'Mínimo 6 caracteres' : 'Seu nome'}
            required
            className="w-full rounded-lg px-4 py-3 text-sm text-gray-100 placeholder-gray-600 outline-none"
            style={inputStyle}
          />
        </div>
      ))}
      {error && (
        <p className="text-sm rounded-lg px-3 py-2"
           style={{ background: 'rgba(239,68,68,0.1)', color: '#fca5a5', border: '1px solid rgba(239,68,68,0.3)' }}>
          {error}
        </p>
      )}
      <button
        type="submit"
        disabled={loading}
        className="w-full py-3 rounded-lg font-title tracking-widest text-sm uppercase text-white transition-all hover:opacity-90 disabled:opacity-50"
        style={{ background: 'linear-gradient(135deg, #7c3aed, #a855f7)' }}
      >
        {loading ? 'Criando conta...' : 'Criar Conta & Continuar →'}
      </button>
    </form>
  );
}

// ── Step 2: Prisoner's Dilemma ────────────────────────────────────────────────
const OUTCOMES = {
  cooperate: {
    cooperate: { you: '+3', other: '+3', label: 'Ganho Mútuo', color: '#22c55e',
      desc: 'Quando dois cooperam, o sistema prospera. Ótimo de Pareto — mas não Equilíbrio de Nash.' },
    defect:    { you: '-1', other: '+5', label: 'Você foi explorado', color: '#ef4444',
      desc: 'Você cooperou e foi traído. O traidor leva tudo, você fica com o prejuízo.' },
  },
  defect: {
    cooperate: { you: '+5', other: '-1', label: 'Você explorou', color: '#f59e0b',
      desc: 'Você traiu quem confiava. Lucrativo no curto prazo, destrutivo no longo.' },
    defect:    { you: '+1', other: '+1', label: 'Guerra de Atrito', color: '#ef4444',
      desc: 'Ambos desconfiam, ambos perdem pouco. Este é o Equilíbrio de Nash.' },
  },
  isolate: {
    cooperate: { you: '0', other: '0', label: 'Isolamento', color: '#6b7280',
      desc: 'Você se isolou. Seguro, mas sem crescimento.' },
    defect:    { you: '0', other: '0', label: 'Isolamento', color: '#6b7280',
      desc: 'Você se isolou. Não foi explorado, mas ficou parado.' },
  },
};

function StepPrisonersDilemma({ onNext }) {
  const [chosen, setChosen] = useState(null);
  const [revealed, setRevealed] = useState(false);
  const [cpuChoice] = useState(() => (Math.random() > 0.4 ? 'cooperate' : 'defect'));

  const outcome = chosen ? OUTCOMES[chosen][cpuChoice] : null;

  return (
    <div>
      <p className="text-gray-400 text-sm mb-6 leading-relaxed">
        Você e um estranho estão presos. Cada um decide{' '}
        <strong className="text-white">sem saber a escolha do outro</strong>.
      </p>

      {!revealed ? (
        <div className="space-y-3">
          {[
            { key: 'cooperate', label: 'COLABORAR', desc: 'Confio no outro. Juntos podemos ganhar.', color: '#22c55e' },
            { key: 'defect',    label: 'EXPLORAR',  desc: 'Vou trair. Maximizo meu ganho individual.', color: '#ef4444' },
            { key: 'isolate',   label: 'ISOLAR',    desc: 'Me retiro. Não arrisquei, não ganhei.', color: '#6b7280' },
          ].map(({ key, label, desc, color }) => (
            <button
              key={key}
              onClick={() => { setChosen(key); setRevealed(true); }}
              className="w-full rounded-xl p-4 text-left transition-all hover:scale-[1.01]"
              style={{ border: `1px solid ${color}40`, background: `${color}10` }}
            >
              <div className="font-title tracking-widest text-sm" style={{ color }}>{label}</div>
              <div className="text-xs text-gray-400 mt-1">{desc}</div>
            </button>
          ))}
        </div>
      ) : (
        <div className="space-y-4 fade-in">
          <div className="rounded-xl p-5" style={{ border: `1px solid ${outcome.color}40`, background: `${outcome.color}10` }}>
            <div className="flex justify-between items-center mb-3">
              <div className="text-center">
                <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">Você</div>
                <div className="font-title text-sm" style={{ color: outcome.color }}>
                  {chosen === 'cooperate' ? 'COLABORAR' : chosen === 'defect' ? 'EXPLORAR' : 'ISOLAR'}
                </div>
                <div className="font-title text-3xl text-white mt-1">{outcome.you}</div>
              </div>
              <div className="font-title text-2xl text-gray-600">VS</div>
              <div className="text-center">
                <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">CPU</div>
                <div className="font-title text-sm text-gray-300">
                  {cpuChoice === 'cooperate' ? 'COLABORAR' : 'EXPLORAR'}
                </div>
                <div className="font-title text-3xl text-white mt-1">{outcome.other}</div>
              </div>
            </div>
            <div className="border-t pt-3" style={{ borderColor: `${outcome.color}30` }}>
              <div className="font-semibold text-sm mb-1" style={{ color: outcome.color }}>{outcome.label}</div>
              <p className="text-xs text-gray-400 leading-relaxed">{outcome.desc}</p>
            </div>
          </div>
          <div className="rounded-lg p-4 text-xs text-gray-400"
               style={{ background: 'rgba(168,85,247,0.08)', border: '1px solid rgba(168,85,247,0.2)' }}>
            <span className="text-purple-300 font-semibold">Nash Equilibrium:</span>{' '}
            Quando ambos exploram — ninguém tem incentivo de mudar sozinho, mesmo que cooperar fosse melhor para todos.
          </div>
          <button
            onClick={onNext}
            className="w-full py-3 rounded-lg font-title tracking-widest text-sm uppercase text-white transition-all hover:opacity-90"
            style={{ background: 'linear-gradient(135deg, #7c3aed, #a855f7)' }}
          >
            Entendi — Criar meu Card →
          </button>
        </div>
      )}
    </div>
  );
}

// ── Step 3: Battle Card Creator ───────────────────────────────────────────────
const AI_QUESTIONS = [
  { id: 'style',    q: 'No conflito, você tende a...', opts: ['Cooperar primeiro, retaliar se traído', 'Atacar antes de ser atacado', 'Observar e esperar o momento certo'] },
  { id: 'strength', q: 'Sua maior força estratégica é...', opts: ['Construir alianças duradouras', 'Antecipar movimentos do adversário', 'Adaptar-se rapidamente a mudanças'] },
  { id: 'betrayal', q: 'Quando alguém te trai você...', opts: ['Respondo com força proporcional', 'Corto qualquer relação futura', 'Espero a oportunidade de virar o jogo'] },
  { id: 'resource', q: 'Você prioriza recursos ou influência?', opts: ['Recursos — capital é poder real', 'Influência — quem controla narrativas, vence', 'Equilíbrio entre os dois'] },
  { id: 'horizon',  q: 'Seu horizonte de planejamento é...', opts: ['Próximas 72 horas (tático)', 'Próximo ano (estratégico)', 'Próxima década (geopolítico)'] },
];

function StepBattleCardCreator({ onNext }) {
  const [answers, setAnswers] = useState({});
  const [photoBase64, setPhotoBase64] = useState(null);
  const allAnswered = AI_QUESTIONS.every((q) => answers[q.id]);

  const handlePhoto = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => setPhotoBase64(ev.target.result);
    reader.readAsDataURL(file);
  };

  return (
    <div className="space-y-5">
      <div>
        <label className="block text-xs uppercase tracking-widest text-gray-400 mb-2">
          Foto (opcional)
        </label>
        <div className="image-upload-wrapper"
             style={photoBase64 ? { backgroundImage: `url(${photoBase64})` } : {}}>
          <input type="file" accept="image/*" onChange={handlePhoto} />
          {!photoBase64 && (
            <div className="text-center pointer-events-none">
              <div className="text-2xl mb-1">📸</div>
              <p className="text-xs text-gray-500">Clique para adicionar foto</p>
            </div>
          )}
        </div>
      </div>

      {AI_QUESTIONS.map((q) => (
        <div key={q.id}>
          <p className="text-sm text-gray-300 mb-2">{q.q}</p>
          <div className="flex flex-col gap-2">
            {q.opts.map((opt) => (
              <button
                key={opt}
                type="button"
                onClick={() => setAnswers((a) => ({ ...a, [q.id]: opt }))}
                className="text-left px-4 py-2 rounded-lg text-xs transition-all"
                style={
                  answers[q.id] === opt
                    ? { background: 'rgba(168,85,247,0.2)', border: '1px solid #a855f7', color: '#e9d5ff' }
                    : { background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)', color: '#9ca3af' }
                }
              >
                {opt}
              </button>
            ))}
          </div>
        </div>
      ))}

      <button
        onClick={() => onNext({ answers, photoBase64 })}
        disabled={!allAnswered}
        className="w-full py-3 rounded-lg font-title tracking-widest text-sm uppercase text-white transition-all hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed"
        style={{ background: 'linear-gradient(135deg, #7c3aed, #a855f7)' }}
      >
        Gerar Card de Batalha →
      </button>
    </div>
  );
}

// ── Step 4: Final Card ────────────────────────────────────────────────────────
const STRATEGY_MAP = {
  'Cooperar primeiro, retaliar se traído': { name: 'TIT-FOR-TAT',  color: '#22c55e' },
  'Atacar antes de ser atacado':           { name: 'FIRST-STRIKE', color: '#ef4444' },
  'Observar e esperar o momento certo':    { name: 'PATIENT HAWK', color: '#f59e0b' },
};

function StepFinalCard({ name, cardData, onFinish }) {
  const strat = STRATEGY_MAP[cardData?.answers?.style] || { name: 'ESTRATEGISTA', color: '#a855f7' };
  const photo = cardData?.photoBase64;

  return (
    <div className="flex flex-col items-center gap-6">
      <p className="text-gray-400 text-sm text-center">
        Seu Card de Batalha foi criado. Ele aparecerá automaticamente no Simulador.
      </p>

      <div className="unmatched-card w-48 sm:w-56">
        <div className="relative w-full h-full card-inner-bg overflow-hidden flex flex-col">
          <div className="w-full relative overflow-hidden bg-gray-900 border-b-2 border-white" style={{ height: '55%' }}>
            {photo ? (
              <img src={photo} alt="avatar" className="w-full h-full object-cover absolute inset-0 opacity-90" />
            ) : (
              <div className="w-full h-full flex items-center justify-center"
                   style={{ background: 'linear-gradient(135deg, #1a0a2e, #4c1d95)' }}>
                <span className="text-5xl">⚡</span>
              </div>
            )}
            <div className="absolute inset-0 bg-gradient-to-r from-black/60 to-transparent" />
            <div className="absolute top-2 left-2 bg-purple-700 text-white font-title text-xs px-2 py-0.5 rounded">
              RANK 3
            </div>
            <div className="absolute bottom-[-10px] right-2 z-20 w-8 h-8 rounded-full bg-black border-2 border-white flex items-center justify-center shadow-lg">
              <span className="font-title text-white text-xs">150</span>
            </div>
          </div>
          <div className="w-full text-white p-2 flex flex-col bg-black" style={{ height: '45%' }}>
            <h2 className="font-title text-base tracking-wider leading-none mb-1 uppercase truncate" style={{ color: strat.color }}>
              {strat.name}
            </h2>
            <div className="border-t border-gray-700 my-1" />
            <p className="text-[10px] font-bold text-gray-200 truncate uppercase">► {name || 'Jogador'}</p>
            <p className="text-[9px] leading-tight text-gray-400 mt-1">Pod:50 | Rec:50 | Inf:50</p>
          </div>
        </div>
      </div>

      <div className="w-full rounded-xl p-5 space-y-3"
           style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(168,85,247,0.15)' }}>
        <h3 className="font-title text-sm tracking-widest text-white">STATS INICIAIS</h3>
        {[
          { label: 'Poder', value: 50, color: '#ef4444' },
          { label: 'Recursos', value: 50, color: '#f59e0b' },
          { label: 'Influência', value: 50, color: '#a855f7' },
        ].map(({ label, value, color }) => (
          <div key={label}>
            <div className="flex justify-between text-xs text-gray-400 mb-1">
              <span className="uppercase tracking-wider">{label}</span>
              <span className="font-bold text-white">{value}</span>
            </div>
            <div className="w-full h-1.5 rounded-full bg-gray-800">
              <div className="h-full rounded-full" style={{ width: `${value}%`, background: color }} />
            </div>
          </div>
        ))}
      </div>

      <button
        onClick={onFinish}
        className="w-full py-3 rounded-lg font-title tracking-widest text-sm uppercase text-white transition-all hover:scale-105 pulse-glow"
        style={{ background: 'linear-gradient(135deg, #7c3aed, #a855f7)' }}
      >
        Entrar no Simulador ⚡
      </button>
    </div>
  );
}

// ── Stepper Header ────────────────────────────────────────────────────────────
const STEPS_META = [
  { n: 1, label: 'Dados' },
  { n: 2, label: 'Tutorial' },
  { n: 3, label: 'Card' },
  { n: 4, label: 'Batalha' },
];

function StepperHeader({ current }) {
  return (
    <div className="flex items-center mb-8">
      {STEPS_META.map((s, i) => (
        <div key={s.n} className="flex items-center" style={{ flex: i < STEPS_META.length - 1 ? '1' : 'none' }}>
          <div
            className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0"
            style={
              current >= s.n
                ? { background: '#a855f7', color: '#fff' }
                : { background: 'rgba(255,255,255,0.06)', color: '#6b7280', border: '1px solid rgba(255,255,255,0.1)' }
            }
          >
            {current > s.n ? '✓' : s.n}
          </div>
          <span className={`text-xs ml-1 hidden sm:block flex-shrink-0 mr-1 ${current >= s.n ? 'text-gray-300' : 'text-gray-600'}`}>
            {s.label}
          </span>
          {i < STEPS_META.length - 1 && (
            <div className="flex-1 h-px mx-2" style={{ background: current > s.n ? '#a855f7' : 'rgba(255,255,255,0.08)' }} />
          )}
        </div>
      ))}
    </div>
  );
}

// ── Main ──────────────────────────────────────────────────────────────────────
export default function RegisterPage() {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({ name: '', email: '', password: '' });
  const [cardData, setCardData] = useState(null);
  const navigate = useNavigate();

  const handleChange = (field, value) => setFormData((d) => ({ ...d, [field]: value }));

  const STEP_TITLES = {
    1: { title: 'CRIAR CONTA',  sub: 'Comece sua jornada estratégica.' },
    2: { title: 'TUTORIAL',     sub: 'Aprenda o Dilema do Prisioneiro na prática.' },
    3: { title: 'SEU CARD',     sub: 'Responda 5 perguntas para gerar sua carta.' },
    4: { title: 'PRONTO!',      sub: 'Seu card de batalha foi gerado.' },
  };

  const { title, sub } = STEP_TITLES[step];

  return (
    <div
      className="min-h-screen flex items-start justify-center px-4 py-10"
      style={{ background: 'linear-gradient(135deg, #12121a, #1a0a2e)' }}
    >
      <div className="w-full max-w-lg">
        <div className="text-center mb-8">
          <Link to="/" className="font-title text-xl tracking-widest text-purple-400">
            GAME THEORY
          </Link>
        </div>

        <div className="rounded-2xl p-6 sm:p-8"
             style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(168,85,247,0.2)' }}>
          <StepperHeader current={step} />

          <h1 className="font-title text-2xl tracking-wider text-white mb-1">{title}</h1>
          <p className="text-gray-500 text-sm mb-6">{sub}</p>

          {step === 1 && <StepBasicData data={formData} onChange={handleChange} onNext={() => setStep(2)} />}
          {step === 2 && <StepPrisonersDilemma onNext={() => setStep(3)} />}
          {step === 3 && <StepBattleCardCreator onNext={(d) => { setCardData(d); setStep(4); }} />}
          {step === 4 && <StepFinalCard name={formData.name} cardData={cardData} onFinish={() => navigate('/simulador')} />}
        </div>

        {step === 1 && (
          <p className="text-center text-sm text-gray-500 mt-4">
            Já tem conta?{' '}
            <Link to="/login" className="text-purple-400 hover:text-purple-300 transition-colors">
              Entrar
            </Link>
          </p>
        )}
      </div>
    </div>
  );
}
