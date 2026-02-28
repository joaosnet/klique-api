import { useState } from 'react';
import { Link } from 'react-router-dom';
import GameTheoryCard from '../components/Cards/GameTheoryCard';

const DEMO_CARDS = [
  {
    id: 'demo-1',
    template_type: 'if_then',
    probability_heat_score: 72,
    scenario_context:
      'Você está a negociar um aumento salarial. O teu gestor diz que o orçamento para aumentos está "congelado este trimestre", mas você sabe que um colega acabou de ser promovido.',
    question:
      'Se o gestor usa a restrição de "budget congelado", qual é a jogada dominante que maximiza o teu payoff sem queimar a relação?',
    predicted_outcome:
      'O "budget congelado" é uma âncora de negociação, não uma restrição real. Aceitar silenciosamente sinaliza que este frame funcionou e será repetido.',
    game_theory_explanation:
      'Este é um Jogo de Barganha com Assimetria de Informação. O gestor tem incentivo em minimizar o custo salarial. A estratégia dominante é converter o jogo de 1 rodada para multi-rodada: "Entendo o constrangimento de agora. Posso propor definirmos métricas concretas para revisitar isto em Janeiro?" Isto preserva a relação, sinaliza valor e cria um compromisso público do gestor.',
  },
  {
    id: 'demo-2',
    template_type: 'black_swan',
    probability_heat_score: 88,
    scenario_context:
      'Combinaste um jantar com alguém que conheceste online. 20 minutos antes do encontro, ela cancela com "surgiu uma emergência de trabalho". Três horas depois envia uma selfie num bar com amigos.',
    question:
      'Como interpretas este sinal pela lente da Teoria dos Jogos, e qual é o próximo movimento que melhor preserva o teu Status Signal?',
    predicted_outcome:
      'O sinal indica teste de reacção ou baixo custo percebido da tua presença. Reagir imediatamente confirma alto investimento emocional e reduz o teu poder de barganha.',
    game_theory_explanation:
      'Em jogos de atracção, o valor percebido (Status Signal) é inversamente proporcional à disponibilidade aparente. O cancelamento foi um teste de Costly Signal — a selfie foi a verificação. A jogada ótima: não reages por 24–48h. Depois reinicias com um frame diferente de alto status: "Vi algo que acho que ia interessar-te — [referência específica ao que ela gosta]." Isto reposiciona-te como o agente de iniciativa, não o receptor.',
  },
  {
    id: 'demo-3',
    template_type: 'payoff_matrix',
    probability_heat_score: 61,
    scenario_context:
      'O teu colega apresentou o trabalho que desenvolvestes juntos numa reunião com a direção, sem te mencionar. O teu gestor elogiou o colega publicamente.',
    question:
      'Cooperas em silêncio, confrontas o colega em privado, ou clarificas a tua contribuição ao gestor? Qual estratégia maximiza o teu payoff a longo prazo?',
    predicted_outcome:
      'Silêncio cria precedente que o comportamento tem custo zero. Confronto directo tem risco de parecer mesquinho. A jogada ótima é reframing de contribuição com o gestor num contexto natural.',
    game_theory_explanation:
      'Este é um Dilema do Prisioneiro assimétrico com elemento de Reputação. Cooperação silenciosa é dominada — cria incentivo para o colega repetir. Confronto directo tem alto risco de reputação negativa. A estratégia ótima: "Fico contente que a análise que o X e eu trabalhámos sobre [tema] tenha ressoado — temos mais dados se quiserem aprofundar." Clarifica a tua contribuição, posiciona-te como colaborador valioso e não como queixoso.',
  },
];

export default function DemoPage() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [revealed, setRevealed] = useState(false);
  const [showCTAModal, setShowCTAModal] = useState(false);
  const [demoComplete, setDemoComplete] = useState(false);

  const card = DEMO_CARDS[currentIndex];

  const handleSwipeAttempt = () => {
    setShowCTAModal(true);
  };

  const handleModalDismiss = () => {
    setShowCTAModal(false);
    if (currentIndex < DEMO_CARDS.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setRevealed(false);
    } else {
      setDemoComplete(true);
    }
  };

  if (demoComplete) {
    return (
      <div style={{ minHeight: 'calc(100vh - 56px)', background: '#12121a', padding: '2rem 1rem', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ maxWidth: 400, width: '100%', textAlign: 'center' }}>
          <div style={{ fontSize: 56, marginBottom: 16 }}>🎴</div>
          <h2 style={{ color: '#e9d5ff', fontSize: 22, fontWeight: 800, letterSpacing: 2, textTransform: 'uppercase', marginBottom: 12 }}>
            Demo Concluída
          </h2>
          <p style={{ color: '#9ca3af', fontSize: 14, lineHeight: 1.7, marginBottom: 28 }}>
            Treinaste com 3 cenários de Teoria dos Jogos. Com a tua conta podes gerar cards ilimitados para qualquer domínio da tua vida.
          </p>
          <Link
            to="/register"
            style={{
              display: 'block', width: '100%', padding: '14px 0', borderRadius: 10, boxSizing: 'border-box',
              background: 'linear-gradient(135deg, #7c3aed, #a855f7)', color: '#fff',
              textAlign: 'center', fontWeight: 800, fontSize: 13, letterSpacing: 2,
              textTransform: 'uppercase', marginBottom: 12, textDecoration: 'none',
            }}
          >
            Activar o Oráculo Completo →
          </Link>
          <Link
            to="/"
            style={{
              display: 'block', color: '#6b7280', fontSize: 12, textDecoration: 'none',
              letterSpacing: 1, textTransform: 'uppercase',
            }}
          >
            Voltar à página inicial
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: 'calc(100vh - 56px)', background: '#12121a', padding: '2rem 1rem', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <div style={{ maxWidth: 520, width: '100%' }}>

        {/* Demo banner */}
        <div style={{
          background: 'rgba(124, 58, 237, 0.15)',
          border: '1px solid rgba(124, 58, 237, 0.4)',
          borderRadius: 8, padding: '10px 16px', marginBottom: '1.5rem',
          display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 8,
        }}>
          <span style={{ color: '#a78bfa', fontSize: 12, fontWeight: 700, letterSpacing: 2, textTransform: 'uppercase' }}>
            DEMO · Crie sua conta para salvar cards
          </span>
          <Link to="/register" style={{ color: '#e9d5ff', fontSize: 12, fontWeight: 600, textDecoration: 'underline' }}>
            Cadastrar Grátis →
          </Link>
        </div>

        {/* Header */}
        <div style={{ marginBottom: '1.25rem' }}>
          <h1 style={{ color: '#e9d5ff', fontSize: 20, fontWeight: 800, letterSpacing: 2, textTransform: 'uppercase', margin: 0 }}>
            Teoria dos Jogos · Demo
          </h1>
          <p style={{ color: '#6b7280', fontSize: 12, marginTop: 4 }}>
            Experimente o fluxo real · Crie conta para salvar e treinar os seus próprios cards
          </p>
        </div>

        {/* Progress bar */}
        <div style={{ marginBottom: '1.25rem', display: 'flex', gap: 6 }}>
          {DEMO_CARDS.map((_, i) => (
            <div key={i} style={{
              height: 4, flex: 1, borderRadius: 4,
              background: i < currentIndex ? '#7c3aed' : i === currentIndex ? '#a78bfa' : '#2d2d44',
              transition: 'background 0.3s',
            }} />
          ))}
        </div>

        {/* Card */}
        <GameTheoryCard
          card={card}
          revealed={revealed}
          onReveal={() => setRevealed(true)}
          onSave={handleSwipeAttempt}
          onDiscard={handleSwipeAttempt}
        />
      </div>

      {/* CTA Modal */}
      {showCTAModal && (
        <div
          style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 200, padding: '1rem' }}
          onClick={handleModalDismiss}
        >
          <div
            style={{ background: '#1a1a2e', border: '1px solid #7c3aed', borderRadius: 16, padding: '2rem', maxWidth: 380, width: '100%' }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ fontSize: 40, textAlign: 'center', marginBottom: 12 }}>⚡</div>
            <h2 style={{ color: '#e9d5ff', fontSize: 20, fontWeight: 800, textAlign: 'center', letterSpacing: 2, textTransform: 'uppercase', marginBottom: 8 }}>
              Gostou da análise?
            </h2>
            <p style={{ color: '#9ca3af', fontSize: 13, textAlign: 'center', lineHeight: 1.7, marginBottom: 24 }}>
              Cria a tua conta gratuita para salvar este card no teu deck, treinar com repetição espaçada e gerar cenários personalizados para qualquer domínio.
            </p>
            <Link
              to="/register"
              style={{
                display: 'block', padding: '13px 0', borderRadius: 10,
                background: 'linear-gradient(135deg, #7c3aed, #a855f7)', color: '#fff',
                textAlign: 'center', fontWeight: 800, fontSize: 13, letterSpacing: 2,
                textTransform: 'uppercase', marginBottom: 10, textDecoration: 'none',
              }}
            >
              Criar Conta Grátis
            </Link>
            <button
              onClick={handleModalDismiss}
              style={{
                width: '100%', padding: '11px 0', borderRadius: 10, border: '1px solid #374151',
                background: 'transparent', color: '#9ca3af', cursor: 'pointer',
                fontSize: 12, letterSpacing: 1, textTransform: 'uppercase',
              }}
            >
              {currentIndex < DEMO_CARDS.length - 1 ? 'Explorar Próximo Card' : 'Ver Conclusão da Demo'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
