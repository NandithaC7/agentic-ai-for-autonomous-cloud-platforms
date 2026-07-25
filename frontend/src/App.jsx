import React, { useState } from 'react';
import { Cloud, Brain, Shield, LogOut } from 'lucide-react';
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
            console.error(e);
        });
    };

    const handleLogout = () => {
        instance.logoutPopup().catch(e => {
            console.error(e);
        });
    };

    return (
        <div className="app">
            <header className="header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <h1>Azure Agentic Cloud</h1>
                    <p>AI-powered autonomous cloud management platform</p>
                </div>
                <AuthenticatedTemplate>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <span style={{ color: 'var(--text-secondary)' }}>
                            Welcome, {accounts[0]?.name}
                        </span>
                        <button onClick={handleLogout} className="button-secondary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <LogOut size={16} /> Logout
                        </button>
                    </div>
                </AuthenticatedTemplate>
            </header>

            <UnauthenticatedTemplate>
                <div style={{ padding: '4rem', textAlign: 'center' }}>
                    <h2>Welcome to Azure Agentic Cloud</h2>
                    <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
                        Please login with your Microsoft account to manage your Azure resources.
                    </p>
                    <button className="button-primary" onClick={handleLogin}>
                        Login with Microsoft
                    </button>
                </div>
            </UnauthenticatedTemplate>

            <AuthenticatedTemplate>
                <div className="tabs">
                    <button
                        className={`tab-button ${activeTab === 'query' ? 'active' : ''}`}
                        onClick={() => setActiveTab('query')}
                    >
                        <span>Ask Questions</span>
                    </button>
                    <button
                        className={`tab-button ${activeTab === 'vision' ? 'active' : ''}`}
                        onClick={() => setActiveTab('vision')}
                    >
                        <span>Vision Deploy</span>
                    </button>
                    <button
                        className={`tab-button ${activeTab === 'deploy' ? 'active' : ''}`}
                        onClick={() => setActiveTab('deploy')}
                    >
                        <span>Deploy Code</span>
                    </button>
                    <button
                        className={`tab-button ${activeTab === 'agents' ? 'active' : ''}`}
                        onClick={() => setActiveTab('agents')}
                    >
                        <span>Agents</span>
                    </button>
                </div>

                <div className="tab-content">
                    {activeTab === 'query' && <QueryTab />}
                    {activeTab === 'vision' && <VisionTab />}
                    {activeTab === 'deploy' && <DeployTab />}
                    {activeTab === 'agents' && <AgentTab />}
                </div>
            </AuthenticatedTemplate>
        </div>
    );
}

export default App;
