# NitroStack Example Prompts

Use these prompts in **NitroStack AI Chat** or **Composer** to see the Agentic AI system in action.
Replace the placeholder credentials with your actual Azure Service Principal details.

---

## 1. Monthly Cloud Audit (Full Pipeline)

> Select the **monthly_cloud_audit** prompt from the Prompts tab, or paste this into AI Chat:

```
Perform a comprehensive monthly cloud audit for my resource group 'my-rg-prod'.

Use these credentials:
- tenant_id: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
- client_id: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
- client_secret: your-client-secret-here
- subscription_id: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

Steps:
1. Run the security scanner to check for vulnerabilities.
2. Run the cost management tool to get current spending.
3. Check for idle or underutilized resources.
4. Read the compliance guidelines and cross-reference findings.
5. Generate a professional Markdown audit report.
```

**What happens:** The AI will chain `check_security_posture` → `get_resource_costs` → `identify_idle_resources` → read `azure://compliance/guidelines` → generate a multi-section Markdown report.

---

## 2. Security Hardening Assessment

```
You are an Azure Security Engineer. Scan my resource group 'my-rg-prod' for security issues.

Credentials:
- tenant_id: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
- client_id: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
- client_secret: your-client-secret-here
- subscription_id: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

1. Check security posture of all VMs.
2. Analyze VM utilization to see which ones are actively running.
3. Read the compliance guidelines.
4. Generate a Security Hardening Report with Critical, High, and Medium priority issues.
```

**What happens:** The AI chains `check_security_posture` → `analyze_vm_utilization` → reads compliance guidelines → produces a prioritized remediation plan.

---

## 3. Cost Optimization Analysis

```
Analyze my cloud spending and recommend cost optimizations for resource group 'my-rg-dev'.

Credentials:
- tenant_id: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
- client_id: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
- client_secret: your-client-secret-here
- subscription_id: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

1. Get all resources and their costs.
2. Find idle resources that are wasting money.
3. Analyze VM utilization to check if VMs are right-sized.
4. Read the VM sizing best practices guide.
5. Generate a Cost Optimization Report with estimated savings.
```

**What happens:** The AI chains `get_resource_costs` → `identify_idle_resources` → `analyze_vm_utilization` → reads `azure://best-practices/vm-sizing` → outputs a FinOps report.

---

## 4. Deploy and Verify (Self-Healing Workflow)

```
Deploy my application 'my-web-app' from '/path/to/app.zip' to resource group 'my-rg-staging'.

Credentials:
- tenant_id: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
- client_id: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
- client_secret: your-client-secret-here
- subscription_id: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

1. Check naming conventions to make sure 'my-web-app' follows our standards.
2. Deploy the app.
3. After deployment, run a security scan on the resource group.
4. Check compliance guidelines.
5. If any issues are found, provide remediation steps.
```

**What happens:** The AI reads `azure://best-practices/naming-conventions` → calls `deploy_code_to_cloud` → runs `check_security_posture` → reads compliance guidelines → generates a deployment report.

---

## 5. Quick Single-Tool Commands

These are simple one-shot commands you can type directly into NitroStack AI Chat:

### Check VM sizes
```
Analyze the VM utilization in my resource group 'my-rg-prod'.
tenant_id: xxx, client_id: xxx, client_secret: xxx, subscription_id: xxx
```

### Find wasted resources
```
Find all idle and deallocated resources in resource group 'my-rg-dev'.
tenant_id: xxx, client_id: xxx, client_secret: xxx, subscription_id: xxx
```

### Security scan
```
Run a security scan on resource group 'my-rg-prod' and tell me if any VMs have issues.
tenant_id: xxx, client_id: xxx, client_secret: xxx, subscription_id: xxx
```

---

## Tips for NitroStack Composer

- **Chain tools visually:** In Composer, drag tools from the canvas and connect them to create visual workflows.
- **Use Resources as context:** When building a workflow, add a "Read Resource" step before the action step so the AI always has compliance guidelines in context.
- **Record demos:** Use NitroStack's screen recording or take screenshots of the AI executing multi-step workflows — these are great for your portfolio!
