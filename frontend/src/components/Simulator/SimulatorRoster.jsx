import EntityCard from './EntityCard';
import EntityEditor from './EntityEditor';
import { useState } from 'react';
import { IconDeckCard, IconSparkBoost } from '../Icons/ActionIcons';

const PRESETS = {
  corporativo: {
    label: 'Mercado',
    entities: [
      { name: 'Startup Inovadora',    power: 2, resources: 2, influence: 4, strategy: 'cooperate', image: null },
      { name: 'Monopólio Tech',        power: 5, resources: 5, influence: 5, strategy: 'defect',    image: null },
      { name: 'Pequena Empresa',       power: 1, resources: 2, influence: 1, strategy: 'cooperate', image: null },
      { name: 'Empresa Conservadora',  power: 3, resources: 4, influence: 2, strategy: 'withdraw',  image: null },
    ],
  },
  guerra: {
    label: 'Guerra Fria',
    entities: [
      { name: 'Potência Nuclear', power: 5, resources: 5, influence: 4, strategy: 'defect',    image: null },
      { name: 'Aliança Pacífica', power: 3, resources: 4, influence: 5, strategy: 'cooperate', image: null },
      { name: 'Nação Neutra',     power: 2, resources: 3, influence: 2, strategy: 'withdraw',  image: null },
    ],
  },
  eleicao: {
    label: 'Eleição',
    entities: [
      { name: 'Populista',          power: 3, resources: 2, influence: 5, strategy: 'defect',    image: null },
      { name: 'Tecnocrata',         power: 2, resources: 4, influence: 3, strategy: 'cooperate', image: null },
      { name: 'Partido Tradicional',power: 4, resources: 5, influence: 4, strategy: 'withdraw',  image: null },
      { name: 'Candidato Radical',  power: 4, resources: 2, influence: 3, strategy: 'defect',    image: null },
    ],
  },
};

export default function SimulatorRoster({ population, onAdd, onRemove, onSimulate, userCard }) {
  const [showEditor, setShowEditor] = useState(false);

  const loadPreset = (key) => {
    const preset = PRESETS[key];
    if (!preset) return;
    let nextId = Date.now();
    preset.entities.forEach((e) => {
      const rank = Math.round((e.power + e.resources + e.influence) / 3);
      onAdd({ ...e, id: nextId++, rank });
    });
  };

  const handleSave = (entity) => {
    onAdd({ ...entity, id: Date.now() });
    setShowEditor(false);
  };

  const canSimulate = population.length >= 2;

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-end justify-between mb-4 flex-shrink-0 pb-3"
           style={{ borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
        <div>
          <h2 className="font-title text-xl text-yellow-500 tracking-wider">ENTIDADES PARTICIPANTES</h2>
          <p className="text-xs text-gray-400 uppercase tracking-widest mt-0.5">
            Cartas no Deck:{' '}
            <span className="text-white font-bold">{population.length}</span>
          </p>
        </div>

        <div className="flex gap-2 flex-wrap justify-end">
          {/* Preset dropdown */}
          <div className="relative group">
            <button
              className="px-3 py-1.5 rounded-lg text-xs uppercase tracking-wider transition-colors text-gray-300 hover:text-white hover:bg-gray-800"
              style={{ border: '1px solid rgba(255,255,255,0.1)' }}
            >
              Presets ▾
            </button>
            <div className="absolute right-0 top-full mt-1 hidden group-hover:block z-20 min-w-max rounded-lg shadow-xl"
                 style={{ background: '#1a1a2e', border: '1px solid rgba(168,85,247,0.3)' }}>
              {Object.entries(PRESETS).map(([key, { label }]) => (
                <button
                  key={key}
                  onClick={() => loadPreset(key)}
                  className="block w-full text-left px-4 py-2 text-xs text-gray-300 hover:text-white hover:bg-purple-900/30 transition-colors"
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={() => setShowEditor(true)}
            className="px-3 py-1.5 rounded-lg text-xs uppercase tracking-wider text-white transition-colors hover:opacity-90"
            style={{ background: 'rgba(168,85,247,0.2)', border: '1px solid #a855f7' }}
          >
            + Entidade
          </button>
        </div>
      </div>

      {/* Cards deck */}
      <div className="flex-1 overflow-hidden">
        {population.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center gap-4 text-center py-12">
            <div
              className="w-20 h-20 rounded-2xl flex items-center justify-center"
              style={{ background: 'rgba(168,85,247,0.08)', border: '2px dashed rgba(168,85,247,0.3)' }}
            >
              <IconDeckCard className="opacity-70" width={34} height={34} />
            </div>
            <div>
              <p className="text-gray-400 text-sm">Nenhuma entidade no deck.</p>
              <p className="text-gray-600 text-xs mt-1">
                Adicione entidades ou carregue um preset para simular.
              </p>
            </div>
            <button
              onClick={() => loadPreset('corporativo')}
              className="px-4 py-2 rounded-lg text-xs uppercase tracking-wider text-purple-400 transition-colors hover:bg-purple-900/20"
              style={{ border: '1px solid rgba(168,85,247,0.3)' }}
            >
              Carregar Preset: Mercado
            </button>
          </div>
        ) : (
          <div className="flex gap-4 overflow-x-auto no-scrollbar pb-4 pt-2 snap-x snap-mandatory">
            {/* User card (special) */}
            {userCard && (
              <div className="flex flex-col items-center gap-1 snap-center flex-shrink-0">
                <EntityCard entity={userCard} showDelete={false} />
                <span
                  className="text-[9px] uppercase tracking-widest px-2 py-0.5 rounded-full"
                  style={{ background: 'rgba(168,85,247,0.15)', color: '#a855f7', border: '1px solid rgba(168,85,247,0.3)' }}
                >
                  Você
                </span>
              </div>
            )}

            {[...population]
              .sort((a, b) => (b.rank ?? 0) - (a.rank ?? 0))
              .map((entity) => (
                <EntityCard
                  key={entity.id}
                  entity={entity}
                  showDelete
                  onDelete={onRemove}
                />
              ))}
          </div>
        )}
      </div>

      {/* Simulate button */}
      <div className="flex-shrink-0 pt-4">
        <button
          onClick={onSimulate}
          disabled={!canSimulate}
          className="w-full py-3 rounded-xl font-title tracking-widest text-sm uppercase text-white transition-all hover:scale-[1.02] disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:scale-100"
          style={{ background: canSimulate ? 'linear-gradient(135deg, #7c3aed, #a855f7)' : undefined }}
        >
          {canSimulate ? <span style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}><IconSparkBoost width={16} height={16} /> SIMULAR INTERAÇÕES</span> : `Adicione pelo menos 2 entidades (${population.length}/2)`}
        </button>
      </div>

      {showEditor && (
        <EntityEditor
          onSave={handleSave}
          onClose={() => setShowEditor(false)}
        />
      )}
    </div>
  );
}
