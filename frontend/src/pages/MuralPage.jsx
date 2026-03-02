import { useTranslation } from 'react-i18next';

export default function MuralPage() {
  const { t } = useTranslation();
  return (
    <div
      style={{
        height: 'calc(100vh - 56px)',
        background: '#12121a',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <iframe
        src="/mural-static/index.html"
        title={t('mural.title')}
        style={{
          border: 'none',
          width: '100%',
          height: '100%',
        }}
      />
    </div>
  );
}
