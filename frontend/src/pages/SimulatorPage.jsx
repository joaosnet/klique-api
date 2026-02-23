import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import SimulatorRoster from '../components/Simulator/SimulatorRoster';
import SimulatorResults from '../components/Simulator/SimulatorResults';

// Special entity: Professor Jiang
const JIANG_ENTITY = {
  id: 'jiang',
  name: 'Prof. Jiang Xueqin',
  power: 4,
  resources: 3,
  influence: 5,
  strategy: 'cooperate',
  image: null,
  rank: 4,
  special: true,
};

function buildUserCard(user) {
  if (!user) return null;
  return {
    id: 'user',
    name: user.name || user.email,
    power: 50,
    resources: 50,
    influence: 50,
    strategy: 'cooperate',
    image: null,
    rank: 3,
    isUser: true,
  };
}

export default function SimulatorPage() {
  const { user } = useAuth();
  const [population, setPopulation] = useState([{ ...JIANG_ENTITY }]);
  const [screen, setScreen] = useState('roster'); // 'roster' | 'results'

  const userCard = buildUserCard(user);

  const handleAdd = (entity) => {
    setPopulation((prev) => [...prev, entity]);
  };

  const handleRemove = (id) => {
    setPopulation((prev) => prev.filter((e) => e.id !== id && e.id !== 'jiang'));
    // Keep Jiang, restore if accidentally removed
    setPopulation((prev) => {
      const hasJiang = prev.some((e) => e.id === 'jiang');
      return hasJiang ? prev : [...prev, { ...JIANG_ENTITY }];
    });
    setPopulation((prev) => prev.filter((e) => e.id !== id));
  };

  const allEntities = userCard
    ? [userCard, ...population]
    : population;

  return (
    <div
      className="flex flex-col font-body"
      style={{
        background: '#12121a',
        minHeight: 'calc(100vh - 56px)',
        color: '#e2e8f0',
      }}
    >
      {/* Sub-header */}
      <header
        className="text-center py-3 flex-shrink-0"
        style={{ background: '#111827', borderBottom: '2px solid #6b21a8' }}
      >
        <h1 className="font-title text-2xl tracking-widest text-purple-400">SIMULADOR UNIVERSAL</h1>
        <p className="text-[10px] text-gray-500 uppercase tracking-widest">
          Negócios, Política &amp; Sociedade
        </p>
      </header>

      {/* Main content */}
      <main className="flex-1 flex flex-col p-4 overflow-hidden max-w-4xl mx-auto w-full">
        {screen === 'roster' ? (
          <SimulatorRoster
            population={population}
            onAdd={handleAdd}
            onRemove={handleRemove}
            onSimulate={() => setScreen('results')}
            userCard={userCard}
          />
        ) : (
          <SimulatorResults
            population={allEntities}
            onReset={() => setScreen('roster')}
          />
        )}
      </main>
    </div>
  );
}
