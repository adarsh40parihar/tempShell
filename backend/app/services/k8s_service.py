from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream
from app.core.config import settings
import hashlib
import secrets  # Secure unique pod name banana
import logging
import time

logger = logging.getLogger(__name__)

class K8sService:
    """Service for managing Kubernetes pods for user shells"""
    
    def __init__(self):
        """Initialize Kubernetes client"""
        self.v1 = None
        self.namespace = settings.K8S_NAMESPACE
        self.enabled = False
        
        try:
            # Try in-cluster config first (for production)
            config.load_incluster_config()
            self.v1 = client.CoreV1Api()
            self.enabled = True
            logger.info("Loaded in-cluster Kubernetes configuration")
        except Exception as e:
            try:
                # Fall back to local kubeconfig (for development)
                config.load_kube_config()
                self.v1 = client.CoreV1Api()
                self.enabled = True
                logger.info("Loaded local Kubernetes configuration")
            except Exception as e2:
                logger.warning(f"Kubernetes not available: {e2}. Shell functionality disabled for local development.")
                self.enabled = False
    
    def create_user_pod(self, username: str) -> str:
        """Create an isolated pod for user shell sessions"""
        if not self.enabled:
            raise Exception("Kubernetes not available. Shell functionality disabled for local development.")
        
        # Generate unique pod ID
        pod_id = hashlib.sha256(
            f"{username}-{secrets.token_hex(16)}-{int(time.time())}".encode()
        ).hexdigest()[:32]
        
        # Security context for strict isolation
        security_context = client.V1SecurityContext(
            run_as_non_root=True,
            run_as_user=1000,
            run_as_group=1000,
            allow_privilege_escalation=False,
            read_only_root_filesystem=False,
            capabilities=client.V1Capabilities(
                drop=["ALL"],
                add=["NET_BIND_SERVICE"]  # Only allow binding to ports
            )
        )
        
        # Resource limits to prevent resource exhaustion
        resources = client.V1ResourceRequirements(
            requests={
                "cpu": settings.POD_CPU_REQUEST,
                "memory": settings.POD_MEMORY_REQUEST
            },
            limits={
                "cpu": settings.POD_CPU_LIMIT,
                "memory": settings.POD_MEMORY_LIMIT
            }
        )
        
        # Pod specification
        pod = client.V1Pod(
            metadata=client.V1ObjectMeta(
                name=pod_id,
                labels={
                    "app": "tempshell",
                    "user": username,
                    "managed-by": "tempshell-backend"
                },
                annotations={
                    "created-at": str(int(time.time()))
                }
            ),
            spec=client.V1PodSpec(
                containers=[
                    client.V1Container(
                        name="shell",
                        image=settings.POD_IMAGE,
                        image_pull_policy="Never",  # Use local image, don't pull from registry
                        command=["sleep", str(settings.POD_TIMEOUT_SECONDS)],
                        security_context=security_context,
                        resources=resources,
                        env=[
                            client.V1EnvVar(name="USER", value="tempuser"),
                            client.V1EnvVar(name="HOME", value="/home/tempuser")
                        ]
                    )
                ],
                restart_policy="Never",
                automount_service_account_token=False  # Don't mount service account
            )
        )
        
        try:
            self.v1.create_namespaced_pod(namespace=self.namespace, body=pod)
            logger.info(f"Created pod {pod_id} for user {username}")
            
            # Wait for pod to be ready
            self._wait_for_pod_ready(pod_id)
            
            return pod_id
        except ApiException as e:
            logger.error(f"Failed to create pod: {e}")
            raise Exception(f"Failed to create shell environment: {e.reason}")
    
    def _wait_for_pod_ready(self, pod_id: str, timeout: int = 60):
        """Wait for pod to be in running state"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                pod = self.v1.read_namespaced_pod(name=pod_id, namespace=self.namespace)
                if pod.status.phase == "Running":
                    logger.info(f"Pod {pod_id} is ready")
                    return
            except ApiException as e:
                logger.warning(f"Error checking pod status: {e}")
            
            time.sleep(2)
        
        raise Exception("Pod failed to become ready within timeout")
    
    def execute_command(self, pod_id: str, command: str) -> tuple:
        """Execute command in pod and return output and exit code"""
        if not self.enabled:
            raise Exception("Kubernetes not available. Shell functionality disabled for local development.")
        
        try:
            cmd = ["/bin/sh", "-c", command]
            
            resp = stream(
                self.v1.connect_get_namespaced_pod_exec,
                pod_id,
                self.namespace,
                command=cmd,
                stderr=True,
                stdin=False,
                stdout=True,
                tty=False,
                _preload_content=False
            )
            
            output = ""
            error_output = ""
            
            while resp.is_open():
                resp.update(timeout=1)
                if resp.peek_stdout():
                    output += resp.read_stdout()
                if resp.peek_stderr():
                    error_output += resp.read_stderr()
            
            # Combine stdout and stderr
            full_output = output
            if error_output:
                full_output += "\n" + error_output
            
            exit_code = resp.returncode if hasattr(resp, 'returncode') else 0
            
            logger.info(f"Command executed in pod {pod_id}: exit_code={exit_code}")
            return full_output.strip() if full_output else "(no output)", exit_code
            
        except ApiException as e:
            logger.error(f"Command execution failed in pod {pod_id}: {e}")
            return f"Error: {e.reason}", 1
        except Exception as e:
            logger.error(f"Unexpected error during command execution: {e}")
            return f"Error: {str(e)}", 1
    
    def delete_pod(self, pod_id: str):
        """Delete user pod"""
        try:
            self.v1.delete_namespaced_pod(
                name=pod_id,
                namespace=self.namespace,
                body=client.V1DeleteOptions(
                    grace_period_seconds=5
                )
            )
            logger.info(f"Deleted pod {pod_id}")
        except ApiException as e:
            if e.status != 404:  # Ignore not found errors
                logger.error(f"Failed to delete pod {pod_id}: {e}")
                raise Exception(f"Failed to delete shell environment: {e.reason}")
    
    def get_pod_status(self, pod_id: str) -> dict:
        """Get status of a pod"""
        try:
            pod = self.v1.read_namespaced_pod(name=pod_id, namespace=self.namespace)
            return {
                "status": pod.status.phase,
                "created_at": pod.metadata.creation_timestamp
            }
        except ApiException as e:
            if e.status == 404:
                return {"status": "not_found", "created_at": None}
            logger.error(f"Failed to get pod status: {e}")
            return {"status": "error", "created_at": None}
    
    def cleanup_old_pods(self):
        """Clean up all old tempshell user pods (except running ones)"""
        if not self.enabled:
            logger.warning("Kubernetes not available. Skipping pod cleanup.")
            return
        
        try:
            # List all pods with tempshell label
            pods = self.v1.list_namespaced_pod(
                namespace=self.namespace,
                label_selector="managed-by=tempshell-backend"
            )
            
            cleaned_count = 0
            for pod in pods.items:
                pod_name = pod.metadata.name
                pod_status = pod.status.phase
                
                # Delete pods that are not Running (Failed, Succeeded, Unknown, etc.)
                if pod_status in ["Failed", "Succeeded", "Unknown", "Error"]:
                    try:
                        self.v1.delete_namespaced_pod(
                            name=pod_name,
                            namespace=self.namespace,
                            body=client.V1DeleteOptions(grace_period_seconds=0)
                        )
                        logger.info(f"Cleaned up old pod {pod_name} with status {pod_status}")
                        cleaned_count += 1
                    except ApiException as e:
                        logger.warning(f"Failed to delete pod {pod_name}: {e}")
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} old shell pods")
            
        except ApiException as e:
            logger.error(f"Failed to list pods for cleanup: {e}")    