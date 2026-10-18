# Validation and operational evidence register

**Scope:** Task 1.1.1–1.1.3 portfolio revision
**Evidence status:** 17 October 2026

This register distinguishes evidence observed directly from historical test
records and work that has not been performed. A check is not considered a
deployment result just because its Terraform plan or mock test passes.

| Area | Status | Evidence and limits |
| --- | --- | --- |
| Live static explainer | Observed | The documented CloudFront URL loaded the interactive explainer in a browser. This verifies only that the static explainer was reachable at the time checked; it does not verify the multi-region Terraform stack or failover. |
| Static-site Terraform | Documented | The root configuration defines a private S3 origin, CloudFront OAC, HTTPS viewer policy, and object upload. No new AWS plan or apply was run for this revision. |
| Multi-region Terraform formatting and provider validation | Previously reported | Project notes record successful `terraform fmt -check` and `terraform validate` using Terraform 1.12.2. Terraform was unavailable in the environment used for this document/package rebuild, so these checks were not rerun. |
| Multi-region plan tests | Previously reported | Project notes record eight mocked, plan-only test runs. They create no AWS resources and verify selected configuration properties only. They do not prove permissions, deployment, CloudFront behavior, alarm delivery, scaling, or recovery. |
| Read-only smoke-check script | Syntax/input checks passed | `terraform/full-architecture/scripts/smoke-test.sh` accepts only HTTPS URLs and checks the primary page and `/origin-health`. It has not been run against a deployment, and it does not test or prove failover. |
| Current multi-region AWS plan/apply | Not performed | No current authenticated AWS plan, apply, or Terraform state for this stack is included. A bucket console link is not evidence that these separate resources were created. |
| Live origin failover, alarms, scaling, and recovery | Not tested | No runtime logs, response captures, CloudWatch alarm history, or measured recovery results are available for the current multi-region configuration. |
| Route 53 DNS failover | Not implemented | No domain or hosted zone was supplied. No Route 53 record, health check, or custom-domain certificate is included in this Terraform root. |
| Submission PDFs and ZIP | Rebuilt | The PDFs were generated from the current editable portfolio sources and the project ZIP was rebuilt from the packaged project tree. The phase 2 document is a current ten-slide explanation; it does not claim that the multi-region stack was deployed. |

## Evidence to collect before claiming operational failover

Use an authorized, isolated AWS account and obtain approval before creating
billable resources or disrupting service. Save the following artifacts with
timestamps and the target account/regions:

1. The reviewed Terraform plan and outputs from an approved apply.
2. CloudFront application URL and primary response before testing.
3. Health endpoint response and primary target-group health.
4. Controlled origin-failure response, observed maintenance response, and
   start/end timestamps.
5. CloudWatch alarm transition and SNS delivery confirmation, if configured.
6. Primary restoration response and measured recovery interval.
7. For DNS work: the domain/hosted-zone ownership, record configuration,
   health-check configuration, HTTPS certificate coverage for both targets,
   DNS resolution before/during/after a controlled test, and rollback evidence.
8. A cost review and reviewed destroy plan after testing.

Do not place access keys, session tokens, Terraform state, private account
details, or sensitive content in screenshots or the public portfolio ZIP.

## Current DNS design decision

The example currently demonstrates CloudFront origin-group failover only.
The project's proposed DNS extension is Route 53 failover between
HTTPS-capable endpoints, with a health check that verifies the primary
application and a tested standby response. The current maintenance S3 website
endpoint is HTTP-only and public for its single maintenance object; it is not
an acceptable direct HTTPS standby for a custom-domain record. A possible
future design is a pair of CloudFront distributions with the same controlled
hostname certificate coverage, fronted by Route 53 failover records. This
requires a real domain, hosted-zone details, and validation of exact alias and
health-check behavior. It is not implemented or claimed operational.
