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
    service_parts = service_spec.strip().split(':')

    # kubectl get pods --selector=app=health --output=jsonpath={.items..metadata.name} |  |  |
    # TODO: Provide better mechanism to specify selector as everything might not be app=
    # This utility needs to provide forwarding

    pods_output = Popen([
        'kubectl',
        'get',
        'pods',
        '--selector=app={selector}'.format(selector=service_parts[0].strip()),
        '--output=jsonpath={.items..metadata.name}',
    ], stdout=PIPE)

    pod_names = pods_output.communicate()[0].decode().split()

    if len(pod_names) <= 0:
        logging.error('No pods found for selector {}'.format(service_parts[0]))
        exit(1)

    port_forwarding_pod = pod_names[0]

    local_port = service_parts[1]
    remote_port = local_port if (len(service_parts) == 2) else service_parts[2]

    Popen('kubectl port-forward --address 0.0.0.0 {} {}:{} >> port-log.txt &'.format(
        port_forwarding_pod,
        local_port,
        remote_port,
    ), close_fds=True, shell=True)

    print('Port Forwarding: {} to local port {} from port {}'.format(
        service_parts[0], # Service name
        local_port, # Local Port
        remote_port,
    ))

if __name__ == "__main__":
    services = os.environ.get('SERVICES', None)

    if not services:
        print('In order to proxy services, you need to specify the SERVICES environment variable.')
        exit(0)

    service_list = services.split(',')

    for service in service_list:
        # Validate will throw error and exit if services incorrectly defined.
        validate_service_spec(service)

    for service in service_list:
        port_forward_service(service)
