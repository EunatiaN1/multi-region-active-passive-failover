#!/usr/bin/env python3
"""Regenerate the three phase PDFs and the Phase 3 final report."""

from __future__ import annotations

import html
import re
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    ListFlowable,
    ListItem,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
)


ROOT = Path(__file__).resolve().parent
STUDENT = "Eunatia Ngobeni"
STUDENT_NUMBER = "92131229"
COURSE = "DLBSEPCP01_E | Cloud Programming"
REVISION_DATE = date.today().strftime("%d %B %Y")
NAVY = colors.HexColor("#10233F")
BLUE = colors.HexColor("#176B87")
CYAN = colors.HexColor("#19B6C8")
INK = colors.HexColor("#203047")
MUTED = colors.HexColor("#627189")
PALE = colors.HexColor("#EAF2F7")

PHASE1 = ROOT / "01-Conception-Phase"
PHASE2 = ROOT / "02-Development-Phase"
PHASE3 = ROOT / "03-Finalisation-Phase"

styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        "BodyPortfolio",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8.6,
        leading=10.8,
        textColor=INK,
        spaceAfter=5.5,
        alignment=TA_LEFT,
    )
)
styles.add(
    ParagraphStyle(
        "TitlePortfolio",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=21,
        leading=25,
        textColor=NAVY,
        spaceAfter=12,
    )
)
styles.add(
    ParagraphStyle(
        "HeadingPortfolio",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=BLUE,
        spaceBefore=7,
        spaceAfter=5,
        keepWithNext=True,
    )
)
styles.add(
    ParagraphStyle(
        "SubheadingPortfolio",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=13,
        textColor=NAVY,
        spaceBefore=5,
        spaceAfter=4,
        keepWithNext=True,
    )
)
styles.add(
    ParagraphStyle(
        "BulletPortfolio",
        parent=styles["BodyPortfolio"],
        leftIndent=12,
        firstLineIndent=-9,
        bulletIndent=0,
        spaceAfter=3,
    )
)


def inline_markup(text: str) -> str:
    links: list[str] = []

    def save_link(match: re.Match[str]) -> str:
        label = html.escape(match.group(1))
        href = html.escape(match.group(2), quote=True)
        links.append(f'<link href="{href}" color="#176B87">{label}</link>')
        return f"@@LINK{len(links) - 1}@@"

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", save_link, text)
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`([^`]+)`", r'<font name="Courier" size="8">\1</font>', text)
    for index, link in enumerate(links):
        text = text.replace(f"@@LINK{index}@@", link)
    return text


def markdown_blocks(
    markdown: str,
    *,
    skip_preamble: bool = False,
) -> list:
    lines = markdown.splitlines()
    flowables: list = []
    paragraph: list[str] = []
    bullets: list[str] = []
    saw_section = not skip_preamble

    def flush_paragraph() -> None:
        if paragraph:
            text = " ".join(part.strip() for part in paragraph)
            flowables.append(Paragraph(inline_markup(text), styles["BodyPortfolio"]))
            paragraph.clear()

    def flush_bullets() -> None:
        if bullets:
            items = [
                ListItem(
                    Paragraph(inline_markup(item), styles["BulletPortfolio"]),
                    leftIndent=10,
                )
                for item in bullets
            ]
            flowables.append(
                ListFlowable(
                    items,
                    bulletType="bullet",
                    start="circle",
                    bulletFontName="Helvetica",
                    bulletFontSize=6,
                    bulletColor=CYAN,
                    leftIndent=13,
                    bulletOffsetY=1,
                    spaceAfter=4,
                )
            )
            bullets.clear()

    index = 0
    while index < len(lines):
        raw = lines[index]
        line = raw.strip()
        if skip_preamble and not saw_section:
            if line.startswith("## "):
                saw_section = True
            else:
                index += 1
                continue

        if line == "<!-- PAGE BREAK -->":
            flush_paragraph()
            flush_bullets()
            flowables.append(PageBreak())
        elif not line:
            flush_paragraph()
            flush_bullets()
        elif line.startswith("# "):
            flush_paragraph()
            flush_bullets()
            flowables.append(Paragraph(inline_markup(line[2:]), styles["TitlePortfolio"]))
        elif line.startswith("## "):
            flush_paragraph()
            flush_bullets()
            flowables.append(
                Paragraph(inline_markup(line[3:]), styles["HeadingPortfolio"])
            )
        elif line.startswith("### "):
            flush_paragraph()
            flush_bullets()
            flowables.append(
                Paragraph(inline_markup(line[4:]), styles["SubheadingPortfolio"])
            )
        elif re.match(r"^(?:[-*]|\d+\.)\s+", line):
            flush_paragraph()
            bullets.append(re.sub(r"^(?:[-*]|\d+\.)\s+", "", line))
        else:
            flush_bullets()
            paragraph.append(line)
        index += 1

    flush_paragraph()
    flush_bullets()
    return flowables


def page_chrome(canvas, doc) -> None:
    canvas.saveState()
    page_width, page_height = doc.pagesize
    canvas.setStrokeColor(PALE)
    canvas.setLineWidth(0.6)
    canvas.line(18 * mm, 15 * mm, page_width - 18 * mm, 15 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 10 * mm, f"{STUDENT}  |  {COURSE}  |  Task 1.1")
    canvas.drawRightString(
        page_width - 18 * mm, 10 * mm, f"{doc.page}"
    )
    canvas.restoreState()


def make_doc(
    path: Path,
    story: list,
    pagesize=A4,
    margins=(19 * mm, 18 * mm),
    cover: tuple[str, str] | None = None,
) -> None:
    left_right, top_bottom = margins
    doc = BaseDocTemplate(
        str(path),
        pagesize=pagesize,
        leftMargin=left_right,
        rightMargin=left_right,
        topMargin=top_bottom,
        bottomMargin=20 * mm,
        title=path.stem.replace("-", " "),
        author=STUDENT,
        subject="Cloud Programming Portfolio, Tasks 1.1.1-1.1.3",
    )
    frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        doc.width,
        doc.height,
        id="main",
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
    )
    def on_page(canvas, page_doc):
        if cover and page_doc.page == 1:
            draw_cover(canvas, pagesize, *cover)
        else:
            page_chrome(canvas, page_doc)

    doc.addPageTemplates([PageTemplate(id="portfolio", frames=frame, onPage=on_page)])
    doc.build(story)


def draw_cover(canvas, pagesize, title: str, subtitle: str) -> None:
    width, height = pagesize
    cover_title = ParagraphStyle(
        "CoverTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=30,
        textColor=colors.white,
        alignment=TA_CENTER,
        spaceAfter=16,
    )
    cover_subtitle = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=14,
        leading=20,
        textColor=colors.HexColor("#D7E7F0"),
        alignment=TA_CENTER,
    )
    info = ParagraphStyle(
        "CoverInfo",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=17,
        textColor=colors.HexColor("#E8F1F6"),
        alignment=TA_CENTER,
    )

    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, width, height, fill=1, stroke=0)
    canvas.setFillColor(CYAN)
    canvas.rect(0, 0, 12, height, fill=1, stroke=0)
    area = width - 90 * mm
    heading = Paragraph(title, cover_title)
    _, heading_height = heading.wrap(area, 160 * mm)
    heading.drawOn(canvas, (width - area) / 2, height * 0.66)
    subheading_par = Paragraph(subtitle, cover_subtitle)
    subheading_par.wrap(area, 80 * mm)
    subheading_par.drawOn(
        canvas, (width - area) / 2, height * 0.66 - heading_height - 10
    )
    details = Paragraph(
        f"<b>{STUDENT}</b><br/>{STUDENT_NUMBER}<br/>{COURSE}<br/>{REVISION_DATE}",
        info,
    )
    details.wrap(area, 80 * mm)
    details.drawOn(canvas, (width - area) / 2, 70 * mm)
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.HexColor("#D7E7F0"))
    canvas.drawCentredString(
        width / 2,
        35 * mm,
        "LIVE STATIC EXPLAINER  |  SEPARATE MULTI-REGION TERRAFORM PROTOTYPE",
    )
    canvas.restoreState()


def build_conception() -> None:
    source = (PHASE1 / "concept-presentation.md").read_text(encoding="utf-8")
    story = markdown_blocks(source)
    story.append(PageBreak())
    story.append(Paragraph("Architecture illustration", styles["HeadingPortfolio"]))
    story.append(
        Paragraph(
            "Conceptual design only. This diagram is not an inventory of deployed AWS resources.",
            styles["BodyPortfolio"],
        )
    )
    image_path = PHASE3 / "assets" / "multi-region-active-passive-architecture.png"
    image = Image(str(image_path))
    max_width = A4[0] - 38 * mm
    max_height = A4[1] - 70 * mm
    scale = min(max_width / image.imageWidth, max_height / image.imageHeight)
    image.drawWidth = image.imageWidth * scale
    image.drawHeight = image.imageHeight * scale
    story.append(image)
    make_doc(PHASE1 / "Task-1.1.1-Phase-1-Conception-Submitted.pdf", story)


SLIDES = [
    (
        "Task 1.1.2 | Development and reflection",
        [
            "Multi-region active-passive failover webpage on AWS.",
            "This presentation distinguishes the live static explainer from the separate Terraform prototype.",
            "The scenario controls illustrate request paths in the browser; they do not change AWS.",
            "Current evidence and limitations are stated explicitly rather than inferred from design diagrams.",
        ],
    ),
    (
        "Problem, audience, and objectives",
        [
            "Explain how a web request can reach an AWS-hosted site and what a regional-failure response could look like.",
            "Primary goals: clear visual communication, repeatable Terraform, HTTPS delivery, and scalable application capacity.",
            "The 99.99% availability target is a design aspiration, not a measured result or provider guarantee.",
            "The sample has no database, session replication, or durable user data.",
        ],
    ),
    (
        "Architecture at a glance",
        [
            "Normal path: visitor → CloudFront → primary ALB → EC2 Auto Scaling application.",
            "Origin failure: selected ALB 5xx responses can cause CloudFront to request the secondary S3 maintenance page.",
            "Route 53 DNS failover appears in the proposed concept but is not present in the Terraform prototype.",
        ],
    ),
    (
        "Live product and scope boundary",
        [
            "The public CloudFront URL hosts the static interactive explainer.",
            "The live static-site deployment uses a private S3 origin and CloudFront Origin Access Control.",
            "The live website is not the multi-region application and does not prove application failover.",
            "The separate multi-region Terraform root has not been applied in AWS.",
        ],
    ),
    (
        "Implementation: primary region",
        [
            "A VPC contains two public subnets in distinct available Availability Zones.",
            "An internet-facing ALB forwards to a target group using the /health endpoint.",
            "The launch template installs a small threaded Python HTTP service managed by systemd.",
            "The application runs as an unprivileged user; instance metadata requires IMDSv2.",
        ],
    ),
    (
        "Implementation: scaling and failover",
        [
            "Auto Scaling defaults: minimum 2, desired 2, maximum 6, CPU target 50%.",
            "CloudFront origin-group failover is configured for HTTP 500, 502, 503, and 504.",
            "The secondary S3 website provides a maintenance response; it is directly reachable over HTTP.",
            "A CloudWatch unhealthy-target alarm publishes to an SNS topic; email is optional and requires confirmation.",
        ],
    ),
    (
        "Security and operating considerations",
        [
            "The ALB accepts origin traffic from CloudFront's managed origin-facing prefix list.",
            "Application instances accept HTTP only from the ALB security group.",
            "The secondary website intentionally permits public reads of index.html only; never store sensitive content there.",
            "The multi-region stack creates billable resources and requires an approved AWS identity, plan review, and cost check.",
        ],
    ),
    (
        "Development and validation",
        [
            "The project history records Terraform 1.12.2 formatting and provider-schema validation as passing.",
            "The history also records eight mocked, plan-only test runs; they create no cloud resources.",
            "Checks cover selected inputs, capacity, network boundaries, health checks, IMDSv2, origin responses, and alarm wiring.",
            "Terraform was unavailable during this package rebuild, so these recorded checks were not rerun.",
        ],
    ),
    (
        "Reflection: limitations and DNS design",
        [
            "The multi-region stack has no current AWS plan, apply, runtime-failover, alarm-delivery, or recovery evidence.",
            "Route 53 records, DNS health checks, a controlled domain, and custom-domain certificates are not implemented.",
            "Direct DNS failover to an S3 website endpoint would not preserve HTTPS.",
            "A future design must test health-check reachability, HTTPS on both targets, DNS caching, recovery, and rollback.",
        ],
    ),
    (
        "Finalisation and next steps",
        [
            "The PDF and ZIP package is rebuilt from current editable sources; historical deployment claims are not reused as evidence.",
            "Next: obtain approval and credentials, review cost and plan, deploy in an isolated account, and collect timestamped test results.",
            "Then test origin failure, alarms, restoration, and measured recovery; only afterward complete and test the DNS layer.",
            "Project: https://github.com/EunatiaN1/multi-region-active-passive-failover",
            "Live static explainer: https://d2quyljtx3dqoe.cloudfront.net/",
        ],
    ),
]


def draw_slide(canvas, title: str, bullets: list[str], page: int) -> None:
    width, height = landscape(A4)
    canvas.saveState()
    canvas.setFillColor(colors.HexColor("#F6F9FC"))
    canvas.rect(0, 0, width, height, fill=1, stroke=0)
    canvas.setFillColor(NAVY)
    canvas.rect(0, height - 95, width, 95, fill=1, stroke=0)
    canvas.setFillColor(CYAN)
    canvas.rect(0, height - 95, 9, 95, fill=1, stroke=0)
    title_style = ParagraphStyle(
        "SlideTitle",
        fontName="Helvetica-Bold",
        fontSize=25 if len(title) < 38 else 21,
        leading=30,
        textColor=colors.white,
    )
    title_par = Paragraph(inline_markup(title), title_style)
    _, title_height = title_par.wrap(width - 90, 65)
    title_par.drawOn(canvas, 48, height - 55 - title_height / 2)

    body_style = ParagraphStyle(
        "SlideBody",
        fontName="Helvetica",
        fontSize=16,
        leading=23,
        textColor=INK,
        spaceAfter=13,
        bulletIndent=0,
    )
    if page == 1:
        canvas.setFillColor(BLUE)
        canvas.roundRect(45, 120, width - 90, 240, 18, fill=1, stroke=0)
        text_color_style = ParagraphStyle(
            "SlideIntro",
            parent=body_style,
            fontSize=19,
            leading=28,
            textColor=colors.white,
            spaceAfter=16,
        )
        y = 325
        for item in bullets:
            paragraph = Paragraph(f"•  {inline_markup(item)}", text_color_style)
            _, item_height = paragraph.wrap(width - 140, 70)
            y -= item_height
            paragraph.drawOn(canvas, 72, y)
            y -= 12
    elif page == 3:
        image_path = PHASE3 / "assets" / "multi-region-active-passive-architecture.png"
        image = Image(str(image_path))
        max_width, max_height = width - 110, 310
        scale = min(max_width / image.imageWidth, max_height / image.imageHeight)
        image_width, image_height = image.imageWidth * scale, image.imageHeight * scale
        image.drawWidth, image.drawHeight = image_width, image_height
        image.drawOn(canvas, (width - image_width) / 2, 150)
        canvas.setFillColor(MUTED)
        canvas.setFont("Helvetica-Oblique", 11)
        canvas.drawCentredString(
            width / 2,
            132,
            "Conceptual diagram; it does not represent deployed resources.",
        )
        y = 112
        short_style = ParagraphStyle(
            "SlideDiagramCaption",
            parent=body_style,
            fontSize=12,
            leading=15,
            spaceAfter=3,
        )
        for item in bullets:
            paragraph = Paragraph(f"•  {inline_markup(item)}", short_style)
            _, item_height = paragraph.wrap(width - 100, 42)
            paragraph.drawOn(canvas, 52, y - item_height)
            y -= item_height + 2
    else:
        y = height - 135
        for item in bullets:
            paragraph = Paragraph(f"•  {inline_markup(item)}", body_style)
            _, item_height = paragraph.wrap(width - 115, 95)
            y -= item_height
            paragraph.drawOn(canvas, 58, y)
            y -= 18

    canvas.setStrokeColor(colors.HexColor("#D8E2EC"))
    canvas.line(45, 42, width - 45, 42)
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(MUTED)
    canvas.drawString(46, 27, f"{STUDENT}  |  {COURSE}  |  Revised {REVISION_DATE}")
    canvas.drawRightString(width - 46, 27, f"{page:02d} / 10")
    canvas.restoreState()


def build_development_slides() -> None:
    path = PHASE2 / "Task-1.1.2-Phase-2-Development-Submitted.pdf"
    canvas = __import__("reportlab.pdfgen.canvas", fromlist=["canvas"]).Canvas(
        str(path), pagesize=landscape(A4), pageCompression=1
    )
    canvas.setTitle("Task 1.1.2 - Development and Reflection")
    canvas.setAuthor(STUDENT)
    canvas.setSubject("Ten-slide Cloud Programming implementation presentation")
    for page, (title, bullets) in enumerate(SLIDES, start=1):
        draw_slide(canvas, title, bullets, page)
        canvas.showPage()
    canvas.save()


def build_phase3_pdfs() -> None:
    abstract_path = PHASE3 / "finalisation-phase-abstract.md"
    abstract_source = abstract_path.read_text(encoding="utf-8")
    abstract_story = markdown_blocks(abstract_source)
    make_doc(PHASE3 / "Task-1.1.3-Phase-3-Abstract.pdf", abstract_story)

    technical_source = (PHASE3 / "final-report-technical.md").read_text(
        encoding="utf-8"
    )
    report_story = [PageBreak()]
    report_story.extend(markdown_blocks(abstract_source))
    report_story.append(PageBreak())
    report_story.extend(markdown_blocks(technical_source, skip_preamble=True))
    make_doc(
        PHASE3 / "Task-1.1.3-Phase-3-Final-Report.pdf",
        report_story,
        cover=(
            "Task 1.1.3 | Finalisation",
            "Final report: abstract and technical description (7 pages total)",
        ),
    )


def main() -> None:
    build_conception()
    build_development_slides()
    build_phase3_pdfs()
    for path in (
        PHASE1 / "Task-1.1.1-Phase-1-Conception-Submitted.pdf",
        PHASE2 / "Task-1.1.2-Phase-2-Development-Submitted.pdf",
        PHASE3 / "Task-1.1.3-Phase-3-Abstract.pdf",
        PHASE3 / "Task-1.1.3-Phase-3-Final-Report.pdf",
    ):
        print(f"{path.relative_to(ROOT.parent)}: {path.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
