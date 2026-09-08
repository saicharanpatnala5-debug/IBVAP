import React, { useState, useEffect } from 'react';
import { Navbar } from './components/common/Navbar';
import { Sidebar } from './components/common/Sidebar';
import { TacticalAuth } from './services/auth';

// 16 Tactical Pages
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { LiveMonitoring } from './pages/LiveMonitoring';
import { Cameras } from './pages/Cameras';
import { Alerts } from './pages/Alerts';
import { Incidents } from './pages/Incidents';
import { IncidentDetails } from './pages/IncidentDetails';
import { VideoSearch } from './pages/VideoSearch';
import { Analytics } from './pages/Analytics';
import { MapView } from './pages/MapView';
import { Settings } from './pages/Settings';
import { About } from './pages/About';
import { Contact } from './pages/Contact';
import { Waitlist } from './pages/Waitlist';
import { ThankYou } from './pages/ThankYou';
import { NotFound } from './pages/NotFound';

export const App: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(true);
  const [currentPage, setCurrentPage] = useState<string>('dashboard');
  const [selectedIncidentId, setSelectedIncidentId] = useState<string>('INC-20260905-001');

  useEffect(() => {
    // Check if an existing session exists; if not, initialize default admin preset for immediate MVP readiness
    if (!TacticalAuth.isAuthenticated()) {
      TacticalAuth.setSession(TacticalAuth.getDefaultPreset('admin'));
    }
    setIsAuthenticated(true);
  }, []);

  const handleNavigate = (page: string) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
    setCurrentPage('dashboard');
  };

  if (!isAuthenticated) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  const renderActivePage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard onNavigate={handleNavigate} />;
      case 'live':
        return <LiveMonitoring />;
      case 'cameras':
        return <Cameras />;
      case 'alerts':
        return <Alerts />;
      case 'incidents':
        return (
          <Incidents
            onSelectIncident={(id) => {
              setSelectedIncidentId(id);
              setCurrentPage('incident-details');
            }}
          />
        );
      case 'incident-details':
        return (
          <IncidentDetails
            incidentId={selectedIncidentId}
            onBack={() => setCurrentPage('incidents')}
          />
        );
      case 'search':
        return <VideoSearch />;
      case 'analytics':
        return <Analytics />;
      case 'map':
        return <MapView />;
      case 'settings':
        return <Settings />;
      case 'about':
        return <About />;
      case 'contact':
        return <Contact />;
      case 'waitlist':
        return <Waitlist onSubmitted={() => setCurrentPage('thankyou')} />;
      case 'thankyou':
        return <ThankYou onReturnHome={() => setCurrentPage('dashboard')} />;
      case 'login':
        return <Login onLoginSuccess={handleLoginSuccess} />;
      default:
        return <NotFound onReturnHome={() => setCurrentPage('dashboard')} />;
    }
  };

  return (
    <div className="min-h-screen bg-obsidian text-slate-100 flex flex-col font-sans selection:bg-brand-emerald/30 selection:text-brand-emerald">
      <Navbar onNavigate={handleNavigate} activePage={currentPage} />
      <div className="flex flex-1 relative overflow-hidden">
        <Sidebar currentPage={currentPage} onNavigate={handleNavigate} />
        <main className="flex-1 bg-obsidian/95 overflow-y-auto">
          {renderActivePage()}
        </main>
      </div>
    </div>
  );
};

export default App;
