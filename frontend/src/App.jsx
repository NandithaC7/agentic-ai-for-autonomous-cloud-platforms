import React, { useState } from 'react';
import { Cloud, LogOut, Shield, Cpu, Eye, Rocket, Bot } from 'lucide-react';
import { loginRequest } from "./authConfig";
import QueryTab from './components/QueryTab';
import VisionTab from './components/VisionTab';
import AgentTab from './components/AgentTab';
import DeployTab from './components/DeployTab';

// Only load MSAL if it's available and configured
let useMsalHook = null;
try {
    useMsalHook = require("@azure/msal-react").useMsal;
} catch (e) {}

function App({ msalEnabled }) {
    const [activeTab, setActiveTab] = useState('query');
    
    // Safely call the hook only if MSAL is enabled
    let msalContext = { instance: null, accounts: [] };
    if (msalEnabled && useMsalHook) {
        try {
            msalContext = useMsalHook();
        } catch(e) {}
    }
    
    const { instance, accounts } = msalContext;
    const isLoggedIn = accounts && accounts.length > 0;

    const handleLogin = () => {
        if (instance) {
            instance.loginPopup(loginRequest).catch(e => {
                console.error("Login error:", e);
                alert("Login failed. Check console for details.");
            });
        }
    };

    const handleLogout = () => {
        if (instance) {
            instance.logoutPopup().catch(e => {
                console.error(e);
            });
        }
    };

    // If MSAL is NOT enabled, render the dashboard directly without login
    if (!msalEnabled) {
        return <Dashboard activeTab={activeTab} setActiveTab={setActiveTab} />;
    }

    // If MSAL is enabled, enforce the login gate
    return (
        <>
            {/* LOGIN SCREEN (Only shown if MSAL is enabled but user is not logged in) */}
            {!isLoggedIn && (
                <div className="login-page">
                    <div className="login-card fade-in">
                        <div className="login-icon">
                            <Cloud size={32} color="white" />
                        </div>
                        <h1>Azure Agentic Cloud</h1>
                        <p className="subtitle">
                            AI-powered autonomous cloud management.<br />
                            Sign in with your Microsoft account to get started.
                        </p>

                        <button className="login-button" onClick={handleLogin}>
                            <svg width="20" height="20" viewBox="0 0 21 21" fill="none">
                                <rect x="1" y="1" width="9" height="9" fill="#f25022"/>
                                <rect x="11" y="1" width="9" height="9" fill="#7fba00"/>
                                <rect x="1" y="11" width="9" height="9" fill="#00a4ef"/>
                                <rect x="11" y="11" width="9" height="9" fill="#ffb900"/>
                            </svg>
                            Sign in with Microsoft
                        </button>

                        <div className="login-features">
                            <div className="login-feature"><span>🛡️</span> Security Scan</div>
                            <div className="login-feature"><span>💰</span> Cost Analysis</div>
                            <div className="login-feature"><span>🚀</span> Auto Deploy</div>
                            <div className="login-feature"><span>🧠</span> AI Vision</div>
                        </div>
                    </div>
                </div>
            )}

            {/* MAIN DASHBOARD (Only shown if logged in) */}
            {isLoggedIn && (
                <Dashboard 
                    activeTab={activeTab} 
                    setActiveTab={setActiveTab} 
                    user={accounts[0]} 
                    onLogout={handleLogout} 
                />
            )}
        </>
    );
}

// Extracted the dashboard UI into a reusable component
function Dashboard({ activeTab, setActiveTab, user, onLogout }) {
    return (
        <div className="app fade-in">
            <header className="header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <h1>Azure Agentic Cloud</h1>
                    <p>AI-powered autonomous cloud management</p>
                </div>
                {/* Only show the logout button if a user object was passed in */}
                {user && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                            🟢 {user.name || user.username}
                        </span>
                        <button onClick={onLogout} className="button-secondary" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                            <LogOut size={14} /> Sign out
                        </button>
                    </div>
                )}
            </header>

            <div className="tabs">
                <button
                    className={`tab-button ${activeTab === 'query' ? 'active' : ''}`}
                    onClick={() => setActiveTab('query')}
                >
                    <span>💬 Ask Questions</span>
                </button>
                <button
                    className={`tab-button ${activeTab === 'vision' ? 'active' : ''}`}
                    onClick={() => setActiveTab('vision')}
                >
                    <span>👁️ Vision Deploy</span>
                </button>
                <button
                    className={`tab-button ${activeTab === 'deploy' ? 'active' : ''}`}
                    onClick={() => setActiveTab('deploy')}
                >
                    <span>🚀 Deploy Code</span>
                </button>
                <button
                    className={`tab-button ${activeTab === 'agents' ? 'active' : ''}`}
                    onClick={() => setActiveTab('agents')}
                >
                    <span>🤖 Agents</span>
                </button>
            </div>

            <div className="tab-content fade-in">
                {activeTab === 'query' && <QueryTab />}
                {activeTab === 'vision' && <VisionTab />}
                {activeTab === 'deploy' && <DeployTab />}
                {activeTab === 'agents' && <AgentTab />}
            </div>
        </div>
    );
}

export default App;
