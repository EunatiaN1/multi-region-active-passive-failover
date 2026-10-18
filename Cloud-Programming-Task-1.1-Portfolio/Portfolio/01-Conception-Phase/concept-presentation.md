# Portfolio Part 1 – Conception Phase

## Project idea and audience

This project explains how AWS can host a simple webpage and how an
active-passive design could respond to a regional application failure. It is
intended for a learner or reviewer who needs to understand the request path
and the role of each cloud component without first deploying a production
system. The deliverables are a responsive interactive explainer, a
conceptual architecture diagram, and Terraform source.

## Proposed architecture and rationale

The actual demonstration website is a static page stored in Amazon S3 and
delivered through Amazon CloudFront. CloudFront uses Origin Access Control
(OAC) to read a private S3 bucket, so visitors do not need direct bucket
access. HTTPS is enforced at the viewer edge. Terraform describes these
resources to make the hosting setup reviewable and repeatable.

Separately, the explainer presents a proposed active-passive application
design. During normal operation, CloudFront forwards requests to an
Application Load Balancer (ALB) in a primary AWS region. The ALB distributes
traffic to EC2 instances across two Availability Zones, and an Auto Scaling
group adjusts compute capacity to demand. A secondary region holds a
maintenance response. CloudFront origin-group failover can select that
response for configured primary-origin failures. Route 53 health checks and
failover records are a separate proposed DNS layer; they do not share the
same trigger or behavior as CloudFront origin failover.

The component choices separate global entry and caching (CloudFront),
private object storage (S3), regional traffic distribution (ALB), and
elastic compute (EC2 Auto Scaling). A static standby lowers idle compute
cost, but it is not a warm replacement application and cannot serve
stateful user workloads.

## Objectives and success criteria

The design aims to explain the normal and failure request paths, provide a
responsive webpage, host the real explainer privately behind HTTPS, and
distinguish implemented resources from proposed behavior. A reader should
be able to identify the purpose of S3, CloudFront, Route 53, ALB, and EC2,
and understand which mechanisms are active in each scenario.

## Scope, assumptions, and constraints

The live deployment is limited to the static explainer's private S3 bucket,
CloudFront distribution, OAC, and access policy. The browser scenario
controls are visual simulations; they do not call AWS or cause failover.
The separate multi-region Terraform root is a prototype for CloudFront
origin failover. It does not configure Route 53 records, public health
checks, a custom domain, or a custom HTTPS certificate. DNS failover would
require a controlled domain and hosted zone, reachable health-check targets,
compatible HTTPS on both targets, additional permissions, cost review, and
runtime testing. The secondary S3 website endpoint is public for its
maintenance object and HTTP-only; it must contain no sensitive information.

Availability and low latency are design objectives, not measured results or
AWS service guarantees. CloudFront propagation, regional quotas, account
permissions, service charges, DNS caching, and the gap between conceptual
design and deployed resources are explicit project constraints. The
accompanying diagram is conceptual, not a deployed-resource inventory.
