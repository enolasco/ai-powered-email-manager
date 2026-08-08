import { useEffect, useState } from 'react';
import { authApi } from './utils/api';
import LoginPage from './pages/LoginPage';
import InboxPage from './pages/InboxPage';

function App() {
  const [authenticated, setAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    authApi.status()
      .then(res => setAuthenticated(res.data.authenticated))
      .catch(() => setAuthenticated(false));
  }, []);

  if (authenticated === null) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'system-ui' }}>
        <p>Loading…</p>
      </div>
    );
  }

  return authenticated ? <InboxPage /> : <LoginPage />;
}

export default App;

