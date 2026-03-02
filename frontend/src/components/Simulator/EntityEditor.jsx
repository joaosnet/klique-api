import { useState } from 'react';
import EntityCard from './EntityCard';
import { IconClose, IconPhoto, IconStrategy } from '../Icons/ActionIcons';

const STRATEGY_OPTIONS = [
  { value: 'cooperate', label: 'Cooperador', desc: 'Colabora; retalia se traído' },
  { value: 'defect', label: 'Explorador', desc: 'Maximiza ganho individual' },
  { value: 'withdraw', label: 'Isolado', desc: 'Evita interações; neutro' },
];

const DEFAULT_ENTITY = { name: '', power: 3, resources: 3, influence: 3, strategy: 'cooperate', image: null };

export default function EntityEditor({ onSave, onClose, initial }) {
  const [form, setForm] = useState(initial ? { ...initial } : { ...DEFAULT_ENTITY });

  const set = (field, value) => setForm((f) => ({ ...f, [field]: value }));

  const handlePhoto = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => set('image', ev.target.result);
    reader.readAsDataURL(file);
  };

  const handleSave = () => {
    if (!form.name.trim()) return;
    const rank = Math.round((form.power + form.resources + form.influence) / 3);
    onSave({ ...form, rank });
  };

  const preview = {
    ...form,
    rank: Math.round((form.power + form.resources + form.influence) / 3),
  };

  return (
    <div className="modal-bg fixed inset-0 z-50 flex items-center justify-center p-4">
      <div
        className="w-full max-w-md rounded-2xl overflow-y-auto max-h-[90vh]"
        style={{ background: '#1a1a2e', border: '1px solid rgba(168,85,247,0.3)' }}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4"
          style={{ borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
          <h2 className="font-title text-lg tracking-widest text-white">
            {initial ? 'EDITAR ENTIDADE' : 'NOVA ENTIDADE'}
          </h2>
          <button onClick={onClose} className="text-gray-500 hover:text-white transition-colors">
            <IconClose width={20} height={20} />
          </button>
        </div>

        <div className="px-6 py-5 space-y-5">
          {/* Preview */}
          <div className="flex justify-center">
            <EntityCard entity={preview} showDelete={false} small={false} />
          </div>

          {/* Name */}
          <div>
            <label className="block text-xs uppercase tracking-widest text-gray-400 mb-2">Nome</label>
            <input
              type="text"
              value={form.name}
              onChange={(e) => set('name', e.target.value)}
              placeholder="Ex: Aliança Pacífica"
              className="w-full rounded-lg px-4 py-2.5 text-sm text-gray-100 placeholder-gray-600 outline-none"
              style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)' }}
            />
          </div>

          {/* Photo */}
          <div>
            <label className="block text-xs uppercase tracking-widest text-gray-400 mb-2">Foto</label>
            <div
              className="image-upload-wrapper"
              style={form.image ? { backgroundImage: `url(${form.image})` } : {}}
            >
              <input type="file" accept="image/*" onChange={handlePhoto} />
              {!form.image && (
                <div className="text-center pointer-events-none flex flex-col items-center justify-center">
                  <IconPhoto width={32} height={32} className="mb-2" />
                  <p className="text-xs text-gray-500">Clique para adicionar</p>
                </div>
              )}
            </div>
            {form.image && (
              <button
                onClick={() => set('image', null)}
                className="text-xs text-red-400 hover:text-red-300 mt-1 transition-colors"
              >
                Remover foto
              </button>
            )}
          </div>

          {/* Strategy */}
          <div>
            <label className="block text-xs uppercase tracking-widest text-gray-400 mb-2">Estratégia</label>
            <div className="grid grid-cols-3 gap-2">
              {STRATEGY_OPTIONS.map(({ value, label }) => (
                <button
                  key={value}
                  type="button"
                  onClick={() => set('strategy', value)}
                  className="py-2.5 flex flex-col items-center justify-center rounded-lg text-xs font-semibold transition-all gap-1"
                  style={
                    form.strategy === value
                      ? { background: 'rgba(168,85,247,0.25)', border: '1px solid #a855f7', color: '#e9d5ff' }
                      : { background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)', color: '#9ca3af' }
                  }
                >
                  <IconStrategy type={value} width={20} height={20} className={form.strategy !== value ? 'opacity-50 grayscale' : ''} />
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* Sliders */}
          {[
            { field: 'power', label: 'Poder', color: '#ef4444' },
            { field: 'resources', label: 'Recursos', color: '#f59e0b' },
            { field: 'influence', label: 'Influência', color: '#a855f7' },
          ].map(({ field, label, color }) => (
            <div key={field}>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-gray-400 uppercase tracking-wider">{label}</span>
                <span className="font-bold text-white">{form[field]}</span>
              </div>
              <input
                type="range"
                min={1}
                max={5}
                value={form[field]}
                onChange={(e) => set(field, Number(e.target.value))}
                style={{ accentColor: color }}
              />
            </div>
          ))}

          {/* Rank preview */}
          <div className="text-center text-xs text-gray-500 uppercase tracking-wider">
            Rank estimado:{' '}
            <span className="text-purple-400 font-bold text-sm">
              {Math.round((form.power + form.resources + form.influence) / 3)}
            </span>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 flex gap-3" style={{ borderTop: '1px solid rgba(255,255,255,0.08)' }}>
          <button
            onClick={onClose}
            className="flex-1 py-2.5 rounded-lg text-sm text-gray-400 hover:text-white hover:bg-gray-800 transition-colors"
            style={{ border: '1px solid rgba(255,255,255,0.1)' }}
          >
            Cancelar
          </button>
          <button
            onClick={handleSave}
            disabled={!form.name.trim()}
            className="flex-1 py-2.5 rounded-lg font-title tracking-widest text-sm uppercase text-white transition-all hover:opacity-90 disabled:opacity-40"
            style={{ background: 'linear-gradient(135deg, #7c3aed, #a855f7)' }}
          >
            Salvar
          </button>
        </div>
      </div>
    </div>
  );
}
