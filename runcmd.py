from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream
def runner(POD_NAME,IMAGE_NAME,command,workdir='/home'):
    # POD_NAME = "62dbdce0b7f095e7964d73576162313fa2fc6816"
    NAMESPACE = "default"
    # IMAGE_NAME = "ubuntu"
    workdir='/home'
    CONTAINER_NAME = POD_NAME
    command="{}".format(command)
    command=command.split()
    print(command)
    config.load_kube_config()
    v1 = client.CoreV1Api()
    try:
            # exec_command = ["sh", "-c", f"cd {workdir} && {command}"]
            resp = stream(
                v1.connect_get_namespaced_pod_exec,
                POD_NAME,
                NAMESPACE,
                container=CONTAINER_NAME,
                command=command,
                stderr=True,
                stdin=False,
                stdout=True,
                tty=False
            )
            print(resp)
            return(resp)
    except ApiException as e:
        return(str(e))