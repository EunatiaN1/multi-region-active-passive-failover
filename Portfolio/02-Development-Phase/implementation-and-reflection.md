# Portfolio Part 2 – Development and Reflection

## Implementation

The solution consists of a standalone HTML webpage and a Terraform
configuration. The page presents a responsive architecture diagram, descriptions
of the AWS services, normal-operation and failover scenarios, and links to
relevant AWS documentation. Its scenario controls update the visual
representation in the browser only. They do not call AWS APIs or trigger a
real failover.

The existing live hosting configuration is defined in
[Terraform](../../terraform/main.tf). It creates an S3 bucket with public access
blocked, server-side encryption, versioning, and a lifecycle rule that expires
non-current object versions after 30 days. CloudFront accesses the bucket
through Origin Access Control and a bucket policy restricted to the
distribution's ARN. The distribution redirects viewers to HTTPS and uses the
AWS-managed CachingOptimized cache policy. Terraform uploads the page as the
distribution's default root object and exports the resulting HTTPS URL, bucket
name, and distribution ID.

A separate [multi-region Terraform root](../../terraform/full-architecture/)
defines the primary VPC, multi-AZ ALB and EC2 Auto Scaling application,
secondary-region S3 maintenance page, CloudFront origin group, and
CloudWatch/SNS alerting. It is kept separate from the live static-site root.
The deployable variant uses CloudFront's generated hostname and omits the
Route 53 DNS failover and custom-domain requirements from the proposed design.

## Development process and verification

Development began with the architecture and scope: a private static-site origin
for the real deployment, alongside an illustrative active-passive diagram.
The webpage and Terraform configuration were then developed to match this
boundary. The finalisation pass added S3 version history and lifecycle cleanup
to support recovery from accidental updates without retaining old versions
indefinitely. CloudFront caching was aligned with the AWS-managed
CachingOptimized policy.

The submitted Phase 2 presentation reports that 38 resources were applied and
that several failover and scaling tests passed. The present repository did not
contain the corresponding full-architecture Terraform source, Terraform state,
or test logs. Those results are therefore reported as stated in the original
submission but have not been independently reproduced against the newly added
configuration.

For a future deployment, authenticate with an authorized profile, initialize
Terraform, inspect the plan, and apply only after checking the resources and
expected AWS charges. After deployment, test the primary URL, origin health
path, S3 privacy boundary, CloudFront failover, and recovery independently.
The S3 website endpoint is HTTP-only and directly reachable; CloudFront's
edge endpoint remains HTTPS. Terraform destroy can be used after testing once
its plan has been reviewed.

## Reflection

The project meets its main goals by combining an understandable webpage with
infrastructure as code and by documenting the difference between the design
being explained and the resources actually deployed. A notable design decision
was to keep the S3 bucket private rather than enabling public website hosting.
This reduces direct exposure of the origin and demonstrates how CloudFront
Origin Access Control can be used for a static site.

The most important limitation is that the newly added full-architecture code
has not been applied or runtime-tested in AWS. The deployed website still
hosts the static explainer, and its scenario controls remain browser-side
illustrations. Three mocked, plan-only Terraform tests now verify selected
configuration properties, including capacity defaults, health checks,
IMDSv2, origin-failover response codes, maintenance-bucket access settings,
alarm wiring, optional email configuration, and CPU-target validation. They
run without AWS credentials and create no resources, but cannot establish
that the stack deploys or behaves as intended in AWS. The selectable
CloudFront-only variant does not provide Route 53 DNS failover; that
capability requires a custom domain and additional configuration.

Overall, the project includes both the existing small static-site deployment
and a separate multi-region Terraform implementation with CloudFront origin
failover. Feedback from a tutor or reviewer should be
incorporated in the final submitted version; this reflection does not assume
that new AWS deployment or runtime tests have been performed.
