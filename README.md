# Kubernetes port forward utility

> When developing services locally, we sometimes require dependant services to be proxied from our cluster to our local machine to ease development.
> This image serves the purpose of easing that process.

### Usage

The image uses the environment variable $SERVICES to see which services you need proxied.

This variable should contain a comma-delimited list of deployments & ports to forward

The format for this variable is DEPLOYMENT_NAME:PORT:TARGET_PORT, OTHER_DEPLOYMENT:PORT:TARGET_PORT etc.

TARGET_PORT is optional. If none is supplied the image will use PORT as both remote and local port.

In your docker-compose file you can simply add:
```yaml
kube-forwards:
    image: chriscmsoft/kube-forwards
    environment:
      - SERVICES=someservice:8000, someotherservice:8001:8000
    volumes:
      - ~/.kube/config:/root/.kube/config
other-service:
    image: some-image:1.0
```

Now if you exec into the other-service container you can curl http://kube-forwards:8000 and it will hit someservice on the Kubernetes cluster.

# Current limitations. 

Because kubectl does not allow porting to 0.0.0.0 [See here](https://github.com/kubernetes/kubernetes/issues/43962), I have had to go hacky-cowboy and increase local_port by 1000, then add nginx to proxy_pass (local_port) to (local_port + 1000) to maintain expected behaviour. Hopefully they will sort out this bug soon so we can remove the hackiness and make the image smaller.

