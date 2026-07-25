from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.containerregistry import ContainerRegistryManagementClient
from azure.mgmt.containerregistry.models import DockerBuildRequest, PlatformProperties, Architecture, OS
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
import os
import uuid
from datetime import datetime, timedelta

def test():
    pass
