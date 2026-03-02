// EntityCard — Unmatched-style card component
// Props: entity { id, name, power, resources, influence, strategy, image, rank }
//        showDelete, small, onDelete
import { IconDelete, IconStrategy } from '../Icons/ActionIcons';

const STRATEGIES = {
  cooperate: { name: 'COOPERADOR', color: '#22c55e', desc: 'Colabora e retalia proporcionalmente.' },
  defect: { name: 'EXPLORADOR', color: '#ef4444', desc: 'Maximiza ganho individual; trai quando conveniente.' },
  withdraw: { name: 'ISOLADO', color: '#6b7280', desc: 'Evita interações; neutro em conflitos.' },
};

export default function EntityCard({ entity, showDelete = true, small = false, onDelete }) {
  const strat = STRATEGIES[entity.strategy] || STRATEGIES.cooperate;
  const total = entity.power + entity.resources + entity.influence;
  const rank = entity.rank ?? Math.round(total / 3);

  const w = small ? 'w-32' : 'w-48 sm:w-56';
  const titleSize = small ? 'text-xs' : 'text-base';
  const textSize = small ? 'text-[8px]' : 'text-[10px]';

  return (
    <div className={`unmatched-card ${w} transition-transform hover:-translate-y-1 relative`}>
      {showDelete && onDelete && (
        <button
          onClick={(e) => { e.stopPropagation(); onDelete(entity.id); }}
          className="absolute top-2 right-2 z-50 w-7 h-7 rounded-full bg-black/60 hover:bg-black/90 flex items-center justify-center border border-red-500/50 shadow-md transition-all"
        >
          <IconDelete width={16} height={16} />
        </button>
      )}

      <div className="relative w-full h-full card-inner-bg overflow-hidden flex flex-col">
        {/* Art / photo area — 55% */}
        <div className="w-full relative overflow-hidden bg-gray-900 border-b-2 border-white flex-shrink-0"
          style={{ height: '55%' }}>
          {entity.image ? (
            <img
              src={entity.image}
              alt={entity.name}
              className="w-full h-full object-cover absolute inset-0 opacity-90"
            />
          ) : (
            <div
              className="w-full h-full flex flex-col items-center justify-center"
              style={{ background: 'linear-gradient(135deg, #1a0a2e, #4c1d95)' }}
            >
              <IconStrategy type={entity.strategy} width={48} height={48} className="opacity-40" />
            </div>
          )}

          {/* Gradient overlay */}
          <div className="absolute inset-0 bg-gradient-to-r from-black/60 to-transparent" />

          {/* Rank tag — top left */}
          <div
            className="absolute top-0 left-0 px-2 py-0.5 font-title text-xs text-white z-10"
            style={{ background: strat.color, borderBottomRightRadius: '6px' }}
          >
            {rank}
          </div>

          {/* Total score badge */}
          <div className="absolute bottom-[-10px] right-2 z-20 w-7 h-7 rounded-full bg-black border-2 border-white flex items-center justify-center shadow-lg">
            <span className="font-title text-white text-[10px]">{total}</span>
          </div>
        </div>

        {/* Text area — 45% */}
        <div className="w-full text-white p-2 flex flex-col bg-black" style={{ height: '45%' }}>
          <h2
            className={`font-title ${titleSize} tracking-wider leading-none mb-1 uppercase truncate`}
            style={{ color: strat.color }}
          >
            {strat.name}
          </h2>
          <div className="border-t border-gray-700 my-1" />
          <p className={`${textSize} font-bold text-gray-200 truncate uppercase`}>► {entity.name}</p>
          <p className={`${textSize} leading-tight text-gray-400 mt-0.5`}>
            Pod:{entity.power} | Rec:{entity.resources} | Inf:{entity.influence}
          </p>
          <p className={`${textSize} leading-tight text-gray-500 mt-1 italic truncate`}>{strat.desc}</p>

          <div className="absolute bottom-1 right-2 text-[7px] text-gray-700 font-bold uppercase tracking-wider">
            RANK {rank}
          </div>
        </div>
      </div>
    </div>
  );
}
