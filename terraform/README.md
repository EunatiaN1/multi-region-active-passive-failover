# Deploy the webpage to AWS

This configuration hosts `../index.html` in a private S3 bucket and serves it
over HTTPS through CloudFront Origin Access Control. The S3 bucket is not
publicly accessible, has versioning enabled, and expires non-current object
versions after 30 days. CloudFront uses the AWS-managed CachingOptimized cache
policy and the default CloudFront certificate and domain; no custom domain or
DNS changes are required.

This root provisions only the explainer website. For the separate
multi-region application architecture described in the portfolio, see
[`full-architecture/README.md`](./full-architecture/README.md). Do not apply
both roots without reviewing the resources, state, and AWS costs.
The full-architecture root requires Terraform 1.6 or newer and includes
mocked plan tests; the static-site root remains compatible with Terraform 1.5
or newer.

## Prerequisites

- Terraform 1.5 or newer
- AWS CLI credentials with permissions to create and configure the S3 bucket,
  bucket policy, versioning and lifecycle rules, CloudFront distribution, and
  CloudFront Origin Access Control resources

Authenticate using your organization's AWS SSO profile, then initialize and
review the deployment:

```sh
aws sso login --profile YOUR_PROFILE
AWS_PROFILE=YOUR_PROFILE terraform -chdir=terraform init
AWS_PROFILE=YOUR_PROFILE terraform -chdir=terraform plan
```

After reviewing the plan and confirming AWS billing implications, apply it:

```sh
AWS_PROFILE=YOUR_PROFILE terraform -chdir=terraform apply
```

Terraform prints the HTTPS `website_url` when deployment completes. CloudFront
distribution provisioning can take several minutes. The S3 bucket and CloudFront
distribution incur AWS charges while they exist; check current AWS pricing
before applying.

To remove the resources created by this configuration:

```sh
AWS_PROFILE=YOUR_PROFILE terraform -chdir=terraform destroy
```
