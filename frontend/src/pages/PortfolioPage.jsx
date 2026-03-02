import { IconSparkBoost } from '../components/Icons/ActionIcons';

const PORTFOLIO_DATA = {
  name: 'João Duarte',
  headline: 'Desenvolvedor Full-Stack · Estrategista · Builder',
  tagline: 'Construo produtos que cruzam código, dados e teoria dos jogos.',
  email: 'joao@example.com',
  github: 'https://github.com/joaod',
  linkedin: '#',
  experiences: [
    {
      role: 'Desenvolvedor Full-Stack',
      company: 'OmniFlash Platform',
      period: '2024 — Presente',
      desc: 'Arquitetura de plataforma React + FastAPI com geração de imagens por IA, sistema de créditos e PWA instalável.',
    },
    {
      role: 'Estrategista de Produto',
      company: 'Projetos Independentes',
      period: '2022 — 2024',
      desc: 'Desenvolvimento de ferramentas analíticas e simuladores para tomada de decisão estratégica.',
    },
  ],
  projects: [
    {
      name: 'Simulador Universal de Teoria dos Jogos',
      desc: 'Plataforma web de simulação estratégica baseada no Dilema do Prisioneiro e Equilíbrio de Nash.',
      tech: ['React 19', 'FastAPI', 'Tailwind CSS', 'PWA'],
      link: '/simulador',
    },
    {
      name: 'Mapa dos Sonhos',
      desc: 'Mural visual interativo para gestão e visualização de objetivos de vida.',
      tech: ['HTML', 'CSS', 'JavaScript'],
      link: '/mural',
    },
    {
      name: 'Avatar Generator API',
      desc: 'API de geração de avatares estilizados com IA usando Stable Diffusion e face-swap.',
      tech: ['Python', 'FastAPI', 'Stable Diffusion', 'SSE'],
      link: '#',
    },
  ],
  skills: [
    { category: 'Frontend', items: ['React 19', 'TypeScript', 'Tailwind CSS', 'Vite', 'PWA'] },
    { category: 'Backend',  items: ['FastAPI', 'Python', 'PostgreSQL', 'Redis', 'Docker'] },
    { category: 'IA/ML',    items: ['Stable Diffusion', 'ComfyUI', 'LangChain', 'GPT-4'] },
    { category: 'Strategy', items: ['Teoria dos Jogos', 'Nash Equilibrium', 'Game Design', 'Product'] },
  ],
};

export default function PortfolioPage() {
  const d = PORTFOLIO_DATA;

  return (
    <div className="min-h-screen" style={{ background: '#12121a', color: '#e2e8f0' }}>
      {/* ── Hero ── */}
      <section
        className="py-24 px-4 text-center relative overflow-hidden"
        style={{ background: 'linear-gradient(135deg, #12121a 0%, #1a0a2e 50%, #12121a 100%)' }}
      >
        <div
          className="absolute inset-0 opacity-5"
          style={{
            backgroundImage: 'radial-gradient(circle, rgba(168,85,247,0.8) 1px, transparent 1px)',
            backgroundSize: '30px 30px',
          }}
        />
        <div className="relative max-w-2xl mx-auto">
          <div className="w-20 h-20 rounded-full mx-auto mb-6 flex items-center justify-center text-4xl"
               style={{ background: 'linear-gradient(135deg, #7c3aed, #a855f7)' }}>
            <IconSparkBoost width={36} height={36} />
          </div>
          <h1 className="font-title text-4xl sm:text-5xl tracking-widest text-white mb-3">{d.name.toUpperCase()}</h1>
          <p className="text-purple-300 text-lg mb-3">{d.headline}</p>
          <p className="text-gray-400 max-w-lg mx-auto">{d.tagline}</p>

          <div className="flex justify-center gap-4 mt-6">
            <a href={`mailto:${d.email}`}
               className="px-5 py-2 rounded-lg text-xs uppercase tracking-wider text-white transition-all hover:opacity-80"
               style={{ background: 'linear-gradient(135deg, #7c3aed, #a855f7)' }}>
              Contato
            </a>
            <a href={d.github} target="_blank" rel="noreferrer"
               className="px-5 py-2 rounded-lg text-xs uppercase tracking-wider text-gray-300 hover:text-white transition-colors"
               style={{ border: '1px solid rgba(168,85,247,0.4)' }}>
              GitHub
            </a>
          </div>
        </div>
      </section>

      <div className="max-w-4xl mx-auto px-4 py-16 space-y-16">
        {/* ── Experiences ── */}
        <section>
          <h2 className="font-title text-2xl tracking-widest text-white mb-8"
              style={{ borderBottom: '2px solid #6b21a8', paddingBottom: '0.5rem' }}>
            EXPERIÊNCIAS
          </h2>
          <div className="space-y-6">
            {d.experiences.map((exp, i) => (
              <div key={i}
                   className="rounded-xl p-6 transition-all hover:border-purple-700"
                   style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)' }}>
                <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-1 mb-3">
                  <div>
                    <h3 className="font-semibold text-white">{exp.role}</h3>
                    <p className="text-purple-400 text-sm">{exp.company}</p>
                  </div>
                  <span className="text-xs text-gray-500 uppercase tracking-wider flex-shrink-0">{exp.period}</span>
                </div>
                <p className="text-gray-400 text-sm leading-relaxed">{exp.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ── Projects ── */}
        <section>
          <h2 className="font-title text-2xl tracking-widest text-white mb-8"
              style={{ borderBottom: '2px solid #6b21a8', paddingBottom: '0.5rem' }}>
            PROJETOS
          </h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {d.projects.map((proj, i) => (
              <a key={i} href={proj.link}
                 className="block rounded-xl p-5 transition-all hover:border-purple-600 hover:-translate-y-1 group"
                 style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)' }}>
                <h3 className="font-semibold text-white text-sm mb-2 group-hover:text-purple-300 transition-colors">
                  {proj.name}
                </h3>
                <p className="text-gray-500 text-xs leading-relaxed mb-4">{proj.desc}</p>
                <div className="flex flex-wrap gap-1.5">
                  {proj.tech.map((t) => (
                    <span key={t} className="text-[10px] px-2 py-0.5 rounded-full uppercase tracking-wider"
                          style={{ background: 'rgba(168,85,247,0.1)', color: '#c084fc', border: '1px solid rgba(168,85,247,0.2)' }}>
                      {t}
                    </span>
                  ))}
                </div>
              </a>
            ))}
          </div>
        </section>

        {/* ── Skills ── */}
        <section>
          <h2 className="font-title text-2xl tracking-widest text-white mb-8"
              style={{ borderBottom: '2px solid #6b21a8', paddingBottom: '0.5rem' }}>
            HABILIDADES
          </h2>
          <div className="grid sm:grid-cols-2 gap-5">
            {d.skills.map((group) => (
              <div key={group.category}
                   className="rounded-xl p-5"
                   style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)' }}>
                <h3 className="font-title text-sm tracking-widest text-purple-400 mb-3 uppercase">
                  {group.category}
                </h3>
                <div className="flex flex-wrap gap-2">
                  {group.items.map((item) => (
                    <span key={item}
                          className="text-xs px-3 py-1 rounded-full text-gray-300"
                          style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)' }}>
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* ── Contact ── */}
        <section className="text-center py-8">
          <h2 className="font-title text-2xl tracking-widest text-white mb-4">CONTATO</h2>
          <p className="text-gray-400 mb-6">Vamos construir algo juntos?</p>
          <a href={`mailto:${d.email}`}
             className="inline-block px-8 py-3 rounded-lg font-title tracking-widest text-sm uppercase text-white transition-all hover:scale-105"
             style={{ background: 'linear-gradient(135deg, #7c3aed, #a855f7)' }}>
            Enviar mensagem
          </a>
        </section>
      </div>
    </div>
  );
}
