# Cloud Programming Portfolio

This folder groups the written deliverables for the three phases of Task 1.1.
The application and infrastructure source remain in the repository root.

| Portfolio part | Phase | Deliverable |
| --- | --- | --- |
| Part 1 | Conception | [Concept notes](./01-Conception-Phase/concept-presentation.md) |
| Part 2 | Development and reflection | [Implementation and reflection](./02-Development-Phase/implementation-and-reflection.md) |
| Part 3 | Finalisation | [Finalisation abstract](./03-Finalisation-Phase/finalisation-phase-abstract.md) |

The Phase 3 report contains a two-page abstract and a ten-page technical
description, updated to match the current CloudFront-only DNS design and
validation status. Three mocked, plan-only Terraform tests now verify
selected configuration properties without deploying resources; AWS
deployment and runtime behavior remain unverified. Tables use wrapped cell
text and expanded padding to keep rows readable and prevent content from
running together.

Latest checks for the full-architecture root: Terraform formatting and
provider validation passed; automated tests passed (3 passed, 0 failed). The
tests use a mocked AWS provider and create no cloud resources.

Submitted PDF deliverables and the assembled submission archive are distributed
separately and are not included in this repository.

## Implementation references

- [Interactive webpage](../index.html)
- [Terraform configuration](../terraform/main.tf)
- [Full active-passive Terraform stack](../terraform/full-architecture/)
- [Deployment instructions](../terraform/README.md)
- [Project overview and scope](../README.md)

The existing live website hosts the static explainer. The separate
multi-region Terraform variant uses CloudFront origin failover and does not
include Route 53 DNS failover. Its S3 website endpoint is directly reachable
over HTTP and must not contain sensitive content. Do not treat the original
Phase 2 presentation's reported test results as validation of this variant.

Before submission, review each written deliverable, add any tutor feedback you
received, and confirm that the code, deployment link, and screenshots reflect
the version you are submitting.
