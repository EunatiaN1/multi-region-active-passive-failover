# Full active-passive architecture (Terraform)

This is a separate Terraform root that expands the static-site deployment into
a multi-region application. It creates a primary-region web application behind
an Application Load Balancer and an Auto Scaling group, a secondary-region S3
maintenance page, a CloudFront origin group, and CloudWatch/SNS alerting. This
deployment variant uses CloudFront's AWS-generated hostname and does not create
a custom domain, ACM certificate, or Route 53 DNS failover records.

## Important safety and availability notes

- Applying this stack creates billable resources, including an ALB, EC2
  instances, a CloudFront distribution, and S3 resources. Review current AWS
  pricing for your account and regions before applying.
- The secondary S3 website endpoint supports HTTP only and is directly
  reachable. CloudFront uses it as an origin and serves the maintenance page
  through its HTTPS edge endpoint when the ALB origin returns a configured
  5xx response. Do not use the failover bucket for confidential content.
- CloudFront origin failover does not switch traffic based on `/origin-health`
  or DNS health checks. This variant intentionally omits Route 53 DNS failover.
- The maintenance bucket grants anonymous `GetObject` only for `index.html`.
  It disables public ACLs, but the bucket policy is intentionally public for
  website hosting. Account-level S3 Block Public Access can still prevent
  deployment if it disallows public bucket policies.
- The optional SNS email subscription must be confirmed by its recipient.

## Resources and request flow

1. Users access the AWS-generated CloudFront hostname.
2. CloudFront forwards normal requests to the ALB in the primary region.
3. The ALB spans two public subnets in distinct Availability Zones and sends
   traffic to EC2 instances controlled by a CPU target-tracking Auto Scaling
   group (defaults: minimum 2, desired 2, maximum 6).
4. CloudFront origin-group failover sends requests to the secondary S3 website
   origin for primary-origin responses 500, 502, 503, or 504.
5. CloudWatch alarms when the primary ALB target group reports unhealthy
   application hosts and publishes to SNS.

The `/origin-health` endpoint is available through CloudFront for manual
verification; it does not trigger a separate DNS failover path.

## Prerequisites

- Terraform 1.6 or later (required for the automated Terraform tests)
- AWS credentials with permission to create the listed EC2, VPC, ELB, Auto
  Scaling, S3, CloudFront, CloudWatch, and SNS resources
- Awareness of account/region quotas, the account-level public-access-block
  setting, and current AWS charges

Terraform uses local state by default. Keep that state private and durable, or
configure a separately bootstrapped remote state backend before a shared or
production deployment.

## Local automated tests

The plan-level Terraform tests use a mocked AWS provider. They check important
configuration properties without AWS credentials or creating cloud resources:

```sh
terraform -chdir=terraform/full-architecture init -backend=false
terraform -chdir=terraform/full-architecture fmt -check
terraform -chdir=terraform/full-architecture validate
terraform -chdir=terraform/full-architecture test
```

These tests do not verify AWS account permissions, deployed service behavior,
failover timing, notifications, scaling, or recovery. Those require an
authorized deployment and controlled runtime tests.

Latest local verification: formatting and provider validation passed, and
the three plan tests passed. No AWS resources were created by these checks.

## Configure, inspect, and deploy

Run from the repository root:

```sh
cp terraform/full-architecture/terraform.tfvars.example \
  terraform/full-architecture/terraform.tfvars
```

The only optional setting in `terraform.tfvars.example` is the notification
email. Leave it empty to disable the email subscription, or set an address
whose recipient can confirm the subscription. Keep `terraform.tfvars` private;
it is gitignored. Then authenticate and inspect the plan:

```sh
aws sso login --profile YOUR_PROFILE
AWS_PROFILE=YOUR_PROFILE terraform -chdir=terraform/full-architecture init
AWS_PROFILE=YOUR_PROFILE terraform -chdir=terraform/full-architecture fmt -check
AWS_PROFILE=YOUR_PROFILE terraform -chdir=terraform/full-architecture validate
AWS_PROFILE=YOUR_PROFILE terraform -chdir=terraform/full-architecture plan
```

Only after reviewing the complete plan and cost should an authorized operator
apply it:

```sh
AWS_PROFILE=YOUR_PROFILE terraform -chdir=terraform/full-architecture apply
```

The recipient must confirm the SNS email subscription if one was configured.
Terraform outputs the application URL, primary ALB name, maintenance endpoint,
and SNS topic ARN.

## Validation checklist

After an approved deployment:

1. Confirm the app URL returns the primary-region page over HTTPS.
2. Confirm `/origin-health` returns 200 while the primary target group is
   healthy.
3. In a controlled test, make the ALB origin return a configured failure and
   confirm CloudFront serves the maintenance page.
4. Confirm the ALB unhealthy-target alarm and optional SNS email subscription.
5. Confirm the maintenance site contains no sensitive data.
6. Restore the primary application and verify recovery, then review logs,
   charges, and all resources before destroying the test stack.

To remove resources after testing, inspect the destroy plan first:

```sh
AWS_PROFILE=YOUR_PROFILE terraform -chdir=terraform/full-architecture plan -destroy
AWS_PROFILE=YOUR_PROFILE terraform -chdir=terraform/full-architecture destroy
```
