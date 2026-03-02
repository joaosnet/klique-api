import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authAPI } from '../services/api';
import { getErrorMessage } from '../utils/errorHandler';
import { IconCameraShot, IconSparkBoost } from '../components/Icons/ActionIcons';

// ── Step 1: Basic Data ───────────────────────────────────────────────────────
function StepBasicData({ data, onChange, onNext }) {
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [usePasskey, setUsePasskey] = useState(false);
  const { login, registerPasskey, loginWithGoogle } = useAuth();

  const handleGoogleLogin = async () => {
    setError('');
    setLoading(true);
    try {
      // Mock token for demo, similar to LoginPage
      alert("Google Login placeholder - Irá criar a conta e pular o passo 1.");
      // await loginWithGoogle("google-token");
      // onNext();
    } catch (err) {
      setError("Erro no cadastro com Google");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!usePasskey && data.password.length < 6) {
      setError('A senha deve ter pelo menos 6 caracteres.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      let finalPassword = data.password;
      if (usePasskey) {
        const array = new Uint8Array(16);
        window.crypto.getRandomValues(array);
        finalPassword = Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
      }

      await authAPI.register(data.name, data.email, finalPassword);
      await login(data.email, finalPassword);

      if (usePasskey) {
        try {
          await registerPasskey();
        } catch (pkErr) {
          console.warn('Registro de passkey cancelado ou falhou, continuando com a conta criada.');
        }
      }

      onNext();
    } catch (err) {
      setError(getErrorMessage(err, 'Erro ao cadastrar. Tente novamente.'));
    } finally {
      setLoading(false);
    }
  };

  const inputStyle = {
    background: 'var(--bg-card-inner)',
    border: '1px solid var(--border-color)',
    color: 'var(--text-main)',
  };

  return (
    <div className="space-y-6">
      {/* Social Buttons */}
      <div className="grid grid-cols-2 gap-3">
        <button
          type="button"
          onClick={handleGoogleLogin}
          className="flex items-center justify-center gap-2 py-2.5 rounded-lg text-xs font-semibold transition-all"
          style={{
            color: 'var(--text-main)',
            border: '1px solid var(--border-color)',
            background: 'transparent',
          }}
        >
          <img src="https://www.google.com/favicon.ico" className="w-4 h-4" alt="Google" />
          Google
        </button>
        <button
          type="button"
          className="flex items-center justify-center gap-2 py-2.5 rounded-lg text-xs font-semibold transition-all"
          style={{
            color: 'var(--text-main)',
            border: '1px solid var(--border-color)',
            background: 'transparent',
          }}
        >
          <span className="text-lg"></span>
          Apple
        </button>
      </div>

      <div className="relative">
        <div className="absolute inset-0 flex items-center"><div className="w-full border-t" style={{ borderColor: 'var(--border-color)' }}></div></div>
        <div className="relative flex justify-center text-xs uppercase"><span className="px-2 tracking-tighter" style={{ background: 'var(--bg-card)', color: 'var(--text-muted)' }}>ou use seu email</span></div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {['name', 'email'].map((field) => (
          <div key={field}>
            <label className="block text-[10px] uppercase tracking-widest mb-1.5 ml-1" style={{ color: 'var(--text-muted)' }}>
              {field === 'name' ? 'Nome' : 'Email'}
            </label>
            <input
              type={field === 'name' ? 'text' : 'email'}
              value={data[field]}
              onChange={(e) => onChange(field, e.target.value)}
              placeholder={field === 'email' ? 'seu@email.com' : 'Seu nome'}
              required
              className="w-full rounded-lg px-4 py-3 text-sm placeholder-gray-500 outline-none focus:ring-1 ring-purple-500"
              style={inputStyle}
            />
          </div>
        ))}

        {!usePasskey && (
          <div>
            <label className="block text-[10px] uppercase tracking-widest mb-1.5 ml-1" style={{ color: 'var(--text-muted)' }}>Senha</label>
            <input
              type="password"
              value={data.password}
              onChange={(e) => onChange('password', e.target.value)}
              placeholder="Mínimo 6 caracteres"
              required={!usePasskey}
              className="w-full rounded-lg px-4 py-3 text-sm placeholder-gray-500 outline-none focus:ring-1 ring-purple-500"
              style={inputStyle}
            />
          </div>
        )}

        <div className="flex items-center justify-between p-3 rounded-lg mt-2" style={{ background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.2)' }}>
          <div>
            <span className="block text-sm text-orange-400 font-semibold mb-0.5">Criar Passkey (Biometria)</span>
            <span className="block text-xs text-orange-200/70">Login sem senha, mais rápido e seguro.</span>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input type="checkbox" checked={usePasskey} onChange={(e) => setUsePasskey(e.target.checked)} className="sr-only peer" />
            <div className="w-11 h-6 bg-orange-900/50 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-orange-500"></div>
          </label>
        </div>

        {error && (
          <p className="text-sm rounded-lg px-4 py-3 mt-4" style={{ background: 'rgba(239,68,68,0.1)', color: '#fca5a5', border: '1px solid rgba(239,68,68,0.3)' }}>
            {error}
          </p>
        )}
        <button
          type="submit"
          disabled={loading}
          className="w-full mt-6 py-3 rounded-lg font-title tracking-widest text-sm uppercase text-white transition-all hover:opacity-90 disabled:opacity-50"
          style={{ background: 'linear-gradient(135deg, #7c3aed, #a855f7)' }}
        >
          {loading ? 'Aguarde...' : 'Criar Conta & Continuar →'}
        </button>
      </form>
    </div>
  );
}

// ── Step 2: Prisoner's Dilemma ────────────────────────────────────────────────
const OUTCOMES = {
  cooperate: {
    cooperate: {
      you: '+3', other: '+3', label: 'Ganho Mútuo', color: '#22c55e',
      desc: 'Quando dois cooperam, o sistema prospera. Ótimo de Pareto — mas não Equilíbrio de Nash.'
    },
    defect: {
      you: '-1', other: '+5', label: 'Você foi explorado', color: '#ef4444',
      desc: 'Você cooperou e foi traído. O traidor leva tudo, você fica com o prejuízo.'
    },
  },
  defect: {
    cooperate: {
      you: '+5', other: '-1', label: 'Você explorou', color: '#f59e0b',
      desc: 'Você traiu quem confiava. Lucrativo no curto prazo, destrutivo no longo.'
    },
    defect: {
      you: '+1', other: '+1', label: 'Guerra de Atrito', color: '#ef4444',
      desc: 'Ambos desconfiam, ambos perdem pouco. Este é o Equilíbrio de Nash.'
    },
  },
  isolate: {
    cooperate: {
      you: '0', other: '0', label: 'Isolamento', color: '#6b7280',
      desc: 'Você se isolou. Seguro, mas sem crescimento.'
    },
    defect: {
      you: '0', other: '0', label: 'Isolamento', color: '#6b7280',
      desc: 'Você se isolou. Não foi explorado, mas ficou parado.'
    },
  },
};

function StepPrisonersDilemma({ onNext }) {
  const [chosen, setChosen] = useState(null);
  const [revealed, setRevealed] = useState(false);
  const [cpuChoice] = useState(() => (Math.random() > 0.4 ? 'cooperate' : 'defect'));

  const outcome = chosen ? OUTCOMES[chosen][cpuChoice] : null;

  return (
    <div>
      <p className="text-sm mb-6 leading-relaxed" style={{ color: 'var(--text-muted)' }}>
        Você e um estranho estão presos. Cada um decide{' '}
        <strong style={{ color: 'var(--text-main)' }}>sem saber a escolha do outro</strong>.
      </p>

      {!revealed ? (
        <div className="space-y-3">
          {[
            { key: 'cooperate', label: 'COLABORAR', desc: 'Confio no outro. Juntos podemos ganhar.', color: '#22c55e' },
            { key: 'defect', label: 'EXPLORAR', desc: 'Vou trair. Maximizo meu ganho individual.', color: '#ef4444' },
            { key: 'isolate', label: 'ISOLAR', desc: 'Me retiro. Não arrisquei, não ganhei.', color: '#6b7280' },
          ].map(({ key, label, desc, color }) => (
            <button
              key={key}
              onClick={() => { setChosen(key); setRevealed(true); }}
              className="w-full rounded-xl p-4 text-left transition-all hover:scale-[1.01]"
              style={{ border: `1px solid ${color}40`, background: `${color}10` }}
            >
              <div className="font-title tracking-widest text-sm" style={{ color }}>{label}</div>
              <div className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>{desc}</div>
            </button>
          ))}
        </div>
      ) : (
        <div className="space-y-4 fade-in">
          <div className="rounded-xl p-5" style={{ border: `1px solid ${outcome.color}40`, background: `${outcome.color}10` }}>
            <div className="flex justify-between items-center mb-3">
              <div className="text-center">
                <div className="text-xs uppercase tracking-wider mb-1" style={{ color: 'var(--text-muted)' }}>Você</div>
                <div className="font-title text-sm" style={{ color: outcome.color }}>
                  {chosen === 'cooperate' ? 'COLABORAR' : chosen === 'defect' ? 'EXPLORAR' : 'ISOLAR'}
                </div>
                <div className="font-title text-3xl mt-1" style={{ color: 'var(--text-main)' }}>{outcome.you}</div>
              </div>
              <div className="font-title text-2xl" style={{ color: 'var(--text-muted)' }}>VS</div>
              <div className="text-center">
                <div className="text-xs uppercase tracking-wider mb-1" style={{ color: 'var(--text-muted)' }}>CPU</div>
                <div className="font-title text-sm" style={{ color: 'var(--text-main)' }}>
                  {cpuChoice === 'cooperate' ? 'COLABORAR' : 'EXPLORAR'}
                </div>
                <div className="font-title text-3xl mt-1" style={{ color: 'var(--text-main)' }}>{outcome.other}</div>
              </div>
            </div>
            <div className="border-t pt-3" style={{ borderColor: `${outcome.color}30` }}>
              <div className="font-semibold text-sm mb-1" style={{ color: outcome.color }}>{outcome.label}</div>
              <p className="text-xs leading-relaxed" style={{ color: 'var(--text-muted)' }}>{outcome.desc}</p>
            </div>
          </div>
          <div className="rounded-lg p-4 text-xs"
            style={{ background: 'rgba(168,85,247,0.08)', border: '1px solid rgba(168,85,247,0.2)' }}>
            <span className="text-purple-300 font-semibold">Nash Equilibrium:</span>{' '}
            <span style={{ color: 'var(--text-muted)' }}>
            Quando ambos exploram — ninguém tem incentivo de mudar sozinho, mesmo que cooperar fosse melhor para todos.
            </span>
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
  { id: 'style', q: 'No conflito, você tende a...', opts: ['Cooperar primeiro, retaliar se traído', 'Atacar antes de ser atacado', 'Observar e esperar o momento certo'] },
  { id: 'strength', q: 'Sua maior força estratégica é...', opts: ['Construir alianças duradouras', 'Antecipar movimentos do adversário', 'Adaptar-se rapidamente a mudanças'] },
  { id: 'betrayal', q: 'Quando alguém te trai você...', opts: ['Respondo com força proporcional', 'Corto qualquer relação futura', 'Espero a oportunidade de virar o jogo'] },
  { id: 'resource', q: 'Você prioriza recursos ou influência?', opts: ['Recursos — capital é poder real', 'Influência — quem controla narrativas, vence', 'Equilíbrio entre os dois'] },
  { id: 'horizon', q: 'Seu horizonte de planejamento é...', opts: ['Próximas 72 horas (tático)', 'Próximo ano (estratégico)', 'Próxima década (geopolítico)'] },
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
        <label className="block text-xs uppercase tracking-widest mb-2" style={{ color: 'var(--text-muted)' }}>
          Foto (opcional)
        </label>
        <div className="image-upload-wrapper"
          style={photoBase64 ? { backgroundImage: `url(${photoBase64})` } : {}}>
          <input type="file" accept="image/*" onChange={handlePhoto} />
          {!photoBase64 && (
            <div className="text-center pointer-events-none">
              <div className="text-2xl mb-1" style={{ display: 'flex', justifyContent: 'center' }}><IconCameraShot width={24} height={24} /></div>
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Clique para adicionar foto</p>
            </div>
          )}
        </div>
      </div>

      {AI_QUESTIONS.map((q) => (
        <div key={q.id}>
          <p className="text-sm mb-2" style={{ color: 'var(--text-main)' }}>{q.q}</p>
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
                    : { background: 'var(--bg-card-inner)', border: '1px solid var(--border-color)', color: 'var(--text-muted)' }
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
  'Cooperar primeiro, retaliar se traído': { name: 'TIT-FOR-TAT', color: '#22c55e' },
  'Atacar antes de ser atacado': { name: 'FIRST-STRIKE', color: '#ef4444' },
  'Observar e esperar o momento certo': { name: 'PATIENT HAWK', color: '#f59e0b' },
};

function StepFinalCard({ name, cardData, onFinish }) {
  const strat = STRATEGY_MAP[cardData?.answers?.style] || { name: 'ESTRATEGISTA', color: '#a855f7' };
  const photo = cardData?.photoBase64;

  return (
    <div className="flex flex-col items-center gap-6">
      <p className="text-sm text-center" style={{ color: 'var(--text-muted)' }}>
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
                <IconSparkBoost width={44} height={44} />
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
        style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)' }}>
        <h3 className="font-title text-sm tracking-widest" style={{ color: 'var(--text-main)' }}>STATS INICIAIS</h3>
        {[
          { label: 'Poder', value: 50, color: '#ef4444' },
          { label: 'Recursos', value: 50, color: '#f59e0b' },
          { label: 'Influência', value: 50, color: '#a855f7' },
        ].map(({ label, value, color }) => (
          <div key={label}>
            <div className="flex justify-between text-xs mb-1" style={{ color: 'var(--text-muted)' }}>
              <span className="uppercase tracking-wider">{label}</span>
              <span className="font-bold" style={{ color: 'var(--text-main)' }}>{value}</span>
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
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}><IconSparkBoost width={16} height={16} /> Entrar no Simulador</span>
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
                : { background: 'var(--bg-card-inner)', color: 'var(--text-muted)', border: '1px solid var(--border-color)' }
            }
          >
            {current > s.n ? '✓' : s.n}
          </div>
          <span className="text-xs ml-1 hidden sm:block flex-shrink-0 mr-1" style={{ color: current >= s.n ? 'var(--text-main)' : 'var(--text-muted)' }}>
            {s.label}
          </span>
          {i < STEPS_META.length - 1 && (
            <div className="flex-1 h-px mx-2" style={{ background: current > s.n ? '#a855f7' : 'var(--border-color)' }} />
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
    1: { title: 'CRIAR CONTA', sub: 'Comece sua jornada estratégica.' },
    2: { title: 'TUTORIAL', sub: 'Aprenda o Dilema do Prisioneiro na prática.' },
    3: { title: 'SEU CARD', sub: 'Responda 5 perguntas para gerar sua carta.' },
    4: { title: 'PRONTO!', sub: 'Seu card de batalha foi gerado.' },
  };

  const { title, sub } = STEP_TITLES[step];

  return (
    <div
      className="flex items-start justify-center px-4"
      style={{
        minHeight: '100dvh',
        paddingTop: '2.5rem',
        paddingBottom: 'calc(2.5rem + env(safe-area-inset-bottom))',
        background:
          'linear-gradient(135deg, var(--bg-app) 0%, var(--bg-card) 45%, color-mix(in srgb, var(--accent-dark) 55%, var(--bg-app) 45%) 100%)',
        color: 'var(--text-main)',
        transition: 'background-color 0.3s ease, color 0.3s ease',
      }}
    >
      <div className="w-full max-w-lg">
        <div className="text-center mb-8">
          <Link to="/" className="font-title text-xl tracking-widest text-purple-400">
            OMNIFLASH
          </Link>
        </div>

        <div className="rounded-2xl p-6 sm:p-8"
          style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)' }}>
          <StepperHeader current={step} />

          <h1 className="font-title text-2xl tracking-wider mb-1" style={{ color: 'var(--text-main)' }}>{title}</h1>
          <p className="text-sm mb-6" style={{ color: 'var(--text-muted)' }}>{sub}</p>

          {step === 1 && <StepBasicData data={formData} onChange={handleChange} onNext={() => setStep(2)} />}
          {step === 2 && <StepPrisonersDilemma onNext={() => setStep(3)} />}
          {step === 3 && <StepBattleCardCreator onNext={(d) => { setCardData(d); setStep(4); }} />}
          {step === 4 && <StepFinalCard name={formData.name} cardData={cardData} onFinish={() => navigate('/simulador')} />}
        </div>

        {step === 1 && (
          <p className="text-center text-sm mt-4" style={{ color: 'var(--text-muted)' }}>
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
