# Portfolio Part 3 – Finalisation Abstract

## Project, outcome, and design

This portfolio project combines an interactive website about multi-region
active-passive failover with infrastructure as code. The website explains the
proposed AWS architecture and lets readers explore normal and simulated
failure paths. Its controls are client-side illustrations: they do not invoke
AWS APIs, change DNS, or demonstrate an actual recovery event.

The currently live website hosts that explainer as a static page. Its
Terraform deployment provisions an S3 bucket with public access blocked,
default encryption, versioning, and a lifecycle rule for non-current versions.
CloudFront uses Origin Access Control (OAC) to read the object, redirects
viewers to HTTPS, and applies the AWS-managed CachingOptimized cache policy.
This deployed static-site root is deliberately independent of the new
multi-region application example.

The submitted architecture proposes a primary application in eu-central-1
with a public Application Load Balancer across two Availability Zones and an
EC2 Auto Scaling group. CloudFront forwards normal requests to the load
balancer. A secondary S3 website in us-east-1 holds a maintenance page;
CloudFront can request it when the primary origin returns HTTP 500, 502, 503,
or 504. The original diagram also shows Route 53 health checks and DNS
failover. These are separate mechanisms: CloudFront origin failover is
response-code-driven, while DNS failover requires managed records and health
checks for a controlled hostname.

The current multi-region Terraform variant uses CloudFront's AWS-generated
hostname so it can be configured without a custom domain. It defines the
primary VPC, ALB, EC2 Auto Scaling application, secondary S3 maintenance
website, CloudFront origin group, and CloudWatch/SNS target-health alerting.
It deliberately omits Route 53 records, DNS health checks, and ACM
certificate provisioning. It is consequently a partial implementation of
the proposal, not the complete DNS-failover architecture. It does not replace
the existing live static website.

<!-- PAGE BREAK -->

## Making of, validation, and reflection

The Terraform application tier uses an Amazon Linux launch template and a
small Python HTTP service managed by systemd. The target group checks
`/health`; a distinct `/origin-health` CloudFront path is available for manual
checking and does not drive Route 53. The Auto Scaling defaults are two
minimum and desired instances, up to six, with target CPU utilization of 50
percent. Instance metadata requires IMDSv2 tokens. The ALB allows origin
traffic from CloudFront's managed origin-facing prefix list, and instances
accept HTTP only from the ALB security group.

The secondary website bucket uses a generated prefix and permits anonymous
reads only for its maintenance `index.html`. The website endpoint itself is
HTTP-only and directly reachable, so it must contain no confidential
information. CloudFront can deliver a selected failover response through
its HTTPS edge endpoint. The CloudWatch alarm observes unhealthy ALB targets
and publishes to an SNS topic; an optional email recipient must confirm the
subscription.

Terraform formatting and provider-schema validation passed. Three automated,
plan-only Terraform tests using a mocked AWS provider also passed. They check
the default Auto Scaling capacity, target health-check path, IMDSv2
requirement, CloudFront failover response codes, maintenance-bucket public
access settings, alarm wiring, optional email subscription, and validation of
the CPU target variable. These tests exercise Terraform's planned
configuration without AWS credentials or creating cloud resources; they do
not verify AWS permissions, deployment, or service behavior. An AWS plan
attempt could not authenticate because no authorized profile was configured.
The multi-region stack has not been applied or runtime-tested. The Phase 2
submission reports an earlier deployment and tests, but its corresponding
source, state, and logs were not available to reproduce those results against
this configuration. No live failover, scaling, alarm, or recovery result is
claimed here.

The finalisation work makes the boundary between explanation, deployed
hosting, validated code, and unverified cloud behavior explicit. The multi-region code advances the
original concept, and automated plan tests now provide repeatable checks of
important configuration choices. The Route 53 DNS layer and operational
evidence remain outstanding. Next steps are to configure an authorized AWS
identity, review a complete plan and account-specific costs, deploy in a
controlled account, and test origin failure, alarms, and recovery. A complete
DNS-failover implementation would additionally need a custom domain, public
hosted zone, and separately reviewed HTTPS-capable standby endpoint. No tutor
feedback was supplied for this revision; authentic feedback should be added
if received.

**Keywords:** AWS, Terraform, Amazon S3, CloudFront, Application Load
Balancer, Auto Scaling, active-passive, origin failover.
