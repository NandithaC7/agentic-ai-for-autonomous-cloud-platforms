import json
from mcp.server.fastmcp import FastMCP
from azure.identity import ClientSecretCredential

from agents.resource_agent import ResourceOptimizationAgent
from agents.cost_agent import CostManagementAgent
from agents.security_agent import SecurityComplianceAgent
from agents.deployment_agent import DeploymentAgent
from core.vision import GeminiVisionAgent, GeminiBicepAgent

mcp = FastMCP("Azure Agentic Cloud (Multi-Tenant)")

def get_credential(tenant_id, client_id, client_secret):
    return ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret
    )

# =============================================================================
# RESOURCES — Read-only reference data the AI can consult at any time
# =============================================================================

@mcp.resource("azure://compliance/guidelines")
def get_compliance_guidelines() -> str:
    """Azure compliance and security guidelines that every deployment must follow."""
    return """# Azure Compliance & Security Guidelines

## Network Security
- No VMs should have port 22 (SSH) or 3389 (RDP) exposed to 0.0.0.0/0 (public internet).
- All public-facing services must sit behind an Application Gateway or Azure Front Door.
- Network Security Groups (NSGs) must follow least-privilege rules.

## Compute
- Deallocate VMs when not in use; consider auto-shutdown schedules for dev/test workloads.
- Any VM deallocated for more than 7 days should be reviewed for deletion.
- Unattached managed disks must be deleted within 14 days of detachment.

## Cost Management
- Every resource group must have a monthly budget alert set at 80% and 100% thresholds.
- Reserved Instances should be evaluated for any VM running 24/7 for more than 3 months.
- Tag all resources with: Owner, Environment (Production/Staging/Development), and CostCenter.

## Tagging Policy
- Required tags: `Environment`, `Owner`, `CostCenter`, `Project`
- Resources missing required tags are non-compliant and must be remediated within 48 hours.

## Deployment
- All container images must be built via Azure Container Registry (ACR) Tasks — never locally.
- Infrastructure changes must go through ARM/Bicep templates; no manual portal deployments.
- Secrets must be stored in Azure Key Vault, never in environment variables or code.
"""


@mcp.resource("azure://best-practices/vm-sizing")
def get_vm_sizing_guide() -> str:
    """Reference guide for choosing the right Azure VM size for different workloads."""
    return """# Azure VM Sizing Best Practices

## Web Applications / APIs
- **Recommended:** B2s, B2ms (burstable, cost-effective for low-traffic apps)
- **High traffic:** D4s_v5, D8s_v5 (general purpose, balanced CPU/memory)

## Databases
- **Small/Medium:** E4s_v5, E8s_v5 (memory-optimized)
- **Large / In-Memory:** M32ms, M64s (memory-intensive workloads like SAP HANA)

## Machine Learning / GPU
- **Training:** NC6s_v3, NC24s_v3 (NVIDIA Tesla V100)
- **Inference:** NV6, NV12 (NVIDIA Tesla M60 for visualization)

## Development / Testing
- **Recommended:** B1s, B1ms (cheapest burstable options)
- **Note:** Always use auto-shutdown schedules for dev VMs.

## Cost Optimization Rules
1. If average CPU < 10% over 14 days → downsize by one tier.
2. If average CPU > 80% over 7 days → upsize by one tier.
3. If VM is deallocated > 50% of the month → switch to Spot Instance or delete.
"""


@mcp.resource("azure://best-practices/naming-conventions")
def get_naming_conventions() -> str:
    """Standard naming conventions for Azure resources."""
    return """# Azure Resource Naming Conventions

## Format: {resource-type}-{project}-{environment}-{region}-{instance}

## Examples
| Resource           | Convention                  | Example                  |
|--------------------|-----------------------------|--------------------------|
| Resource Group     | rg-{project}-{env}          | rg-webapp-prod           |
| Virtual Machine    | vm-{project}-{env}-{##}     | vm-api-prod-01           |
| Storage Account    | st{project}{env}            | stwebappprod             |
| Container Registry | cr{project}{env}            | crwebappprod             |
| Virtual Network    | vnet-{project}-{env}        | vnet-webapp-prod         |
| Subnet             | snet-{purpose}-{env}        | snet-backend-prod        |
| NSG                | nsg-{subnet}-{env}          | nsg-backend-prod         |
| Key Vault          | kv-{project}-{env}          | kv-webapp-prod           |
| Container Instance | ci-{app}-{env}              | ci-frontend-staging      |

## Rules
- All names must be lowercase.
- Use hyphens (-) to separate components (except Storage Accounts which require no hyphens).
- Include the environment (prod, staging, dev) in every resource name.
"""


# =============================================================================
# PROMPTS — Pre-built AI instruction templates for complex workflows
# =============================================================================

@mcp.prompt()
def monthly_cloud_audit(tenant_id: str, client_id: str, client_secret: str, subscription_id: str, resource_group: str) -> str:
    """Run a full monthly cloud audit: security scan, cost analysis, idle resource check, and compliance report."""
    return f"""You are an Azure Cloud Auditor. Perform a comprehensive monthly audit for resource group '{resource_group}'.

Credentials:
- tenant_id: {tenant_id}
- client_id: {client_id}
- client_secret: {client_secret}
- subscription_id: {subscription_id}

Execute these steps in order:
1. **Security Scan** — Use `check_security_posture` to scan all VMs for vulnerabilities.
2. **Cost Analysis** — Use `get_resource_costs` to retrieve current resource spending.
3. **Idle Resources** — Use `identify_idle_resources` to find deallocated VMs and wasted resources.
4. **Compliance Check** — Read the `azure://compliance/guidelines` resource and cross-reference your findings.

After completing all steps, generate a professional **Markdown audit report** with these sections:
- Executive Summary (2-3 sentences)
- Security Findings (table of issues)
- Cost Overview (table of resources and estimated costs)
- Idle Resources (list with recommendations)
- Compliance Violations (compare findings against guidelines)
- Action Items (prioritized list of fixes)
"""


@mcp.prompt()
def security_hardening(tenant_id: str, client_id: str, client_secret: str, subscription_id: str, resource_group: str) -> str:
    """Scan for security issues and provide a step-by-step hardening plan."""
    return f"""You are an Azure Security Engineer. Perform a security hardening assessment for resource group '{resource_group}'.

Credentials:
- tenant_id: {tenant_id}
- client_id: {client_id}
- client_secret: {client_secret}
- subscription_id: {subscription_id}

Steps:
1. Use `check_security_posture` to scan all VMs.
2. Use `analyze_vm_utilization` to understand which VMs are actively running.
3. Read the `azure://compliance/guidelines` resource for security policies.
4. For each VM, determine:
   - Is the NSG properly configured?
   - Is disk encryption enabled?
   - Are patches up to date?
5. Generate a **Security Hardening Report** with:
   - Critical Issues (must fix within 24 hours)
   - High Priority (fix within 1 week)
   - Medium Priority (fix within 1 month)
   - Remediation steps for each issue
"""


@mcp.prompt()
def cost_optimization(tenant_id: str, client_id: str, client_secret: str, subscription_id: str, resource_group: str) -> str:
    """Analyze cloud spending and recommend optimizations to reduce costs."""
    return f"""You are an Azure FinOps Analyst. Perform a cost optimization analysis for resource group '{resource_group}'.

Credentials:
- tenant_id: {tenant_id}
- client_id: {client_id}
- client_secret: {client_secret}
- subscription_id: {subscription_id}

Steps:
1. Use `get_resource_costs` to get all resources and their types/locations.
2. Use `identify_idle_resources` to find deallocated or unused resources.
3. Use `analyze_vm_utilization` to check if VMs are right-sized.
4. Read the `azure://best-practices/vm-sizing` resource for sizing guidance.
5. Generate a **Cost Optimization Report** with:
   - Current Resource Inventory (table)
   - Idle Resources (with estimated monthly waste)
   - Right-Sizing Recommendations (which VMs to downsize/upsize)
   - Estimated Monthly Savings
   - Quick Wins (actions that save money immediately)
"""


@mcp.prompt()
def deploy_and_verify(tenant_id: str, client_id: str, client_secret: str, subscription_id: str, resource_group: str, app_name: str, zip_path: str) -> str:
    """Deploy an application and then verify it passes security and compliance checks."""
    return f"""You are a DevOps Engineer. Deploy the application '{app_name}' and verify it meets all compliance standards.

Credentials:
- tenant_id: {tenant_id}
- client_id: {client_id}
- client_secret: {client_secret}
- subscription_id: {subscription_id}

Steps:
1. Read `azure://best-practices/naming-conventions` to verify the app name follows conventions.
2. Use `deploy_code_to_cloud` to deploy '{zip_path}' as '{app_name}' to resource group '{resource_group}'.
3. After deployment, use `check_security_posture` to verify the deployment is secure.
4. Read `azure://compliance/guidelines` to verify compliance.
5. Generate a **Deployment Report** with:
   - Deployment Status (success/failure)
   - Deployed Resources (table)
   - Post-Deployment Security Check Results
   - Compliance Status (pass/fail for each guideline)
   - Any remediation needed
"""


# =============================================================================
# TOOLS — Actions the AI can execute against Azure
# =============================================================================

@mcp.tool()
def analyze_vm_utilization(tenant_id: str, client_id: str, client_secret: str, subscription_id: str, resource_group: str) -> str:
    """Analyze VM utilization in the specified user's Azure resource group. Returns VM names and their current sizes."""
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
    """Retrieve all resources with their type and location for cost analysis in the specified Azure resource group."""
    cred = get_credential(tenant_id, client_id, client_secret)
    agent = CostManagementAgent(subscription_id, credential=cred)
    return json.dumps(agent.get_resource_costs(resource_group), indent=2)

@mcp.tool()
def check_security_posture(tenant_id: str, client_id: str, client_secret: str, subscription_id: str, resource_group: str) -> str:
    """Scan and check the security posture of VMs including NSG, disk encryption, and patch compliance."""
    cred = get_credential(tenant_id, client_id, client_secret)
    agent = SecurityComplianceAgent(subscription_id, credential=cred)
    return json.dumps(agent.check_security_posture(resource_group), indent=2)

@mcp.tool()
def deploy_code_to_cloud(tenant_id: str, client_id: str, client_secret: str, subscription_id: str, resource_group: str, app_name: str, zip_path: str) -> str:
    """Deploy application code from a zip file to Azure Container Instances (ACI) securely via ACR Tasks."""
    cred = get_credential(tenant_id, client_id, client_secret)
    if not DeploymentAgent:
        return json.dumps({"error": "Deployment agent not available."})
    agent = DeploymentAgent(subscription_id, credential=cred)
    return json.dumps(agent.deploy_from_zip(resource_group, app_name, zip_path), indent=2)


@mcp.tool()
def analyze_architecture_diagram(image_path: str) -> str:
    """Analyze a cloud architecture diagram image and extract all Azure resources found in it. Returns a JSON summary of detected resources (VMs, SQL, Web Apps, etc.)."""
    vision = GeminiVisionAgent()
    result = vision.analyze_image(image_path)
    return json.dumps(result, indent=2) if result else json.dumps({"error": "Could not analyze the image. Check the file path and try again."})

@mcp.tool()
def generate_bicep_from_diagram(image_path: str) -> str:
    """Full pipeline: Analyze an architecture diagram image, extract resources, and generate a deployable Bicep (Infrastructure-as-Code) template. Returns the Bicep code as a string."""
    vision = GeminiVisionAgent()
    arch_data = vision.analyze_image(image_path)
    if not arch_data:
        return json.dumps({"error": "Vision analysis returned empty results."})
    coder = GeminiBicepAgent()
    bicep_code = coder.generate_bicep(arch_data)
    if not bicep_code:
        return json.dumps({"error": "Failed to generate Bicep code from the detected resources."})
    return json.dumps({"detected_resources": arch_data, "bicep_code": bicep_code}, indent=2)


# --- Additional Prompt: Diagram to Deployment ---

@mcp.prompt()
def diagram_to_deployment(image_path: str, tenant_id: str, client_id: str, client_secret: str, subscription_id: str, resource_group: str) -> str:
    """Analyze an architecture diagram, generate Bicep IaC, and optionally deploy it — a complete draw-to-deploy pipeline."""
    return f"""You are a Cloud Solutions Architect. A user has provided an architecture diagram at '{image_path}'.

Credentials for deployment:
- tenant_id: {tenant_id}
- client_id: {client_id}
- client_secret: {client_secret}
- subscription_id: {subscription_id}
- resource_group: {resource_group}

Execute these steps:
1. Use `analyze_architecture_diagram` to extract all Azure resources from the diagram image.
2. Use `generate_bicep_from_diagram` to generate a deployable Bicep template.
3. Read `azure://best-practices/naming-conventions` to verify resource names follow standards.
4. Read `azure://compliance/guidelines` to check for compliance issues in the generated template.
5. Present the results in a clear report:
   - Detected Resources (table)
   - Generated Bicep Code (code block)
   - Naming Convention Compliance (pass/fail per resource)
   - Security/Compliance Notes
   - Recommended next steps for deployment
"""


if __name__ == "__main__":
    mcp.run(transport='stdio')
