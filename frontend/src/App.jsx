import React, { useState } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Chat from './components/Chat';

function App() {
  const [activeUserId, setActiveUserId] = useState('A30Q8X8B1S3GGT');

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Header />
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        <Sidebar activeUserId={activeUserId} setActiveUserId={setActiveUserId} />
        <Chat activeUserId={activeUserId} />
      </div>
    </div>
  );
}

export default App;
