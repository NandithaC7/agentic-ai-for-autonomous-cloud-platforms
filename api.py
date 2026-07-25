import os
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from azure.core.credentials import AccessToken

# --- Imports for Orchestrator ---
from agents.orchestrator import OrchestratorAgent, AgentType
from core.llm import get_azure_openai_client

from agents.resource_agent import ResourceOptimizationAgent
from agents.cost_agent import CostManagementAgent
from agents.security_agent import SecurityComplianceAgent
from agents.provisioning_agent import ProvisioningAgent

try:
    from agents.deployment_agent import DeploymentAgent
except ImportError:
    DeploymentAgent = None

app = FastAPI(
    title="Azure Agentic Cloud API (OAuth Multi-Tenant)",
    description="AI-powered autonomous cloud management for Azure",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# --- Custom Access Token Credential Wrapper ---
class OAuthAccessTokenCredential:
    def __init__(self, token: str):
        self.token = token

    def get_token(self, *scopes, **kwargs):
        import time
        # Return the token, set expiration to 1 hour from now as a safe default
        return AccessToken(self.token, int(time.time()) + 3600)

# -------------------------------------------------------------------------
# Pydantic Models
# -------------------------------------------------------------------------
class QueryRequest(BaseModel):
    query: str
    resource_group: str
    subscription_id: str

class OptimizationRequest(BaseModel):
    resource_group: str
    subscription_id: str
    auto_apply: bool = False

def create_orchestrator_for_user(token: str, subscription_id: str):
    credential = OAuthAccessTokenCredential(token)
    llm_client = get_azure_openai_client()
    
    agents_registry = {
        AgentType.RESOURCE_OPTIMIZATION: ResourceOptimizationAgent(subscription_id, credential=credential),
        AgentType.COST_MANAGEMENT: CostManagementAgent(subscription_id, credential=credential),
        AgentType.SECURITY_COMPLIANCE: SecurityComplianceAgent(subscription_id, credential=credential),
        AgentType.PROVISIONING: ProvisioningAgent(subscription_id, llm_client=llm_client, credential=credential)
    }
    
    return OrchestratorAgent(llm_client, agents_registry)

# -------------------------------------------------------------------------
# Core Endpoints
# -------------------------------------------------------------------------
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "azure-agent-system-oauth-multitenant"}

@app.post("/query")
async def process_query(request: QueryRequest, auth: HTTPAuthorizationCredentials = Depends(security)):
    try:
        orchestrator = create_orchestrator_for_user(auth.credentials, request.subscription_id)
        result = orchestrator.process_query(
            query=request.query,
            context={"resource_group": request.resource_group}
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
