import { Link } from 'react-router-dom';

export default function HeroSection() {
  return (
    <section className="hero-bg min-h-screen flex flex-col items-center justify-center px-4 text-center relative overflow-hidden">
      {/* Decorative grid lines */}
      <div
        className="absolute inset-0 opacity-5"
        style={{
          backgroundImage:
            'linear-gradient(rgba(168,85,247,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(168,85,247,0.5) 1px, transparent 1px)',
          backgroundSize: '60px 60px',
        }}
      />

      {/* Tag */}
      <div className="relative mb-6 fade-in-up">
        <span
          className="inline-block px-4 py-1 text-xs uppercase tracking-widest rounded-full font-semibold"
          style={{ background: 'rgba(168,85,247,0.15)', border: '1px solid #a855f7', color: '#a855f7' }}
        >
          Teoria dos Jogos · Reflexos Preditivos · IA
        </span>
      </div>

      {/* Headline */}
      <h1
        className="font-title text-4xl sm:text-6xl lg:text-7xl tracking-widest text-white mb-6 relative"
        style={{ animationDelay: '0.1s' }}
      >
        DECIFRE QUALQUER
        <br />
        <span style={{ color: '#a855f7' }}>JOGO.</span>
        <br />
        PREVEJA QUALQUER <span style={{ color: '#e9d5ff' }}>MOVIMENTO.</span>
      </h1>

      {/* Subtitle */}
      <p
        className="max-w-2xl text-gray-300 text-base sm:text-lg leading-relaxed mb-10 fade-in-up"
        style={{ animationDelay: '0.25s' }}
      >
        De flertes a geopolítica — o OmniFlash usa Inteligência Artificial e Teoria dos Jogos
        para modelar qualquer cenário da sua vida e treinar os seus reflexos preditivos
        através de <span className="text-purple-300 font-semibold">flashcards táticos imersivos.</span>
      </p>

      {/* CTAs */}
      <div className="flex flex-col sm:flex-row gap-4 fade-in-up" style={{ animationDelay: '0.4s' }}>
        <Link
          to="/register"
          className="px-8 py-3 rounded-lg font-title tracking-widest text-sm uppercase text-white transition-all hover:scale-105 pulse-glow"
          style={{ background: 'linear-gradient(135deg, #7c3aed, #a855f7)' }}
        >
          Activar o Oráculo
        </Link>
        <Link
          to="/login"
          className="px-8 py-3 rounded-lg font-title tracking-widest text-sm uppercase transition-all hover:bg-gray-800"
          style={{ border: '1px solid #6b7280', color: '#e2e8f0' }}
        >
          Já tenho conta
        </Link>
      </div>

      {/* Scroll indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-1 opacity-50">
        <span className="text-xs text-gray-500 uppercase tracking-widest">Scroll</span>
        <svg className="w-4 h-4 text-gray-500 animate-bounce" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </section>
  );
}
