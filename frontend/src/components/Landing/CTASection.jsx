import { Link } from 'react-router-dom';
import { useState, useEffect } from 'react';

// Simulated counters — replace with API call if you add an endpoint
const INITIAL_PLAYERS = 347;
const INITIAL_WINNERS = 89;

export default function CTASection() {
  const [players, setPlayers] = useState(INITIAL_PLAYERS);
  const [winners, setWinners] = useState(INITIAL_WINNERS);

  // Animate counters up on mount
  useEffect(() => {
    let p = 0;
    let w = 0;
    const interval = setInterval(() => {
      p = Math.min(p + 7, INITIAL_PLAYERS);
      w = Math.min(w + 2, INITIAL_WINNERS);
      setPlayers(p);
      setWinners(w);
      if (p >= INITIAL_PLAYERS && w >= INITIAL_WINNERS) clearInterval(interval);
    }, 16);
    return () => clearInterval(interval);
  }, []);

  return (
    <section
      className="py-24 px-4 text-center relative overflow-hidden"
      style={{ background: 'linear-gradient(135deg, #0f0f17 0%, #1a0a2e 50%, #0f0f17 100%)' }}
    >
      {/* Glow orb */}
      <div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 rounded-full pointer-events-none"
        style={{ background: 'radial-gradient(circle, rgba(168,85,247,0.12) 0%, transparent 70%)' }}
      />

      <div className="relative max-w-2xl mx-auto">
        <p className="text-purple-400 text-sm uppercase tracking-widest mb-4 font-semibold">
          O Desafio
        </p>
        <h2 className="font-title text-3xl sm:text-5xl tracking-wider text-white mb-6">
          VOCÊ CONSEGUE SUPERAR
          <br />
          <span style={{ color: '#a855f7' }}>O PROFESSOR JIANG?</span>
        </h2>

        {/* Counter */}
        <div className="flex justify-center gap-8 mb-10">
          <div>
            <div className="font-title text-4xl sm:text-5xl text-white">{players}</div>
            <div className="text-xs text-gray-500 uppercase tracking-widest mt-1">
              Jogadores já tentaram
            </div>
          </div>
          <div
            className="w-px self-stretch"
            style={{ background: 'rgba(168,85,247,0.3)' }}
          />
          <div>
            <div className="font-title text-4xl sm:text-5xl text-purple-400">{winners}</div>
            <div className="text-xs text-gray-500 uppercase tracking-widest mt-1">
              Venceram o simulador
            </div>
          </div>
        </div>

        {/* CTAs */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/register"
            className="px-10 py-4 rounded-lg font-title tracking-widest text-sm uppercase text-white transition-all hover:scale-105 pulse-glow"
            style={{ background: 'linear-gradient(135deg, #7c3aed, #a855f7)' }}
          >
            Cadastre-se e Batalhe
          </Link>
          <Link
            to="/simulador"
            className="px-10 py-4 rounded-lg font-title tracking-widest text-sm uppercase transition-all hover:bg-gray-800"
            style={{ border: '1px solid rgba(168,85,247,0.4)', color: '#c084fc' }}
          >
            Ver o Simulador
          </Link>
        </div>

        <p className="text-gray-600 text-xs mt-6">
          Gratuito · Sem cartão de crédito · Instale como app no Android
        </p>
      </div>
    </section>
  );
}
