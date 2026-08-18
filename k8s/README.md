# Kubernetes Delivery Configuration

The base manifests deploy `delivery-api` into the `devsecops-platform` namespace. They demonstrate production-oriented defaults: two replicas, health probes, a disruption budget, resource requests and limits, restricted pod-security labels, a non-root service account, a read-only container filesystem, dropped Linux capabilities, and default seccomp.

The production overlay contains the image token `__IMAGE_TAG__`. The deployment workflow replaces it with an immutable image digest before applying the rendered manifest. This keeps the cluster deployment tied to the exact image that passed the security gate.

```bash
# Validate locally after installing kubectl.
kubectl kustomize k8s/overlays/prod
```

The `NetworkPolicy` assumes an `ingress-nginx` namespace and DNS access. Adjust it to match the chosen cluster ingress controller and DNS architecture before a real deployment.
