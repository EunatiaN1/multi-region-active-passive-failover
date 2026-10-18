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

The `/origin-health` endpoint is routed to the primary ALB for manual
verification; it is not a Route 53 health check and does not trigger DNS
failover. CloudFront origin-group failover is response-code-driven. It is not
an independent regional DNS failover mechanism.

The primary-region bootstrap runs the sample service as an unprivileged
systemd user with a restricted capability set and filesystem protections.
The threaded HTTP server can handle concurrent requests; only `/` and the
health endpoints are served.

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
configuration properties, including scaling bounds, network access, regional
separation, project naming, and subnet sizing, without AWS credentials or
creating cloud resources:

```sh
terraform -chdir=terraform/full-architecture init -backend=false
terraform -chdir=terraform/full-architecture fmt -check
terraform -chdir=terraform/full-architecture validate
terraform -chdir=terraform/full-architecture test
```

These tests do not verify AWS account permissions, deployed service behavior,
failover timing, notifications, scaling, or recovery. Those require an
authorized deployment and controlled runtime tests.

Run the commands above after changing the configuration. No AWS resources are
created by the mocked plan tests.

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

1. Save the approved Terraform plan, apply output, account/region, UTC
   timestamps, and resource outputs in the evidence record. Redact account
   identifiers where required by the submission rules.
2. Confirm the `application_url` returns the primary-region page over HTTPS.
   Capture the URL and response status; do not treat the AWS-generated URL as
   a custom-domain DNS test.
3. Confirm `/origin-health` returns HTTP 200 while primary targets are healthy.
   Record the command, timestamp, and response.
4. In a controlled test environment, make the primary origin return one of the
   configured 5xx responses and confirm CloudFront serves the maintenance
   page. Record the response code, body, test start/end times, and recovery
   result. Do not break a shared or production service to force this test.
5. Confirm the ALB unhealthy-target alarm enters ALARM and the SNS email
   subscription is confirmed and receives the notification, if configured.
6. Confirm the maintenance page contains no sensitive data and that its
   public HTTP endpoint is understood and accepted.
7. Restore the primary application, confirm the primary response is restored,
   and record observed recovery time. Review logs, charges, and all resources
   before destroying the test stack.

The read-only primary-path smoke check can be run after deployment:

```sh
bash terraform/full-architecture/scripts/smoke-test.sh \
  "$(terraform -chdir=terraform/full-architecture output -raw application_url)"
```

It checks for the expected primary page and `/origin-health` response. It
does not cause an outage, test the maintenance path, or prove failover. Run
the controlled failover and restoration steps separately in an approved
test environment.

### Route 53 DNS failover: design boundary

This Terraform root does not implement DNS failover. Do not point a domain's
records at this stack and claim DNS failover is operational. A production
design needs a domain and hosted zone under the operator's control, plus
explicit decisions for:

- The primary and standby DNS targets and whether those targets serve the same
  application or a maintenance response.
- Health checks that observe the real primary service, with a documented
  endpoint, protocol, expected response, failure threshold, and recovery
  behavior. A health check must not be described as monitoring a service that
  it cannot reach.
- HTTPS on both targets. An S3 website endpoint is HTTP-only; direct DNS
  failover from a CloudFront HTTPS hostname to that endpoint would not preserve
  browser HTTPS. The standby must have an HTTPS-capable endpoint and compatible
  certificate before failover records are introduced.
- Route 53 failover record names/types, alias behavior, TTL, health evaluation,
  DNS caching, and how application traffic interacts with the CloudFront
  origin group.
- A controlled test plan, rollback, recovery observation, and cost review.

One candidate for further design is Route 53 failover between two
HTTPS-capable CloudFront distributions: a primary distribution serving the
application path and a standby distribution serving the maintenance page.
This requires a controlled hostname, correctly scoped certificates, reachable
health-check targets, and verification of Route 53/CloudFront alias and health
check behavior. It is a design candidate, not implemented or tested here.
Do not add placeholder domain values or claim it works until it is configured
and tested in an authorized AWS account.

The repository's [validation evidence register](../../Portfolio/03-Finalisation-Phase/validation-evidence.md)
lists what is currently observed and what remains to collect.

To remove resources after testing, inspect the destroy plan first:

```sh
AWS_PROFILE=YOUR_PROFILE terraform -chdir=terraform/full-architecture plan -destroy
AWS_PROFILE=YOUR_PROFILE terraform -chdir=terraform/full-architecture destroy
```
