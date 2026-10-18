# Cloud Programming Portfolio

This is the submission index for Task 1.1.1–1.1.3. The Markdown sources,
regenerated PDFs, architecture illustration, and Terraform source are included
in this folder and the accompanying project ZIP.

| Task | PDF deliverable | Editable source |
| --- | --- | --- |
| 1.1.1 Conception | [Conception submission](./01-Conception-Phase/Task-1.1.1-Phase-1-Conception-Submitted.pdf) | [Concept](./01-Conception-Phase/concept-presentation.md) |
| 1.1.2 Development and reflection | [Ten-slide presentation](./02-Development-Phase/Task-1.1.2-Phase-2-Development-Submitted.pdf) | [Implementation and reflection](./02-Development-Phase/implementation-and-reflection.md) |
| 1.1.3 Finalisation | [Two-page abstract](./03-Finalisation-Phase/Task-1.1.3-Phase-3-Abstract.pdf); [seven-page final report](./03-Finalisation-Phase/Task-1.1.3-Phase-3-Final-Report.pdf) | [Abstract](./03-Finalisation-Phase/finalisation-phase-abstract.md); [technical description](./03-Finalisation-Phase/final-report-technical.md) |

Regenerate the PDFs from this folder with Python 3 and ReportLab:

```sh
python3 -m pip install -r requirements-build.txt
python3 build_pdfs.py
```

## Scope and evidence at this revision

The live CloudFront URL serves the static interactive explainer. It is not the
multi-region application. The separate Terraform example defines a primary
application, a secondary maintenance page, CloudFront origin-group failover,
and CloudWatch/SNS alerting. It does not define Route 53 records or a custom
domain, and it has not been applied or runtime-tested in AWS. The scenario
controls on the webpage are simulations, not AWS controls.

The project records eight mocked, plan-only Terraform test runs in the
development history. They create no AWS resources and are not deployment or
failover evidence. Terraform was not available in the current editing
environment, so those checks were not rerun while rebuilding this package.
See the [evidence register](./03-Finalisation-Phase/validation-evidence.md)
and [multi-region deployment guide](../terraform/full-architecture/README.md)
for the distinction between verified, previously reported, and outstanding
evidence.

The Phase 2 PDF is regenerated as a current-ten-slide explanation. Statements
in the original Phase 2 submission about an earlier deployment are historical
claims only; their source, state, and logs were not available for independent
verification and they do not describe the current Terraform configuration.

## Project references

- [Interactive webpage](../index.html)
- [Static-site Terraform](../terraform/)
- [Multi-region Terraform](../terraform/full-architecture/)
- [Architecture illustration](./03-Finalisation-Phase/assets/multi-region-active-passive-architecture.png)
- [Project overview](../README.md)

Before upload, check that the PDFs open correctly, review the ZIP contents,
add any authentic tutor feedback you received, and retain AWS screenshots or
logs only if you actually collect them. Do not present the local mocked tests
as live AWS validation.
