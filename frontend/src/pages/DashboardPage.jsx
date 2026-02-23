export default function DashboardPage() {
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
        src="/dashboard/index.html"
        title="Dashboard"
        style={{
          flex: 1,
          border: 'none',
          width: '100%',
          height: '100%',
        }}
      />
    </div>
  );
}
