import React, { useState, useEffect } from 'react';
import { Search, History, BarChart3, Film, User, TrendingUp, Clock } from 'lucide-react';
import { searchMovies, getMetrics, getUserInfo } from '../api/client';

const Sidebar = ({ activeUserId, setActiveUserId }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [userInfo, setUserInfo] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [metricsData, userData] = await Promise.all([
          getMetrics(),
          getUserInfo(activeUserId)
        ]);
        setMetrics(metricsData);
        setUserInfo(userData);
      } catch (err) {
        console.error('Failed to fetch data:', err);
        setUserInfo(null);
      }
    };
    fetchData();
  }, [activeUserId]);

  const handleSearch = async (e) => {
    const q = e.target.value;
    setQuery(q);
    if (q.length > 2) {
      setLoading(true);
      try {
        const data = await searchMovies(q);
        setResults(data.results);
      } catch (err) {
        console.error('Search failed:', err);
      } finally {
        setLoading(false);
      }
    } else {
      setResults([]);
    }
  };

  return (
    <aside style={{ width: '320px', display: 'flex', flexDirection: 'column', gap: '1rem', padding: '0 1rem 1rem 1rem' }}>
      {/* Search Section */}
      <section className="glass" style={{ padding: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', color: 'var(--text-secondary)' }}>
          <Search size={18} />
          <h2 style={{ fontSize: '0.875rem', fontWeight: '600', textTransform: 'uppercase' }}>Search Database</h2>
        </div>
        
        <div style={{ position: 'relative' }}>
          <input
            type="text"
            placeholder="Search movies..."
            value={query}
            onChange={handleSearch}
            style={{
              width: '100%',
              background: 'var(--bg-primary)',
              border: '1px solid var(--border-color)',
              borderRadius: '10px',
              padding: '0.75rem 1rem',
              color: 'var(--text-primary)',
              fontSize: '0.875rem',
              transition: 'var(--transition-fast)'
            }}
            onFocus={(e) => e.target.style.borderColor = 'var(--brand-primary)'}
            onBlur={(e) => e.target.style.borderColor = 'var(--border-color)'}
          />
        </div>

        {results.length > 0 && (
          <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {results.map((item, i) => (
              <div key={i} style={{ 
                padding: '0.5rem', 
                borderRadius: '8px', 
                background: 'rgba(255,255,255,0.03)',
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem'
              }}>
                <Film size={14} color="var(--text-tertiary)" />
                <span style={{ fontSize: '0.8rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {item}
                </span>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Metrics Section */}
      <section className="glass" style={{ padding: '1.25rem', flex: 1 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', color: 'var(--text-secondary)' }}>
          <TrendingUp size={18} />
          <h2 style={{ fontSize: '0.875rem', fontWeight: '600', textTransform: 'uppercase' }}>Stats</h2>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1rem' }}>
          <MetricCard icon={<User size={16} />} label="Total Users" value={metrics?.users || '3.5k'} />
          <MetricCard icon={<Film size={16} />} label="Movies" value={metrics?.movies || '20k+'} />
          <MetricCard icon={<History size={16} />} label="Conversations" value={metrics?.conversations || '1.2k'} />
        </div>

        <div style={{ marginTop: '2rem', padding: '1rem', borderRadius: '12px', background: 'var(--brand-primary-dim)', border: '1px solid rgba(99, 102, 241, 0.2)' }}>
          <p style={{ fontSize: '0.75rem', color: 'var(--brand-primary-light)', fontWeight: '500', marginBottom: '0.5rem' }}>
            Current Dataset
          </p>
          <p style={{ fontSize: '0.875rem', fontWeight: '600' }}>LLM-REDIAL (Movie)</p>
        </div>
      </section>

      {/* User Info Section */}
      <section className="glass" style={{ padding: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', color: 'var(--text-secondary)' }}>
          <User size={18} />
          <h2 style={{ fontSize: '0.875rem', fontWeight: '600', textTransform: 'uppercase' }}>User Profile</h2>
        </div>
        
        <div style={{ marginBottom: '1.5rem' }}>
          <p style={{ fontSize: '0.7rem', color: 'var(--text-tertiary)', marginBottom: '0.5rem' }}>ACTIVE USER ID</p>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <input 
              type="text" 
              defaultValue={activeUserId}
              onBlur={(e) => setActiveUserId(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && setActiveUserId(e.target.value)}
              style={{
                flex: 1,
                background: 'rgba(255,255,255,0.03)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                padding: '0.5rem',
                color: 'var(--brand-primary-light)',
                fontSize: '0.875rem',
                fontWeight: '600'
              }}
            />
          </div>
          <p style={{ fontSize: '0.65rem', color: 'var(--text-tertiary)', marginTop: '0.4rem' }}>
            Press Enter to switch user context
          </p>
        </div>

        {userInfo ? (
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem', color: 'var(--text-secondary)' }}>
              <Clock size={14} />
              <span style={{ fontSize: '0.75rem', fontWeight: '600' }}>RECENT HISTORY</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
              {userInfo.history && userInfo.history.length > 0 ? (
                userInfo.history.slice(0, 5).map((movie, i) => (
                  <div key={i} style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', padding: '0.25rem 0', borderBottom: '1px solid rgba(255,255,255,0.02)' }}>
                    {movie}
                  </div>
                ))
              ) : (
                <span style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>No history found</span>
              )}
            </div>
          </div>
        ) : (
          <div style={{ padding: '1rem', textAlign: 'center', color: 'var(--text-tertiary)', fontSize: '0.8rem' }}>
            User data unavailable
          </div>
        )}
      </section>
    </aside>
  );
};

const MetricCard = ({ icon, label, value }) => (
  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.5rem 0' }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
      <div style={{ color: 'var(--text-tertiary)' }}>{icon}</div>
      <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>{label}</span>
    </div>
    <span style={{ fontWeight: '700', fontSize: '1rem' }}>{value}</span>
  </div>
);

export default Sidebar;
