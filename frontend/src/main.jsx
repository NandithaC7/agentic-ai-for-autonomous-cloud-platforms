import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './App.css'
import { PublicClientApplication } from "@azure/msal-browser";
import { MsalProvider } from "@azure/msal-react";
import { msalConfig } from "./authConfig";

// Only initialize MSAL if a real client ID was provided
const isMsalConfigured = msalConfig.auth.clientId !== "YOUR_CLIENT_ID_HERE" && msalConfig.auth.clientId.length > 10;
let msalInstance = null;

if (isMsalConfigured) {
    msalInstance = new PublicClientApplication(msalConfig);
}

function Root() {
    // If MSAL is configured, wrap the app in the provider (enables login)
    if (msalInstance) {
        return (
            <MsalProvider instance={msalInstance}>
                <App msalEnabled={true} />
            </MsalProvider>
        );
    }
    // If no client ID provided, render the app normally without the login provider
    return <App msalEnabled={false} />;
}

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <Root />
    </React.StrictMode>,
)
