# ODOOX Security & Release Policies

## 1. Supply Chain Security

To protect the ODOOX middleware from supply chain attacks, the following CI/CD gates are enforced on all code merged to the `main` branch:

- **SBOM Generation:** A Software Bill of Materials (SBOM) in SPDX format is generated for every build and retained as an artifact.
- **Dependency Scanning:** Aqua Security's Trivy scanner runs against the repository on every PR and push.
  - **Enforcement:** The build will **fail** if any `HIGH` or `CRITICAL` Common Vulnerabilities and Exposures (CVEs) are detected in our Python dependencies or Docker base image.

## 2. Commit & Release Signatures

All code entering production must cryptographically prove its origin.

- **Signed Commits Required:** All developers must configure Git to sign commits using GPG or SSH keys. Unsigned commits are rejected by GitHub branch protection rules.
- **Signed Releases:** All semantic version tags (e.g., `v1.2.0`) created for production deployments must be cryptographically signed by the release engineer.
- **Branch Protection:**
  - `main` branch requires a minimum of 1 approved Pull Request review.
  - The `Run Tests & Coverage` and `Supply Chain Security Scan` status checks must pass before a merge is permitted.

*This policy is strictly enforced and audited quarterly.*
