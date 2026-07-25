export const msalConfig = {
    auth: {
        clientId: "YOUR_CLIENT_ID_HERE", // Need to be replaced with the actual client id
        authority: "https://login.microsoftonline.com/common",
        redirectUri: "http://localhost:5173",
    },
    cache: {
        cacheLocation: "sessionStorage", // This configures where your cache will be stored
        storeAuthStateInCookie: false, // Set this to "true" if you are having issues on IE11 or Edge
    }
};

// Add scopes here for ID token to be used at Microsoft identity platform endpoints.
export const loginRequest = {
    scopes: ["https://management.azure.com/user_impersonation"]
};
