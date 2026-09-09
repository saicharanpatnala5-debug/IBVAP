import React, { useState } from 'react';
import { 
  Cpu, 
  Play, 
  RotateCcw, 
  ShieldAlert, 
  MapPin, 
  Truck, 
  CloudFog, 
  CheckCircle, 
  Radio, 
  Users, 
  Activity, 
  Sliders 
} from 'lucide-react';
import { useTacticalStore } from '../../store/useTacticalStore';

export interface SimulatedOutpost {
  id: string;
  name: string;
  sector: string;
  activeAlerts: number;
  unitStatus: 'STANDBY' | 'ON PATROL' | 'RESPONDING';
  interceptEta: string;
  threatRisk: number;
}

export const DigitalTwinSimulator: React.FC<{ onClose?: () => void }> = ({ onClose }) => {
  const { setThreatLevel } = useTacticalStore();
  const [selectedScenario, setSelectedScenario] = useState<'breaches' | 'convoy' | 'fog'>('breaches');
  const [isSimulating, setIsSimulating] = useState(false);
  const [simulationActive, setSimulationActive] = useState(false);
  const [injectedCount, setInjectedCount] = useState(0);

  const [outposts, setOutposts] = useState<SimulatedOutpost[]>([
    { id: 'BOP-01', name: 'Mechi River Post', sector: 'Sector Alpha', activeAlerts: 1, unitStatus: 'STANDBY', interceptEta: '4m 10s', threatRisk: 45 },
    { id: 'BOP-02', name: 'Panitanki Integrated CP', sector: 'Sector Alpha', activeAlerts: 2, unitStatus: 'ON PATROL', interceptEta: '2m 15s', threatRisk: 78 },
    { id: 'BOP-03', name: 'Naxalbari Forest Gate', sector: 'Sector Beta', activeAlerts: 0, unitStatus: 'STANDBY', interceptEta: '5m 30s', threatRisk: 22 },
    { id: 'BOP-04', name: 'Galgalia Tea Corridor', sector: 'Sector Beta', activeAlerts: 1, unitStatus: 'STANDBY', interceptEta: '3m 45s', threatRisk: 50 },
    { id: 'BOP-05', name: 'Sukhiapokhri Ridge', sector: 'Sector Gamma', activeAlerts: 0, unitStatus: 'STANDBY', interceptEta: '6m 00s', threatRisk: 15 }
  ]);

  const handleInjectScenario = (scenarioKey: 'breaches' | 'convoy' | 'fog') => {
    setIsSimulating(true);
    setSelectedScenario(scenarioKey);

    setTimeout(() => {
      setIsSimulating(false);
      setSimulationActive(true);

      if (scenarioKey === 'breaches') {
        setThreatLevel('CRITICAL');
        setInjectedCount(5);
        setOutposts([
          { id: 'BOP-01', name: 'Mechi River Post', sector: 'Sector Alpha', activeAlerts: 3, unitStatus: 'RESPONDING', interceptEta: '1m 45s', threatRisk: 125 },
          { id: 'BOP-02', name: 'Panitanki Integrated CP', sector: 'Sector Alpha', activeAlerts: 4, unitStatus: 'RESPONDING', interceptEta: '1m 20s', threatRisk: 132 },
          { id: 'BOP-03', name: 'Naxalbari Forest Gate', sector: 'Sector Beta', activeAlerts: 2, unitStatus: 'ON PATROL', interceptEta: '2m 10s', threatRisk: 95 },
          { id: 'BOP-04', name: 'Galgalia Tea Corridor', sector: 'Sector Beta', activeAlerts: 3, unitStatus: 'RESPONDING', interceptEta: '1m 55s', threatRisk: 110 },
          { id: 'BOP-05', name: 'Sukhiapokhri Ridge', sector: 'Sector Gamma', activeAlerts: 1, unitStatus: 'ON PATROL', interceptEta: '3m 00s', threatRisk: 65 }
        ]);
      } else if (scenarioKey === 'convoy') {
        setThreatLevel('HIGH');
        setInjectedCount(4);
        setOutposts([
          { id: 'BOP-01', name: 'Mechi River Post', sector: 'Sector Alpha', activeAlerts: 1, unitStatus: 'STANDBY', interceptEta: '4m 10s', threatRisk: 45 },
          { id: 'BOP-02', name: 'Panitanki Integrated CP', sector: 'Sector Alpha', activeAlerts: 5, unitStatus: 'RESPONDING', interceptEta: '1m 15s', threatRisk: 118 },
          { id: 'BOP-03', name: 'Naxalbari Forest Gate', sector: 'Sector Beta', activeAlerts: 1, unitStatus: 'ON PATROL', interceptEta: '3m 00s', threatRisk: 55 },
          { id: 'BOP-04', name: 'Galgalia Tea Corridor', sector: 'Sector Beta', activeAlerts: 0, unitStatus: 'STANDBY', interceptEta: '4m 00s', threatRisk: 30 },
          { id: 'BOP-05', name: 'Sukhiapokhri Ridge', sector: 'Sector Gamma', activeAlerts: 0, unitStatus: 'STANDBY', interceptEta: '6m 00s', threatRisk: 15 }
        ]);
      } else if (scenarioKey === 'fog') {
        setThreatLevel('MEDIUM');
        setInjectedCount(3);
        setOutposts([
          { id: 'BOP-01', name: 'Mechi River Post', sector: 'Sector Alpha', activeAlerts: 2, unitStatus: 'ON PATROL', interceptEta: '2m 50s', threatRisk: 82 },
          { id: 'BOP-02', name: 'Panitanki Integrated CP', sector: 'Sector Alpha', activeAlerts: 2, unitStatus: 'ON PATROL', interceptEta: '2m 30s', threatRisk: 75 },
          { id: 'BOP-03', name: 'Naxalbari Forest Gate', sector: 'Sector Beta', activeAlerts: 3, unitStatus: 'RESPONDING', interceptEta: '2m 05s', threatRisk: 90 },
          { id: 'BOP-04', name: 'Galgalia Tea Corridor', sector: 'Sector Beta', activeAlerts: 2, unitStatus: 'ON PATROL', interceptEta: '3m 15s', threatRisk: 80 },
          { id: 'BOP-05', name: 'Sukhiapokhri Ridge', sector: 'Sector Gamma', activeAlerts: 1, unitStatus: 'ON PATROL', interceptEta: '3m 30s', threatRisk: 70 }
        ]);
      }
    }, 450);
  };

  const handleResetBaseline = () => {
    setSimulationActive(false);
    setThreatLevel('LOW');
    setInjectedCount(0);
    setOutposts([
      { id: 'BOP-01', name: 'Mechi River Post', sector: 'Sector Alpha', activeAlerts: 1, unitStatus: 'STANDBY', interceptEta: '4m 10s', threatRisk: 45 },
      { id: 'BOP-02', name: 'Panitanki Integrated CP', sector: 'Sector Alpha', activeAlerts: 2, unitStatus: 'ON PATROL', interceptEta: '2m 15s', threatRisk: 78 },
      { id: 'BOP-03', name: 'Naxalbari Forest Gate', sector: 'Sector Beta', activeAlerts: 0, unitStatus: 'STANDBY', interceptEta: '5m 30s', threatRisk: 22 },
      { id: 'BOP-04', name: 'Galgalia Tea Corridor', sector: 'Sector Beta', activeAlerts: 1, unitStatus: 'STANDBY', interceptEta: '3m 45s', threatRisk: 50 },
      { id: 'BOP-05', name: 'Sukhiapokhri Ridge', sector: 'Sector Gamma', activeAlerts: 0, unitStatus: 'STANDBY', interceptEta: '6m 00s', threatRisk: 15 }
    ]);
  };

  const totalSimulatedAlerts = outposts.reduce((sum, o) => sum + o.activeAlerts, 0);
  const avgResponseTime = simulationActive ? '1m 42s' : '4m 20s';

  return (
    <div className="rounded-2xl liquid-glass border border-cyan-500/40 p-5 space-y-5 shadow-2xl animate-fade-in font-mono text-slate-200">
      {/* Simulator Banner */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-cyan-500/20 pb-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/50 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <Cpu className="w-5 h-5 text-cyan-400 animate-spin-slow" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-base font-bold text-white tracking-wider">
                PREDICTIVE DIGITAL TWIN & SIMULATION ENGINE
              </h3>
              <span className={`text-[10px] font-black px-2 py-0.5 rounded border uppercase ${
                simulationActive 
                  ? 'bg-rose-500/20 text-rose-300 border-rose-500/50 animate-pulse'
                  : 'bg-cyan-500/20 text-cyan-300 border-cyan-500/50'
              }`}>
                {simulationActive ? '● STRESS TEST RUNNING' : 'BASELINE ACTIVE'}
              </span>
            </div>
            <p className="text-xs text-cyan-300/80">
              Interactive "What If?" Scenario Stress-Testing for SIH 2026 Jury Assessment
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {simulationActive && (
            <button
              onClick={handleResetBaseline}
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 text-xs font-bold transition-all flex items-center space-x-1.5 cursor-pointer"
            >
              <RotateCcw className="w-3.5 h-3.5 text-amber-400" />
              <span>Reset Baseline</span>
            </button>
          )}

          {onClose && (
            <button
              onClick={onClose}
              className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white text-xs cursor-pointer"
            >
              Close Twin
            </button>
          )}
        </div>
      </div>

      {/* "What If?" Scenario Selector Grid */}
      <div className="space-y-2">
        <label className="text-xs text-slate-400 font-bold uppercase tracking-wider block flex items-center space-x-1.5">
          <Sliders className="w-3.5 h-3.5 text-cyan-400" />
          <span>Select "What If?" Stress Test Scenario:</span>
        </label>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {/* Scenario 1 */}
          <button
            type="button"
            onClick={() => handleInjectScenario('breaches')}
            disabled={isSimulating}
            className={`p-3.5 rounded-xl border text-left transition-all cursor-pointer ${
              selectedScenario === 'breaches' && simulationActive
                ? 'bg-rose-500/15 border-rose-500/60 shadow-lg shadow-rose-500/20'
                : 'bg-slate-900/70 border-slate-800 hover:border-cyan-500/40 hover:bg-slate-900'
            }`}
          >
            <div className="flex items-center space-x-2 mb-1.5">
              <ShieldAlert className="w-4 h-4 text-rose-400" />
              <span className="text-xs font-bold text-white">5 Coordinated Breaches</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-snug">
              Simulates simultaneous intrusions across Sector Alpha & Beta; tests multi-outpost alert distribution and field unit response coordination.
            </p>
          </button>

          {/* Scenario 2 */}
          <button
            type="button"
            onClick={() => handleInjectScenario('convoy')}
            disabled={isSimulating}
            className={`p-3.5 rounded-xl border text-left transition-all cursor-pointer ${
              selectedScenario === 'convoy' && simulationActive
                ? 'bg-amber-500/15 border-amber-500/60 shadow-lg shadow-amber-500/20'
                : 'bg-slate-900/70 border-slate-800 hover:border-cyan-500/40 hover:bg-slate-900'
            }`}
          >
            <div className="flex items-center space-x-2 mb-1.5">
              <Truck className="w-4 h-4 text-amber-400" />
              <span className="text-xs font-bold text-white">Unregistered Heavy Convoy</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-snug">
              Simulates 3 freight trucks & escort vehicles approaching Panitanki CP; stress-tests multi-target ANPR and human verification guardrails.
            </p>
          </button>

          {/* Scenario 3 */}
          <button
            type="button"
            onClick={() => handleInjectScenario('fog')}
            disabled={isSimulating}
            className={`p-3.5 rounded-xl border text-left transition-all cursor-pointer ${
              selectedScenario === 'fog' && simulationActive
                ? 'bg-cyan-500/15 border-cyan-500/60 shadow-lg shadow-cyan-500/20'
                : 'bg-slate-900/70 border-slate-800 hover:border-cyan-500/40 hover:bg-slate-900'
            }`}
          >
            <div className="flex items-center space-x-2 mb-1.5">
              <CloudFog className="w-4 h-4 text-cyan-400" />
              <span className="text-xs font-bold text-white">Dense Monsoon Fog Blindout</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-snug">
              Optical visibility degraded by 80%; proves zero-delay autonomous failover to Thermal LWIR Dual-Spectrum Cross-Attention.
            </p>
          </button>
        </div>
      </div>

      {/* Live Simulation Operational Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
        <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800">
          <div className="text-slate-400 text-[10px]">TOTAL ACTIVE INCURSIONS</div>
          <div className="text-xl font-bold text-white mt-0.5 flex items-center space-x-1.5">
            <Activity className="w-4 h-4 text-cyan-400" />
            <span>{totalSimulatedAlerts} Targets</span>
          </div>
        </div>

        <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800">
          <div className="text-slate-400 text-[10px]">AVG FIELD RESPONSE TIME</div>
          <div className="text-xl font-bold text-emerald-400 mt-0.5">
            {avgResponseTime}
          </div>
        </div>

        <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800">
          <div className="text-slate-400 text-[10px]">SYNCHRONIZED SENSORS</div>
          <div className="text-xl font-bold text-cyan-400 mt-0.5">
            14 Nodes Online
          </div>
        </div>

        <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800">
          <div className="text-slate-400 text-[10px]">SECTOR TOPOLOGY</div>
          <div className="text-xl font-bold text-amber-400 mt-0.5">
            5 Outposts Tracked
          </div>
        </div>
      </div>

      {/* Outpost Alert Distribution Grid */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs text-slate-400">
          <span className="font-bold uppercase tracking-wider">Simulated Outpost Load Distribution:</span>
          <span className="text-[10px] text-cyan-400">Kalman Heading Vectors • Automated Sector Balancing</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
          {outposts.map((post) => {
            const isCriticalPost = post.threatRisk >= 90;
            return (
              <div
                key={post.id}
                className={`p-3 rounded-xl border transition-all ${
                  isCriticalPost
                    ? 'bg-rose-500/10 border-rose-500/50 shadow-sm'
                    : 'bg-slate-900/50 border-slate-800'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center space-x-1.5">
                    <MapPin className="w-3.5 h-3.5 text-cyan-400" />
                    <span className="font-bold text-xs text-white">{post.id}</span>
                  </div>
                  <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded border uppercase ${
                    post.unitStatus === 'RESPONDING'
                      ? 'bg-rose-500/20 text-rose-300 border-rose-500/40 animate-pulse'
                      : post.unitStatus === 'ON PATROL'
                      ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                      : 'bg-slate-800 text-slate-400 border-slate-700'
                  }`}>
                    {post.unitStatus}
                  </span>
                </div>

                <div className="text-[11px] text-slate-300 font-semibold mb-2">{post.name}</div>

                <div className="flex items-center justify-between text-[10px] font-mono pt-1.5 border-t border-slate-800/80 text-slate-400">
                  <span>Alerts: <strong className="text-white">{post.activeAlerts}</strong></span>
                  <span>Intercept: <strong className="text-emerald-400">{post.interceptEta}</strong></span>
                  <span>Risk: <strong className={isCriticalPost ? 'text-rose-400' : 'text-amber-300'}>{post.threatRisk}</strong></span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
