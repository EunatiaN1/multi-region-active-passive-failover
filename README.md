# Multi-Region Active-Passive Failover

An interactive, responsive architecture explainer for a proposed AWS
multi-region active-passive failover design.

## Live site

https://d2quyljtx3dqoe.cloudfront.net/

## Current deployment scope

The live deployment is a static website: `index.html` is stored in a private S3
bucket and served through CloudFront. The scenario controls illustrate the
documented request paths; they do not trigger or verify real failover.

The live AWS account does **not** currently have the primary-region application,
secondary-region maintenance origin, CloudFront origin group, Route 53 failover
records, health checks, or CloudWatch/SNS alerting described by the explainer.
Real DNS failover also requires a domain. See
[`terraform/README.md`](./terraform/README.md) for the included static-site
Terraform configuration and deployment instructions.

## Files

- `index.html` — standalone webpage; no build step or external frontend
  dependencies.
- `terraform/` — Terraform configuration for a private S3 bucket and CloudFront
  distribution. This provisions the static site only, not the full multi-region
  failover architecture.

## License

No license has been specified. All rights reserved unless the repository owner
adds a license.
