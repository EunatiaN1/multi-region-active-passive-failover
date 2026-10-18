# Portfolio Part 1 – Conception Phase

## Project idea

This project presents an interactive webpage about hosting a simple website on
AWS and explains how an active-passive design can improve availability during
an outage. The intended audience is a learner or reviewer who needs to
understand the roles of the main AWS components and follow the request path
without first deploying a full production application.

The central idea is to separate the website used for the demonstration from the
larger failover architecture it explains. The demonstration website is a static
site stored in Amazon S3 and delivered over HTTPS through Amazon CloudFront. The
page then visualises a more resilient application design in which a primary
region serves normal traffic and a passive region is available as a fallback.
Amazon Route 53 and CloudFront are described as independent failover layers:
Route 53 can respond to regional health-check results, while CloudFront can
switch origins for configured origin-failure responses.

## Proposed architecture

In the hosting implementation, a private S3 bucket stores the static page.
CloudFront uses Origin Access Control to retrieve the object, so the bucket
does not need public access. Visitors use the CloudFront HTTPS endpoint rather
than accessing S3 directly. Terraform defines the hosting resources so they can
be reviewed and provisioned consistently.

The architecture explainer depicts the intended active-passive application
pattern separately. During normal operation, requests use the primary
application region. If the primary application origin returns configured
failure responses, CloudFront origin failover can direct eligible requests to
a standby origin. If the primary region is unhealthy, Route 53 health checks
and failover routing can direct DNS responses to the standby endpoint. The
standby is passive during normal operation, which avoids maintaining a second
active application fleet.

## Objectives and success criteria

The project aims to:

1. Explain an AWS hosting and failover design in clear, visual form.
2. Provide a responsive webpage that can be viewed on desktop and mobile
   screens.
3. Use Terraform for the static-site hosting infrastructure.
4. Keep the S3 origin private and serve the website through HTTPS.
5. State clearly which architecture components are illustrative and which are
   actually provisioned.

The design is successful if a reader can follow the normal and failure request
paths, identify the purpose of S3, CloudFront, and Route 53, and distinguish the
educational failover simulation from real AWS failover behavior.

## Scope, assumptions, and constraints

The deployed scope is the static explainer website: one private S3 bucket, a
CloudFront distribution, an Origin Access Control, and the access policy needed
for CloudFront to read the page. The project does not provision a production
application, a second application region, Route 53 records, public health
checks, monitoring, or notification services. Real DNS failover requires a
domain and additional resources, permissions, testing, and operating cost.

The architecture diagram is therefore a teaching aid, not a live control
plane. This boundary keeps the assignment implementation manageable while
avoiding a misleading claim that clicking a scenario button changes AWS
resources. AWS charges, CloudFront propagation time, and the need for suitable
AWS credentials are also considered when planning deployment.

## Implementation status and design caveat

The existing live deployment remains the static explainer. A separate
Terraform configuration is available under
[`terraform/full-architecture/`](../../terraform/full-architecture/) for a
deployable variant with the VPC, load balancer, Auto Scaling group, CloudFront
origin group, secondary S3 maintenance website, and monitoring. To allow use
of CloudFront's generated hostname without a custom domain, this variant omits
the Route 53 DNS failover shown in the proposed design. The S3 website origin
supports HTTP only but CloudFront serves the maintenance response over HTTPS;
the website endpoint itself is public and must contain no sensitive
information.

The availability percentage is a design goal, not an AWS service guarantee
or a measured result.
