import { useState } from 'react';

const STEPS = [
  {
    id: 1,
    title: 'Quem é Jiang Xueqin',
    subtitle: 'O Professor que joga com o futuro',
    content: (
      <>
        <p className="text-gray-300 leading-relaxed mb-4">
          Jiang Xueqin é um educador sino-canadense formado em Yale (turma de 1999), conhecido
          por aplicar Teoria dos Jogos ao ensino de História e Geopolítica. Criador do projeto
          <span className="text-purple-300 font-semibold"> Predictive History</span> e autor de{' '}
          <em>Creative China</em> (2014), ele leciona que eventos históricos podem ser
          mapeados como jogos estratégicos entre atores racionais.
        </p>
        <div
          className="rounded-lg p-4 text-sm text-gray-400 italic"
          style={{ background: 'rgba(168,85,247,0.08)', border: '1px solid rgba(168,85,247,0.2)' }}
        >
          "História não é uma sequência de acasos. É o resultado de atores perseguindo incentivos
          dentro de restrições. Se você mapeia os incentivos, você prevê o resultado."
          <br />
          <span className="text-purple-400 not-italic font-semibold">— Jiang Xueqin</span>
        </div>
      </>
    ),
    icon: '🎓',
  },
  {
    id: 2,
    title: 'O Método',
    subtitle: 'Teoria dos Jogos aplicada à Geopolítica',
    content: (
      <>
        <p className="text-gray-300 leading-relaxed mb-4">
          O método de Jiang combina{' '}
          <span className="text-purple-300 font-semibold">Teoria dos Jogos clássica</span> com
          análise de incentivos políticos e econômicos. O processo segue quatro etapas:
        </p>
        <ol className="space-y-2 text-sm text-gray-300">
          {[
            ['1. Identificar atores', 'Quem são os jogadores? Estados, facções, lobbies, famílias.'],
            ['2. Mapear incentivos', 'O que cada ator quer maximizar? Poder, riqueza, sobrevivência.'],
            ['3. Estratégias dominantes', 'Dada a matriz de payoffs, qual é a jogada racional de cada ator?'],
            ['4. Equilíbrio de Nash', 'Qual resultado nenhum ator tem incentivo individual de mudar?'],
          ].map(([t, d]) => (
            <li key={t} className="flex gap-3">
              <span
                className="font-semibold text-purple-400 text-xs uppercase tracking-wider mt-0.5 whitespace-nowrap"
              >
                {t}
              </span>
              <span className="text-gray-400">{d}</span>
            </li>
          ))}
        </ol>
      </>
    ),
    icon: '♟',
  },
  {
    id: 3,
    title: 'A Previsão de Trump',
    subtitle: 'Geo-Strategy #8 — maio de 2024',
    content: (
      <>
        <p className="text-gray-300 leading-relaxed mb-4">
          Na aula <em>"Geo-Strategy #8: The Iran Trap"</em>, em maio de 2024, Jiang analisou
          os incentivos da eleição americana e declarou ser{' '}
          <span className="text-purple-300 font-semibold">"muito provável"</span> que Trump
          voltasse à Casa Branca em novembro de 2024.
        </p>
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div
            className="rounded-lg p-3 text-center"
            style={{ background: 'rgba(34,197,94,0.1)', border: '1px solid rgba(34,197,94,0.3)' }}
          >
            <div className="text-green-400 font-title text-lg">ACERTOU</div>
            <div className="text-xs text-gray-400 mt-1">Vitória de Trump em novembro/2024</div>
          </div>
          <div
            className="rounded-lg p-3 text-center"
            style={{ background: 'rgba(251,191,36,0.1)', border: '1px solid rgba(251,191,36,0.3)' }}
          >
            <div className="text-yellow-400 font-title text-lg">ERROU</div>
            <div className="text-xs text-gray-400 mt-1">Previu Nikki Haley como VP (foi J.D. Vance)</div>
          </div>
        </div>
        <p className="text-xs text-gray-500 italic">
          O vídeo da aula viralizou após o resultado eleitoral, com milhões de visualizações.
        </p>
      </>
    ),
    icon: '🗳',
  },
  {
    id: 4,
    title: 'O Jogo do Irã',
    subtitle: 'Da previsão à realidade — junho de 2025',
    content: (
      <>
        <p className="text-gray-300 leading-relaxed mb-4">
          A análise de Jiang sobre o "Iran Trap" se desdobrou em junho de 2025 com o conflito
          de 12 dias entre Israel e Irã, validando seu mapeamento de incentivos:{' '}
          <span className="text-purple-300 font-semibold">lobby pró-Israel, incentivos sauditas e a posição de Kushner</span>{' '}
          como vetores de pressão.
        </p>
        <div
          className="rounded-lg p-4 text-sm"
          style={{ background: 'rgba(251,191,36,0.08)', border: '1px solid rgba(251,191,36,0.2)' }}
        >
          <p className="text-yellow-300 font-semibold mb-2">Crítica honesta:</p>
          <p className="text-gray-400 leading-relaxed">
            O método de Jiang é mais <em>construção de cenários por incentivos</em> do que um
            modelo estatístico formal. Não há probabilidades calibradas — é análise qualitativa
            estruturada. Poderosa, mas não é previsão matemática.
          </p>
        </div>
      </>
    ),
    icon: '🌍',
  },
];

export default function JiangSection() {
  const [activeStep, setActiveStep] = useState(0);
  const step = STEPS[activeStep];

  return (
    <section id="jiang" className="py-20 px-4" style={{ background: '#0f0f17' }}>
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <span
            className="inline-block mb-3 px-3 py-1 text-xs uppercase tracking-widest rounded-full"
            style={{ background: 'rgba(168,85,247,0.1)', border: '1px solid rgba(168,85,247,0.3)', color: '#a855f7' }}
          >
            O Professor
          </span>
          <h2 className="font-title text-3xl sm:text-4xl tracking-wider text-white mb-3">
            JIANG XUEQIN
          </h2>
          <p className="text-gray-400 max-w-xl mx-auto">
            O educador que usou Teoria dos Jogos para prever uma das eleições mais
            imprevisíveis da história recente.
          </p>
        </div>

        {/* Stepper tabs */}
        <div className="flex gap-2 mb-8 overflow-x-auto no-scrollbar pb-1">
          {STEPS.map((s, i) => (
            <button
              key={s.id}
              onClick={() => setActiveStep(i)}
              className={`flex-shrink-0 flex items-center gap-2 px-4 py-2 rounded-lg text-sm transition-all ${
                i === activeStep
                  ? 'text-white'
                  : 'text-gray-500 hover:text-gray-300'
              }`}
              style={
                i === activeStep
                  ? { background: 'rgba(168,85,247,0.2)', border: '1px solid #a855f7' }
                  : { background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)' }
              }
            >
              <span>{s.icon}</span>
              <span className="hidden sm:inline whitespace-nowrap">{s.title}</span>
              <span className="sm:hidden font-bold">{s.id}</span>
            </button>
          ))}
        </div>

        {/* Step content */}
        <div
          key={activeStep}
          className="rounded-xl p-6 sm:p-8 fade-in"
          style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(168,85,247,0.15)' }}
        >
          <div className="flex items-start gap-4 mb-6">
            <span className="text-4xl">{step.icon}</span>
            <div>
              <h3 className="font-title text-xl sm:text-2xl tracking-wider text-white">
                {step.title}
              </h3>
              <p className="text-purple-400 text-sm mt-1">{step.subtitle}</p>
            </div>
          </div>
          <div>{step.content}</div>
        </div>

        {/* Navigation */}
        <div className="flex justify-between mt-6">
          <button
            onClick={() => setActiveStep((s) => Math.max(0, s - 1))}
            disabled={activeStep === 0}
            className="px-5 py-2 text-sm rounded-lg transition-colors disabled:opacity-30 disabled:cursor-not-allowed text-gray-300 hover:text-white hover:bg-gray-800"
            style={{ border: '1px solid rgba(255,255,255,0.1)' }}
          >
            ← Anterior
          </button>
          <span className="text-xs text-gray-600 self-center">
            {activeStep + 1} / {STEPS.length}
          </span>
          <button
            onClick={() => setActiveStep((s) => Math.min(STEPS.length - 1, s + 1))}
            disabled={activeStep === STEPS.length - 1}
            className="px-5 py-2 text-sm rounded-lg transition-colors disabled:opacity-30 disabled:cursor-not-allowed text-gray-300 hover:text-white hover:bg-gray-800"
            style={{ border: '1px solid rgba(255,255,255,0.1)' }}
          >
            Próximo →
          </button>
        </div>
      </div>
    </section>
  );
}
