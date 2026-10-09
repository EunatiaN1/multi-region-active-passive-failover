# Deploy the webpage to AWS

This configuration hosts `../index.html` in a private S3 bucket and serves it
over HTTPS through CloudFront Origin Access Control. The S3 bucket is not
publicly accessible. The CloudFront distribution uses the default CloudFront
certificate and domain; no custom domain or DNS changes are required.

## Prerequisites

- Terraform 1.5 or newer
- AWS CLI credentials with permissions to create S3 bucket, bucket policy,
  CloudFront distribution, and CloudFront Origin Access Control resources

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
