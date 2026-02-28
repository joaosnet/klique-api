import { Link } from 'react-router-dom';

const STEPS = [
  {
    number: '01',
    icon: '🗺️',
    title: 'Escolha um Domínio',
    description:
      'Negociação, dating, geopolítica, escritório — qualquer campo onde decisões importam. Você define o campo de batalha.',
  },
  {
    number: '02',
    icon: '🤖',
    title: 'Gere Cards com IA',
    description:
      'O Oráculo analisa o domínio e gera flashcards táticos com cenários reais, perguntas estratégicas e análise de Teoria dos Jogos.',
  },
  {
    number: '03',
    icon: '⚡',
    title: 'Treine e Evolua',
    description:
      'Repetição espaçada (SRS) agenda os cards no momento certo. O teu radar de proficiência mostra onde és forte e onde tens pontos cegos.',
  },
];

export default function HowItWorksSection() {
  return (
    <section className="py-20 px-4" style={{ background: '#0f0f17' }}>
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-14">
          <p className="text-purple-400 text-sm uppercase tracking-widest mb-3 font-semibold">
            Como Funciona
          </p>
          <h2 className="font-title text-3xl sm:text-4xl tracking-wider text-white mb-4">
            TRÊS PASSOS PARA{' '}
            <span style={{ color: '#a855f7' }}>DOMINAR QUALQUER JOGO</span>
          </h2>
          <p className="text-gray-400 text-sm max-w-xl mx-auto leading-relaxed">
            Do cenário à análise estratégica — o Oráculo guia o teu raciocínio com Teoria dos Jogos aplicada ao mundo real.
          </p>
        </div>

        {/* Steps grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          {STEPS.map((step) => (
            <div
              key={step.number}
              className="rounded-xl p-6 relative"
              style={{
                background: 'rgba(255,255,255,0.03)',
                border: '1px solid rgba(168,85,247,0.15)',
              }}
            >
              <div
                className="font-title text-5xl mb-3"
                style={{ color: 'rgba(168,85,247,0.25)', lineHeight: 1 }}
              >
                {step.number}
              </div>
              <div className="text-3xl mb-3">{step.icon}</div>
              <h3 className="font-title text-base tracking-wider text-white mb-2">
                {step.title}
              </h3>
              <p className="text-gray-400 text-sm leading-relaxed">{step.description}</p>
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="text-center">
          <Link
            to="/demo"
            className="inline-block px-10 py-4 rounded-lg font-title tracking-widest text-sm uppercase text-white transition-all hover:scale-105 pulse-glow"
            style={{ background: 'linear-gradient(135deg, #7c3aed, #a855f7)' }}
          >
            Experimentar Agora →
          </Link>
          <p className="text-gray-600 text-xs mt-4">
            Sem conta necessária · 3 cards de demonstração gratuitos
          </p>
        </div>
      </div>
    </section>
  );
}
