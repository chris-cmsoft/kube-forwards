# Kubernetes port forward utility

> This image was built from need in an environment where there are many microservices and spinning up all of these services and creating test data was a mission every time we wanted to make a small change.  
> After moving to Kubernetes we started port-forwarding like mad men and women to try connect to kubernetes services.  
> So I built this image which automates that port-forwarding when running in docker-compose locally.  
> The plan: simple. Specify a deployment name & port and viola ! You can reach it immediately without any setup.
> * No manual forwarding
> * No manual test data creation and recreation

### Usage

The image uses and env variable $SERVICES to register proxies.

It also uses a volume mount to your kubernetes config to be able to reach your cluster.

> ### We have explicitly tried to make everything as simple and readable as possible for the following reason:

> Security concern.  
> We are aware that it poses a significant risk mounting a kubernetes config into a 3rd party container.  
> If you are concerned about this, you can clone this repo as a starting point and build your own version which you can trust.  

The format is specified in the format {deployment_name}:{local_port}:{?remote_port},{another_deployment_name}...

> The remote_port can be omitted in which case the local_port will be used.

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

Now when doing http / database connections to the kubernetes cluster simply specify `kube-forwards` as the host and your port mapping as the port.
