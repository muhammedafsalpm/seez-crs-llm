import React, { useEffect, useState } from 'react';
import { Activity, ShieldCheck, ShieldAlert } from 'lucide-react';
import { getHealth } from '../api/client';

const Header = () => {
  const [status, setStatus] = useState('loading'); // loading, healthy, error

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const data = await getHealth();
        if (data.status === 'healthy') {
          setStatus('healthy');
        } else {
          setStatus('error');
        }
      } catch (err) {
        setStatus('error');
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="glass" style={{ margin: '1rem', padding: '0.75rem 1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <div style={{ background: 'var(--brand-primary)', width: '32px', height: '32px', borderRadius: '8px', display: 'grid', placeItems: 'center' }}>
          <Activity size={20} color="white" />
        </div>
        <h1 style={{ fontSize: '1.25rem', fontWeight: '700', letterSpacing: '-0.025em' }}>
          CRS <span className="gradient-text">Studio</span>
        </h1>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
          {status === 'healthy' ? (
            <ShieldCheck size={16} color="#10b981" />
          ) : status === 'error' ? (
            <ShieldAlert size={16} color="#ef4444" />
          ) : (
            <Activity size={16} className="animate-spin" />
          )}
          <span>System {status === 'healthy' ? 'Online' : status === 'error' ? 'Offline' : 'Checking...'}</span>
        </div>
        <div style={{ width: '1px', height: '20px', background: 'var(--border-color)' }}></div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: status === 'healthy' ? '#10b981' : '#ef4444' }}></div>
          <span style={{ fontSize: '0.75rem', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            API v1.0.0
          </span>
        </div>
      </div>
    </header>
  );
};

export default Header;
