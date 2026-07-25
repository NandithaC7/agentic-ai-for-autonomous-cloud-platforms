import os
import zipfile
import tempfile
import uuid
import json
import time
from datetime import datetime, timedelta

from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.containerregistry import ContainerRegistryManagementClient
from azure.mgmt.containerregistry.models import DockerBuildRequest, PlatformProperties, Architecture, OS
from azure.mgmt.resource import ResourceManagementClient
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from azure.identity import DefaultAzureCredential

class DeploymentAgent:
    """
    Agent for deploying user applications to Azure Container Instances dynamically in the user's cloud.
    """
    
    DOCKERFILE_TEMPLATES = {
        "nodejs": "FROM node:18-alpine\nWORKDIR /app\nCOPY package*.json ./\nRUN npm install --production\nCOPY . .\nEXPOSE 3000\nCMD [\"npm\", \"start\"]\n",
        "python": "FROM python:3.11-slim\nWORKDIR /app\nCOPY requirements.txt ./\nRUN pip install --no-cache-dir -r requirements.txt\nCOPY . .\nEXPOSE 8000\nCMD [\"python\", \"app.py\"]\n",
        "python-flask": "FROM python:3.11-slim\nWORKDIR /app\nCOPY requirements.txt ./\nRUN pip install --no-cache-dir -r requirements.txt\nCOPY . .\nEXPOSE 5000\nCMD [\"python\", \"app.py\"]\n",
        "python-fastapi": "FROM python:3.11-slim\nWORKDIR /app\nCOPY requirements.txt ./\nRUN pip install --no-cache-dir -r requirements.txt\nCOPY . .\nEXPOSE 8000\nCMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]\n",
        "go": "FROM golang:1.21-alpine AS builder\nWORKDIR /app\nCOPY go.* ./\nRUN go mod download\nCOPY . .\nRUN go build -o main .\n\nFROM alpine:latest\nWORKDIR /root/\nCOPY --from=builder /app/main .\nEXPOSE 8080\nCMD [\"./main\"]\n",
        "static": "FROM nginx:alpine\nCOPY . /usr/share/nginx/html/\nRUN chmod -R 755 /usr/share/nginx/html && chown -R nginx:nginx /usr/share/nginx/html\nEXPOSE 80\nCMD [\"nginx\", \"-g\", \"daemon off;\"]\n"
    }
    
    def __init__(self, subscription_id, credential=None):
        self.subscription_id = subscription_id
        self.credential = credential or DefaultAzureCredential()
        self.container_client = ContainerInstanceManagementClient(self.credential, subscription_id)
        self.acr_client = ContainerRegistryManagementClient(self.credential, subscription_id)
        self.storage_client = StorageManagementClient(self.credential, subscription_id)
        self.resource_client = ResourceManagementClient(self.credential, subscription_id)

    def ensure_infrastructure(self, resource_group):
        """Ensures that a Storage Account and ACR exist in the given resource group."""
        print(f"Ensuring infrastructure exists in resource group: {resource_group}")
        # Get RG location
        rg_info = self.resource_client.resource_groups.get(resource_group)
        location = rg_info.location

        # Find or create Storage Account
        storage_accounts = list(self.storage_client.storage_accounts.list_by_resource_group(resource_group))
        if storage_accounts:
            storage_account = storage_accounts[0]
            storage_name = storage_account.name
            print(f"Using existing Storage Account: {storage_name}")
        else:
            storage_name = f"st{uuid.uuid4().hex[:16]}"
            print(f"Creating Storage Account: {storage_name}...")
            poller = self.storage_client.storage_accounts.begin_create(
                resource_group,
                storage_name,
                {"location": location, "sku": {"name": "Standard_LRS"}, "kind": "StorageV2"}
            )
            poller.result()
            print("Storage Account created.")

        # Find or create ACR
        registries = list(self.acr_client.registries.list_by_resource_group(resource_group))
        if registries:
            registry = registries[0]
            acr_name = registry.name
            print(f"Using existing ACR: {acr_name}")
        else:
            acr_name = f"acr{uuid.uuid4().hex[:16]}"
            print(f"Creating ACR: {acr_name}...")
            poller = self.acr_client.registries.begin_create(
                resource_group,
                acr_name,
                {"location": location, "sku": {"name": "Basic"}, "admin_user_enabled": True}
            )
            poller.result()
            print("ACR created.")

        return storage_name, acr_name, location

    def upload_to_storage(self, file_path, storage_name, resource_group, container_name="deployments"):
        """Uploads project to Azure Storage and generates a SAS URL for ACR Tasks."""
        # Get storage account keys
        keys = self.storage_client.storage_accounts.list_keys(resource_group, storage_name)
        account_key = keys.keys[0].value
        
        connection_string = f"DefaultEndpointsProtocol=https;AccountName={storage_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        try:
            container_client = blob_service_client.get_container_client(container_name)
            if not container_client.exists():
                blob_service_client.create_container(container_name)
        except Exception:
            blob_service_client.create_container(container_name)
        
        # We must upload the zip file. Since it's a directory, we need to zip it.
        # Wait, file_path is already a zip file from the API request or it's a directory?
        # The user uploads a zip file. Let's assume file_path is the zip file.
        blob_name = f"{uuid.uuid4()}.zip"
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
            
        print(f"Uploaded to {blob_name}")
        
        # Generate SAS token
        sas_token = generate_blob_sas(
            account_name=storage_name,
            container_name=container_name,
            blob_name=blob_name,
            account_key=account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=2)
        )
        
        sas_url = f"https://{storage_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"
        return blob_name, sas_url

    def download_from_storage(self, blob_name, storage_name, resource_group, container_name="deployments"):
        keys = self.storage_client.storage_accounts.list_keys(resource_group, storage_name)
        account_key = keys.keys[0].value
        connection_string = f"DefaultEndpointsProtocol=https;AccountName={storage_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        with open(temp_zip.name, "wb") as f:
            f.write(blob_client.download_blob().readall())
        return temp_zip.name

    def extract_project(self, zip_path):
        extract_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        return extract_dir

    def detect_project_type(self, project_dir):
        files_in_root = os.listdir(project_dir)
        if 'package.json' in files_in_root:
            pkg_path = os.path.join(project_dir, 'package.json')
            try:
                with open(pkg_path, 'r') as f:
                    pkg_data = json.load(f)
                    if 'scripts' in pkg_data and 'start' in pkg_data['scripts']:
                        return 'nodejs', 3000
            except: pass
        if 'requirements.txt' in files_in_root:
            with open(os.path.join(project_dir, 'requirements.txt'), 'r') as f:
                content = f.read().lower()
                if 'flask' in content: return 'python-flask', 5000
                elif 'fastapi' in content or 'uvicorn' in content: return 'python-fastapi', 8000
                else: return 'python', 8000
        if 'go.mod' in files_in_root: return 'go', 8080
        return 'static', 80

    def generate_dockerfile(self, project_dir, project_type):
        dockerfile_path = os.path.join(project_dir, 'Dockerfile')
        if os.path.exists(dockerfile_path): return dockerfile_path
        template = self.DOCKERFILE_TEMPLATES.get(project_type, self.DOCKERFILE_TEMPLATES['static'])
        with open(dockerfile_path, 'w') as f:
            f.write(template)
        return dockerfile_path

    def build_image_via_acr_task(self, sas_url, acr_name, image_name, resource_group):
        """Uses ACR Tasks to build the Docker image securely in Azure."""
        print(f"Triggering ACR Task to build image {image_name}...")
        
        build_request = DockerBuildRequest(
            source_location=sas_url,
            image_names=[f"{image_name}:latest"],
            is_push_enabled=True,
            platform=PlatformProperties(
                os=OS.LINUX,
                architecture=Architecture.AMD64
            ),
            docker_file_path="Dockerfile"
        )
        
        poller = self.acr_client.registries.begin_schedule_run(
            resource_group_name=resource_group,
            registry_name=acr_name,
            run_request=build_request
        )
        run = poller.result()
        print(f"ACR Task triggered successfully. Run ID: {run.run_id}")
        
        # Wait for the build to complete
        while True:
            run_status = self.acr_client.runs.get(resource_group, acr_name, run.run_id)
            if run_status.status in ['Succeeded', 'Failed', 'Canceled', 'Error', 'Timeout']:
                if run_status.status != 'Succeeded':
                    raise Exception(f"ACR Build failed with status: {run_status.status}")
                break
            print(f"Build status: {run_status.status}. Waiting 10 seconds...")
            time.sleep(10)
            
        print("ACR Build completed successfully!")
        return f"{acr_name}.azurecr.io/{image_name}:latest"

    def deploy_to_container(self, upload_file_path, app_name, resource_group):
        """Deploy application directly to ACI for the multi-tenant user."""
        try:
            # 1. Ensure infrastructure
            storage_name, acr_name, location = self.ensure_infrastructure(resource_group)
            
            # We need to process the zip to ensure it has a Dockerfile.
            # Extract it locally on backend
            extract_dir = self.extract_project(upload_file_path)
            project_type, port = self.detect_project_type(extract_dir)
            self.generate_dockerfile(extract_dir, project_type)
            
            # Zip it back up with the Dockerfile
            new_zip_path = tempfile.NamedTemporaryFile(delete=False, suffix='.zip').name
            import shutil
            shutil.make_archive(new_zip_path.replace('.zip', ''), 'zip', extract_dir)
            
            # 2. Upload to storage and get SAS
            blob_name, sas_url = self.upload_to_storage(new_zip_path, storage_name, resource_group)
            
            # 3. Build via ACR task
            deployment_id = str(uuid.uuid4())[:8]
            image_name = f"app-{deployment_id}"
            full_image_name = self.build_image_via_acr_task(sas_url, acr_name, image_name, resource_group)
            
            # 4. Deploy to ACI
            container_group_name = f"{app_name}-{deployment_id}"
            print(f"Deploying to ACI: {container_group_name}")
            
            # Get ACR Credentials (admin user)
            creds = self.acr_client.registries.list_credentials(resource_group, acr_name)
            acr_password = creds.passwords[0].value
            
            container_group = {
                "location": location,
                "containers": [{
                    "name": container_group_name,
                    "image": full_image_name,
                    "resources": {"requests": {"cpu": 1.0, "memory_in_gb": 1.5}},
                    "ports": [{"port": port}]
                }],
                "os_type": "Linux",
                "ip_address": {
                    "type": "Public",
                    "ports": [{"protocol": "TCP", "port": port}]
                },
                "image_registry_credentials": [{
                    "server": f"{acr_name}.azurecr.io",
                    "username": acr_name,
                    "password": acr_password
                }],
                "restart_policy": "Always"
            }
            
            poller = self.container_client.container_groups.begin_create_or_update(
                resource_group, container_group_name, container_group
            )
            
            return {
                "deployment_id": deployment_id,
                "container_group_name": container_group_name,
                "status": "deploying",
                "message": f"Deploying {project_type} application to {location}"
            }
        except Exception as e:
            print(f"Deployment error: {str(e)}")
            raise Exception(f"Deployment failed: {str(e)}")

    def get_deployment_status(self, container_group_name, resource_group):
        try:
            cg = self.container_client.container_groups.get(resource_group, container_group_name)
            prov_state = cg.provisioning_state
            cont_state = "Unknown"
            if cg.containers and len(cg.containers) > 0 and cg.containers[0].instance_view:
                if cg.containers[0].instance_view.current_state:
                    cont_state = cg.containers[0].instance_view.current_state.state
            url = None
            if cg.ip_address and cg.ip_address.ip:
                url = f"http://{cg.ip_address.ip}"
            
            return {
                "status": "succeeded" if (prov_state == "Succeeded" and cont_state in ["Running", "Succeeded"]) else "deploying",
                "state": f"{prov_state} - Container: {cont_state}",
                "url": url
            }
        except Exception as e:
            return {"status": "failed", "message": str(e)}

    def get_logs(self, container_name, resource_group):
        try:
            logs = self.container_client.containers.list_logs(resource_group, container_name, container_name)
            return logs.content.split('\n') if logs.content else []
        except: return []
