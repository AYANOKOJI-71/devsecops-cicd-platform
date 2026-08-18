#!/usr/bin/env python3
"""Statically validate the repository’s deployable configuration without cloud access."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import hcl2
import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = ROOT / ".github" / "workflows"
K8S_DIR = ROOT / "k8s"
TERRAFORM_DIR = ROOT / "terraform"

EXPECTED_WORKFLOWS = {
    "ci.yml": "Quality Gate",
    "security.yml": "Security Gates",
    "codeql.yml": "CodeQL",
    "release.yml": "Release Container",
    "deploy.yml": "Deploy to Production EKS",
}


def fail(message: str) -> None:
    """Print a validation failure and terminate with a nonzero exit status."""

    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_yaml(path: Path) -> dict:
    """Parse a single YAML document and require a mapping root."""

    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        fail(f"Invalid YAML in {path.relative_to(ROOT)}: {error}")
    if not isinstance(document, dict):
        fail(f"Expected a mapping in {path.relative_to(ROOT)}")
    return document


def validate_workflows() -> None:
    """Validate workflow names, minimum permissions, and external-action pinning."""

    for filename, expected_name in EXPECTED_WORKFLOWS.items():
        path = WORKFLOW_DIR / filename
        document = load_yaml(path)
        if document.get("name") != expected_name:
            fail(f"Unexpected workflow name in {filename}")
        if "permissions" not in document:
            fail(f"Workflow {filename} must declare permissions explicitly")

        source = path.read_text(encoding="utf-8")
        for action, revision in re.findall(r"uses:\s+([^@\s]+)@([^\s#]+)", source):
            if action.startswith("docker://"):
                continue
            if not re.fullmatch(r"[a-f0-9]{40}", revision):
                fail(f"Action {action} in {filename} is not pinned to a 40-character commit SHA")

    deploy_source = (WORKFLOW_DIR / "deploy.yml").read_text(encoding="utf-8")
    required_deployment_controls = [
        "environment: production",
        "id-token: write",
        "kubectl rollout status",
        "^sha256:[a-f0-9]{64}$",
    ]
    for control in required_deployment_controls:
        if control not in deploy_source:
            fail(f"Deployment workflow is missing control: {control}")


def validate_kubernetes() -> None:
    """Parse every Kubernetes file and confirm the hardened base has required resources."""

    for path in sorted(K8S_DIR.rglob("*.yaml")):
        load_yaml(path)

    kustomization = load_yaml(K8S_DIR / "base" / "kustomization.yaml")
    resources = set(kustomization.get("resources", []))
    expected_resources = {
        "namespace.yaml",
        "deployment.yaml",
        "service.yaml",
        "hpa.yaml",
        "pdb.yaml",
        "networkpolicy.yaml",
        "role.yaml",
        "rolebinding.yaml",
    }
    missing = expected_resources - resources
    if missing:
        fail(f"Kustomize base is missing resources: {', '.join(sorted(missing))}")

    deployment_source = (K8S_DIR / "base" / "deployment.yaml").read_text(encoding="utf-8")
    required_controls = [
        "runAsNonRoot: true",
        "readOnlyRootFilesystem: true",
        "drop:",
        "RuntimeDefault",
    ]
    for control in required_controls:
        if control not in deployment_source:
            fail(f"Kubernetes deployment is missing hardening control: {control}")


def validate_terraform() -> None:
    """Parse all Terraform files and confirm no state files were added to the module."""

    for path in sorted(TERRAFORM_DIR.glob("*.tf")):
        try:
            with path.open(encoding="utf-8") as file_handle:
                hcl2.load(file_handle)
        except Exception as error:  # hcl2 exposes multiple parser exception types.
            fail(f"Invalid Terraform in {path.relative_to(ROOT)}: {error}")

    state_files = list(TERRAFORM_DIR.glob("*.tfstate*"))
    if state_files:
        fail("Terraform state must not be committed")


def validate_dockerfile() -> None:
    """Check the Dockerfile for explicit non-root execution and a health check."""

    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    for control in ["USER appuser", "HEALTHCHECK", "python:3.12-slim"]:
        if control not in dockerfile:
            fail(f"Dockerfile is missing control: {control}")


def main() -> None:
    """Run all static configuration checks and report a concise success result."""

    validate_workflows()
    validate_kubernetes()
    validate_terraform()
    validate_dockerfile()
    print("Configuration validation passed: workflows, Kubernetes, Terraform, and Dockerfile.")


if __name__ == "__main__":
    main()
