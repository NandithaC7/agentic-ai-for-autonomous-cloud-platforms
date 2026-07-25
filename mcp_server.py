import json
from mcp.server.fastmcp import FastMCP
from azure.identity import ClientSecretCredential

from agents.resource_agent import ResourceOptimizationAgent
from agents.cost_agent import CostManagementAgent
from agents.security_agent import SecurityComplianceAgent
from agents.deployment_agent import DeploymentAgent

mcp = FastMCP("Azure Agentic Cloud (Multi-Tenant)")

def get_credential(tenant_id, client_id, client_secret):
    return ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret
    )

@mcp.tool()
def analyze_vm_utilization(tenant_id: str, client_id: str, client_secret: str, subscription_id: str, resource_group: str) -> str:
    """Analyze VM utilization in the specified user's Azure resource group."""
    cred = get_credential(tenant_id, client_id, client_secret)
    agent = ResourceOptimizationAgent(subscription_id, credential=cred)
    return json.dumps(agent.analyze_vm_utilization(resource_group), indent=2)

@mcp.tool()
def identify_idle_resources(tenant_id: str, client_id: str, client_secret: str, subscription_id: str, resource_group: str) -> str:
    """Identify idle resources (e.g., deallocated VMs) in the specified Azure resource group."""
    cred = get_credential(tenant_id, client_id, client_secret)
    agent = ResourceOptimizationAgent(subscription_id, credential=cred)
    return json.dumps(agent.identify_idle_resources(resource_group), indent=2)

@mcp.tool()
def get_resource_costs(tenant_id: str, client_id: str, client_secret: str, subscription_id: str, resource_group: str) -> str:
    """Retrieve basic resource type and location data for the specified Azure resource group."""
    cred = get_credential(tenant_id, client_id, client_secret)
    agent = CostManagementAgent(subscription_id, credential=cred)
    return json.dumps(agent.get_resource_costs(resource_group), indent=2)

@mcp.tool()
def check_security_posture(tenant_id: str, client_id: str, client_secret: str, subscription_id: str, resource_group: str) -> str:
    """Scan and check the security posture of VMs in the specified Azure resource group."""
    cred = get_credential(tenant_id, client_id, client_secret)
    agent = SecurityComplianceAgent(subscription_id, credential=cred)
    return json.dumps(agent.check_security_posture(resource_group), indent=2)

@mcp.tool()
def deploy_code_to_cloud(tenant_id: str, client_id: str, client_secret: str, subscription_id: str, resource_group: str, upload_file_path: str, app_name: str) -> str:
    """Deploy application directly to ACI for the multi-tenant user using ACR tasks."""
    cred = get_credential(tenant_id, client_id, client_secret)
    agent = DeploymentAgent(subscription_id, credential=cred)
    result = agent.deploy_to_container(upload_file_path, app_name, resource_group)
    return json.dumps(result, indent=2)

if __name__ == "__main__":
    mcp.run(transport='stdio')
