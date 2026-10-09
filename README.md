# Multi-Region Active-Passive Failover

An interactive explainer for a proposed resilient AWS web architecture. Explore
how CloudFront, Route 53, regional origins, and health checks could work together
to route traffic from a primary region to a standby region.

> **Live demo:** [d2quyljtx3dqoe.cloudfront.net](https://d2quyljtx3dqoe.cloudfront.net/)

## What you'll find

- A responsive, interactive architecture diagram.
- Scenario controls that illustrate the documented request paths during normal
  operation and a simulated failover.
- An explanation of the AWS components and the role each would play.
- Terraform configuration for hosting this static explainer with a private S3
  bucket and CloudFront.

## Architecture scope

The scenario controls are an educational visualization. They do **not** trigger
or verify a real failover.

The live AWS deployment hosts only this static website. It does not include the
primary-region application, secondary-region maintenance origin, CloudFront
origin group, Route 53 failover records, health checks, or CloudWatch/SNS
alerting shown in the explainer. Real DNS failover also requires a domain.

## Run locally

No build step or frontend dependencies are required. Open `index.html` directly
in a browser, or serve the repository with any static web server.

## Deploy the explainer to AWS

The Terraform in [`terraform/`](./terraform/) provisions the static website only:
a private S3 bucket, CloudFront distribution, and Origin Access Control.

Requirements:

- Terraform 1.5 or newer
- AWS CLI credentials with permission to create the resources above

Review the deployment steps, permissions, and cost considerations in the
[Terraform README](./terraform/README.md) before applying. AWS resources incur
charges while deployed.

## Repository layout

| Path | Description |
| --- | --- |
| [`index.html`](./index.html) | Standalone interactive website |
| [`terraform/`](./terraform/) | Terraform for static-site hosting on AWS |

## License

No license has been specified. All rights are reserved unless the repository
owner adds a license.
