# Kubernetes Delivery Configuration

The base manifests deploy `delivery-api` into the `devsecops-platform` namespace. They demonstrate production-oriented defaults: two replicas, health probes, a disruption budget, resource requests and limits, restricted pod-security labels, a non-root service account, a read-only container filesystem, dropped Linux capabilities, and default seccomp.

The production overlay contains the image token `__IMAGE_TAG__`. A cluster administrator uses the rendered manifest during controlled platform bootstrap. The deployment workflow does not apply the full manifest set; it can only update the `delivery-api` container image on the existing Deployment with an immutable digest. This keeps the release traceable to the exact image that passed the security gate without granting the workflow authority over Services, NetworkPolicies, or RBAC.

```bash
# Validate locally after installing kubectl.
kubectl kustomize k8s/overlays/prod
```

The `NetworkPolicy` assumes an `ingress-nginx` namespace and DNS access. Adjust it to match the chosen cluster ingress controller and DNS architecture before a real deployment.
