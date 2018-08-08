#!/usr/bin/env python3

"""
Library to find deployments that need to be proxied

options: (To be specified as environment variables)

        SERVICES: The deployments that need to be proxied

                This script will look for the first running container and proxy that through to the machine.
"""

import os
import logging
from subprocess import run, PIPE, Popen


nginx_directives = ''

def validate_service_spec(service_spec):
    """
    Valid service entries are services with:
            * A deployment name
            * At least one port

    Allowed additions:
            * second port for local machine
    """
    service_parts = service_spec.strip().split(':')

    # There have to be at least two parts to the string
    if len(service_parts) <= 1:
        logging.warn('Service spec needs at lease one deployment name & port in the format NAME:PORT')
        logging.error(
            'Service: (' + service_spec + ') does not comply with standard. service needs to be secified in the '
                                          'format NAME:TARGET_PORT:PORT_FORWARD_PORT(optional).')
        exit(1)

    if len(service_parts[0]) <= 0:
        logging.warn('Service name must be string')
        logging.error('Service: (' + service_spec + ') does not comply with standard.')
        exit(1)

    if not service_parts[1].isdigit():
        logging.warn('Service port must be integer')
        logging.error('Service: (' + service_spec + ') does not comply with standard. (' + service_parts[
            1] + ') os not a valid integer.')
        exit(1)

    if len(service_parts) >= 3 and not service_parts[2].isdigit():
        logging.warn('Service port must be integer')
        logging.error('Service: (' + service_spec + ') does not comply with standard. (' + service_parts[
            2] + ') os not a valid integer.')
        exit(1)

    return True


def port_forward_service(service_spec):
    # kubectl get pods --selector=app=authenticationservice --output=jsonpath={.items..metadata.name}

    service_parts = service_spec.strip().split(':')

    output = run(['kubectl', 'get', 'pods', '--selector=app={}'.format(service_parts[0].strip()),
                  '--output=jsonpath={.items..metadata.name}'], stdout=PIPE)

    if not output.stdout.decode().strip():
        logging.error('No pods found for selector {}'.format(service_parts[0]))
        exit(1)

    local_port = service_parts[1]
    local_proxy_port = int(local_port) + 1000
    remote_port = local_port if (len(service_parts) == 2) else service_parts[2]
    global nginx_directives
    nginx_directives += """
    server {{
        listen {listen_port};
        
        server_name _;

        location / {{
                proxy_pass http://127.0.0.1:{proxy_port};
                proxy_pass_header Server;
                proxy_set_header Host $http_host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Scheme $scheme;
                proxy_set_header X-Forwarded-Proto https;
        }}
    }}
    """.format(listen_port=local_port, proxy_port=local_proxy_port)

    Popen('kubectl port-forward {} {}:{} >> port-log.txt &'.format(
        output.stdout.decode().strip(),
        local_proxy_port,
        service_parts[1] if (len(service_parts) == 2) else service_parts[2]
    ), close_fds=True, shell=True)

    print('Port Forwarding: {} to local port {} from port {}'.format(
        service_parts[0], # Service name
        local_port, # Local Port
        remote_port,
    ))

def update_nginx_configs():
    file = open('/etc/nginx/sites-enabled/default', 'w+')
    file.truncate(0)
    file.write(nginx_directives)
    file.close()


if __name__ == "__main__":
    services = os.environ.get('SERVICES', None)

    if not services:
        print('In order to proxy services, you need to specify the SERVICES environment variable.')
        exit(0)

    service_list = services.split(',')

    for service in service_list:
        # Validate will throw error and exit if services i oncorrectly defined.
        validate_service_spec(service)

    for service in service_list:
        port_forward_service(service)

    update_nginx_configs()

    Popen('service nginx restart', shell=True)
