"""
Kubernetes operator example: bazinga operator
"""

import time
import os
import yaml
import json
from datetime import datetime
from time import sleep

import kopf
from pykube import KubeConfig, HTTPClient, Secret, Deployment, all
from pykube.exceptions import PyKubeError, HTTPError, KubernetesError
from pprint import pprint

try:
    cfg = KubeConfig.from_service_account()
except FileNotFoundError:
    cfg = KubeConfig.from_file()

api = HTTPClient(cfg)


@kopf.on.create('bazinga.io', 'v1', 'secretz')
def create_secret(body, meta, spec, status, logger, **kwargs):
    secretName = spec.get('secretName')
    print(f"Create Secret.... {secretName}")

    data = _render_yaml(spec, meta)
    
    obj = Secret(api, data)
    try:
        obj.create()
    except HTTPError as e:
        obj.update()
        if e.code == 409:
            logger.info(
                "Element {:s} exist!!!".format(secretName))
            return
        raise e
    
    logger.info(f"Add new secret {secretName}!!!")

@kopf.on.update('bazinga.io', 'v1', 'secretz')
def update_secret(body, meta, spec, status, old, new, diff, logger, **kwargs):
    secretName = spec.get('secretName')
    print(f'Update Secret.... {secretName}')

    data = _render_yaml(spec, meta)
    
    obj = Secret(api, data)
    obj.update()

    logger.info(f"Secret {secretName} update!!!")

@kopf.on.delete('bazinga.io', 'v1', 'secretz')
def delete(body, meta, spec, status, **kwargs):
    pass

# @kopf.on.event('bazinga.io', 'v1', 'secretz')
# def event_fn_with_error(**kwargs):
#     raise Exception("Plop!!!")

@kopf.on.event('', 'v1', 'secrets', labels={'bazinga.io/secretz': 'true'})
def mod_secret(event, meta, logger, **kwards):
    event_type = event.get('type')
    secretName = meta.get('name')
    namespace = meta.get('namespace')
    
    if event_type == 'MODIFIED':
        print(f"Event Secret.... {secretName}")
        
        logger.info(f"This secret changed {secretName} !!!") 
        _restart_deploy(secretName, namespace)

def _create_children(owner):
    return []

def _wait_for_something():
    time.sleep(1)

def _render_yaml(spec, meta):
    name = spec.get('secretName')
    deploy = spec.get('deployName')
    namespace = meta.get('namespace')
    
    d = spec.get('data')
    for nk, nv in d.items():
        k = nk
        v = nv

    path = os.path.join(os.path.dirname(__file__), 'template/secret.yaml')
    tmpl = open(path, 'rt').read()
    text = tmpl.format(name=name, key=k, value=v, namespace=namespace)
    data = yaml.safe_load(text)
    
    return data

def _restart_deploy(secretName, namespace):
    deploys = Deployment.objects(api, namespace=namespace)
    for deploy in deploys:
        if 'bazinga.io/secretz' in deploy.annotations:
            j = json.dumps(deploy.obj)
            if 'envFrom' in j:
                if secretName in j:    
                    print(f"Restart deployment {deploy.namespace}/{deploy.name}...")
                    deploy.obj['spec']['template']['metadata']['annotations']['secretz.bazinga.io/restartAt'] = f"{datetime.now().isoformat()}"
                    deploy.update()