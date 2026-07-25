# ☁️ Agentic AI for Autonomous Cloud Platforms

> **AI-powered autonomous cloud management built on the Model Context Protocol (MCP)**

An intelligent, multi-agent system that uses LLMs to autonomously manage, monitor, optimize, and secure Azure cloud infrastructure. Built with a dual architecture — a **React web dashboard** for end-users and an **MCP server** for AI-native tool orchestration via [NitroStack](https://nitrostack.dev), Claude Desktop, or any MCP-compatible client.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **Multi-Agent Orchestration** | 5 specialized AI agents coordinate through a central Orchestrator powered by Gemini |
| 🔐 **Microsoft OAuth Login** | Users authenticate with their Microsoft account — no secrets pasted into forms |
| 📡 **MCP Server** | Expose all agent capabilities as standardized MCP tools, prompts, and resources |
| 🛡️ **Security Scanner** | Automatically checks NSG rules, disk encryption, and patch compliance |
| 💰 **Cost Optimizer** | Finds idle VMs, unattached disks, and recommends right-sizing |
| 🚀 **Zero-Touch Deployment** | Upload a `.zip` → auto-build via ACR Tasks → deploy to Azure Container Instances |
| 📋 **Built-in Compliance** | AI reads compliance guidelines as MCP Resources before making decisions |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACES                          │
│                                                                 │
│   ┌───────────────────┐         ┌────────────────────────────┐  │
│   │  React Dashboard  │         │   NitroStack / Claude      │  │
│   │  (OAuth Login)    │         │   (MCP Client)             │  │
│   └────────┬──────────┘         └─────────────┬──────────────┘  │
│            │ REST API + Bearer Token           │ MCP (stdio)    │
└────────────┼───────────────────────────────────┼────────────────┘
             │                                   │
┌────────────┼───────────────────────────────────┼────────────────┐
│            ▼                                   ▼                │
│   ┌─────────────┐                    ┌──────────────────┐       │
│   │   api.py    │                    │  mcp_server.py   │       │
│   │  (FastAPI)  │                    │  (FastMCP)       │       │
│   └──────┬──────┘                    └────────┬─────────┘       │
│          │                                    │                 │
│          ▼                                    ▼                 │
│   ┌─────────────────────────────────────────────────┐           │
│   │              ORCHESTRATOR AGENT                  │           │
│   │         (Gemini LLM — Routes Queries)            │           │
│   └──────────┬──────┬──────┬──────┬──────┬──────────┘           │
│              │      │      │      │      │                      │
│              ▼      ▼      ▼      ▼      ▼                      │
│   ┌──────┐┌──────┐┌──────┐┌──────┐┌──────────┐                 │
│   │Resrc ││Cost  ││Secur ││Prov  ││Deploy    │                 │
│   │Optim ││Mgmt  ││Compl ││ision ││Agent     │                 │
│   └──┬───┘└──┬───┘└──┬───┘└──┬───┘└────┬─────┘                 │
│      │       │       │       │         │                        │
│      ▼       ▼       ▼       ▼         ▼                        │
│   ┌─────────────────────────────────────────────────┐           │
│   │              AZURE SDK (User's Cloud)            │           │
│   └─────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🤖 The 5 AI Agents

| Agent | Purpose | Azure SDK Used |
|-------|---------|----------------|
| **ResourceOptimizationAgent** | Analyzes VM utilization and finds idle/deallocated resources | `azure-mgmt-compute` |
| **CostManagementAgent** | Retrieves resource inventory for cost analysis | `azure-mgmt-resource` |
| **SecurityComplianceAgent** | Scans VMs for NSG config, disk encryption, patch compliance | `azure-mgmt-compute` |
| **ProvisioningAgent** | Creates VMs, VNets, Subnets via ARM | `azure-mgmt-compute`, `azure-mgmt-network` |
| **DeploymentAgent** | Builds images via ACR Tasks, deploys to ACI | `azure-mgmt-containerregistry`, `azure-mgmt-containerinstance` |

---

## 📡 MCP Server — Powered by Model Context Protocol

The `mcp_server.py` exposes the agent system as an MCP-compliant server with **Tools**, **Prompts**, and **Resources**.

### Tools (5)
Actions the AI can execute against your Azure cloud:

| Tool | Description |
|------|-------------|
| `analyze_vm_utilization` | List VMs and their current sizes in a resource group |
| `identify_idle_resources` | Find deallocated VMs and wasted resources |
| `get_resource_costs` | Get all resources with types and locations for cost analysis |
| `check_security_posture` | Scan VMs for NSG, encryption, and patch compliance |
| `deploy_code_to_cloud` | Deploy a zip file to ACI via ACR Tasks |

### Prompts (4)
Pre-built AI instruction templates for complex multi-step workflows:

| Prompt | Description |
|--------|-------------|
| `monthly_cloud_audit` | Full audit: security → costs → idle resources → compliance report |
| `security_hardening` | Deep security scan with prioritized remediation plan |
| `cost_optimization` | FinOps analysis with right-sizing recommendations |
| `deploy_and_verify` | Deploy app → security scan → compliance check → report |

### Resources (3)
Read-only reference data the AI consults for decision-making:

| Resource URI | Description |
|-------------|-------------|
| `azure://compliance/guidelines` | Security, cost, tagging, and deployment compliance rules |
| `azure://best-practices/vm-sizing` | VM sizing guide for different workload types |
| `azure://best-practices/naming-conventions` | Standard naming conventions for Azure resources |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- An Azure account (for connecting to real cloud resources)
- A [Gemini API Key](https://aistudio.google.com/) (free tier available)

### 1. Clone & Install

```bash
git clone https://github.com/NandithaC7/agentic-ai-for-autonomous-cloud-platforms.git
cd agentic-ai-for-autonomous-cloud-platforms

# Backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 2. Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your-gemini-api-key-here
```

That's it! Azure credentials are provided per-request by the user (via OAuth or MCP tool arguments).

### 3. Run the React Dashboard

```bash
# Terminal 1 — Backend
source venv/bin/activate
uvicorn api:app --reload

# Terminal 2 — Frontend
cd frontend
npm run dev
```

Open `http://localhost:5173` and click **Login with Microsoft**.

---

## 🔌 Connect to MCP Clients

### NitroStack / NitroStudio

1. Open NitroStudio → **Add / Manage Projects**
2. Set the command:
   - **Command:** `/path/to/project/venv/bin/python`
   - **Arguments:** `/path/to/project/mcp_server.py`
3. Add environment variable: `GEMINI_API_KEY=your-key`
4. Click Connect — you'll see all Tools, Prompts, and Resources appear on the canvas.

### Claude Desktop

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "azure-agentic-cloud": {
      "command": "/path/to/project/venv/bin/python",
      "args": ["/path/to/project/mcp_server.py"],
      "env": {
        "GEMINI_API_KEY": "your-key"
      }
    }
  }
}
```

Restart Claude Desktop. The Azure tools will appear in Claude's tool picker.

### Any MCP Client (Generic)

The server uses **stdio** transport. Launch it with:

```bash
venv/bin/python mcp_server.py
```

---

## 📋 Example Prompts

See [`examples/nitrostack_prompts.md`](examples/nitrostack_prompts.md) for ready-to-use prompts you can paste into NitroStack or Claude Desktop.

**Quick examples:**

```
# Monthly Audit (chains 4 tools + 1 resource)
"Perform a monthly cloud audit for resource group 'my-rg-prod'"

# Cost Optimization
"Analyze spending in 'my-rg-dev' and recommend ways to cut costs"

# Security Hardening
"Scan 'my-rg-prod' for security issues and give me a prioritized fix list"

# Deploy + Verify
"Deploy my-app.zip to staging and verify it passes security checks"
```

---

## 📁 Project Structure

```
├── agents/
│   ├── base_agent.py            # Base class with Azure SDK clients
│   ├── orchestrator.py          # LLM-powered query router
│   ├── resource_agent.py        # VM utilization & idle resource detection
│   ├── cost_agent.py            # Cost & resource inventory analysis
│   ├── security_agent.py        # Security posture scanning
│   ├── provisioning_agent.py    # VM/VNet/Subnet provisioning
│   └── deployment_agent.py      # ACR build + ACI deployment
├── core/
│   ├── llm.py                   # Gemini LLM client wrapper
│   └── vision.py                # Gemini Vision agent
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Main app with MSAL auth
│   │   ├── authConfig.js        # Microsoft OAuth configuration
│   │   └── components/          # React UI components
│   └── package.json
├── examples/
│   └── nitrostack_prompts.md    # Ready-to-use AI prompts
├── mcp_server.py                # MCP server (Tools + Prompts + Resources)
├── api.py                       # FastAPI REST backend (OAuth)
├── main.py                      # CLI entry point
├── requirements.txt
└── README.md
```

---

## 🛡️ Security Model

| Component | Auth Method |
|-----------|-------------|
| React Dashboard | Microsoft OAuth 2.0 (MSAL) — user logs in with their Microsoft account |
| MCP Server (NitroStack) | Service Principal credentials passed per-tool-call (multi-tenant) |
| Azure SDK | `OAuthAccessTokenCredential` (web) or `ClientSecretCredential` (MCP) |
| Gemini API | `GEMINI_API_KEY` env var (server-side only) |

- No Azure credentials are stored on the server.
- No local `docker build` — all image builds happen securely in Azure via ACR Tasks.
- Secrets are never logged or persisted.

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|-----------|
| AI/LLM | Google Gemini (via `google-genai` SDK) |
| Agent Protocol | Model Context Protocol (MCP) via `FastMCP` |
| Backend | Python, FastAPI, Azure SDK |
| Frontend | React, Vite, MSAL.js |
| MCP Client | NitroStack / NitroStudio, Claude Desktop |
| Cloud | Microsoft Azure (Compute, Storage, ACR, ACI, NSG) |

---

## 📄 License

This project is open source under the [MIT License](LICENSE).

---

<p align="center">
  Built with ❤️ using <strong>Model Context Protocol</strong> and <strong>NitroStack</strong>
</p>
