import React, { useState } from 'react';
import { Cloud, LogOut, Shield, Cpu, Eye, Rocket, Bot } from 'lucide-react';
import { useMsal, AuthenticatedTemplate, UnauthenticatedTemplate } from "@azure/msal-react";
import { loginRequest } from "./authConfig";
import QueryTab from './components/QueryTab';
import VisionTab from './components/VisionTab';
import AgentTab from './components/AgentTab';
import DeployTab from './components/DeployTab';

function App() {
    const [activeTab, setActiveTab] = useState('query');
    const { instance, accounts } = useMsal();

    const handleLogin = () => {
        instance.loginPopup(loginRequest).catch(e => {
            console.error("Login error:", e);
        });
    };

    const handleLogout = () => {
        instance.logoutPopup().catch(e => {
            console.error(e);
        });
    };

    return (
        <>
            {/* ===== LOGIN SCREEN ===== */}
            <UnauthenticatedTemplate>
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
                            <div className="login-feature">
                                <span>🛡️</span> Security Scan
                            </div>
                            <div className="login-feature">
                                <span>💰</span> Cost Analysis
                            </div>
                            <div className="login-feature">
                                <span>🚀</span> Auto Deploy
                            </div>
                            <div className="login-feature">
                                <span>🧠</span> AI Vision
                            </div>
                        </div>

                        <div className="login-setup-note">
                            <strong>First time?</strong> You need an Azure App Registration.<br />
                            Go to <a href="https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade" target="_blank" rel="noreferrer">Azure Portal → App Registrations</a> → New Registration → copy the Client ID → paste it in <code>frontend/src/authConfig.js</code>
                        </div>
                    </div>
                </div>
            </UnauthenticatedTemplate>

            {/* ===== MAIN DASHBOARD ===== */}
            <AuthenticatedTemplate>
                <div className="app fade-in">
                    <header className="header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                            <h1>Azure Agentic Cloud</h1>
                            <p>AI-powered autonomous cloud management</p>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                            <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                                {accounts[0]?.name || accounts[0]?.username}
                            </span>
                            <button onClick={handleLogout} className="button-secondary" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                                <LogOut size={14} /> Sign out
                            </button>
                        </div>
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
            </AuthenticatedTemplate>
        </>
    );
}

export default App;
