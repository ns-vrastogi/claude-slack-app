#!/usr/bin/env python3
"""
Production Deployment Report Generator
Generates PDF reports for production deployments with deployment, validation, and PDV results.

Usage:
    python3 generate_report.py <deployment_data_json_file>

Example:
    python3 generate_report.py /tmp/deployment_data.json
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
import sys
import json
import os


def get_status_color(status):
    """Return color based on status."""
    status_upper = status.upper()
    if 'SUCCESS' in status_upper or 'PASSED' in status_upper or 'OPERATIONAL' in status_upper:
        return colors.HexColor('#28a745')  # Green
    elif 'FAILED' in status_upper or 'ERROR' in status_upper:
        return colors.HexColor('#dc3545')  # Red
    elif 'PARTIAL' in status_upper or 'ATTENTION' in status_upper or 'WARNING' in status_upper:
        return colors.HexColor('#ffc107')  # Yellow/Amber
    else:
        return colors.HexColor('#6c757d')  # Gray


def get_status_symbol(status):
    """Return symbol based on status."""
    status_upper = status.upper()
    if 'SUCCESS' in status_upper or 'PASSED' in status_upper or 'OPERATIONAL' in status_upper:
        return '✅'
    elif 'FAILED' in status_upper or 'ERROR' in status_upper:
        return '❌'
    elif 'PARTIAL' in status_upper or 'ATTENTION' in status_upper or 'WARNING' in status_upper:
        return '⚠️'
    else:
        return '●'


def generate_pdf_report(data, output_path):
    """
    Generate PDF report from deployment data.

    Args:
        data: Dictionary containing deployment information
        output_path: Path to save the PDF file
    """
    # Create PDF document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.75*inch,
        bottomMargin=0.5*inch
    )

    # Container for the 'Flowable' objects
    elements = []

    # Define styles
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )

    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=8,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )

    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        leading=14
    )

    # Extract metadata
    metadata = data.get('metadata', {})
    pops = data.get('pops', {})

    # Title
    elements.append(Paragraph("PRODUCTION DEPLOYMENT COMPREHENSIVE REPORT", title_style))
    elements.append(Spacer(1, 0.3*inch))

    # Metadata section
    elements.append(Paragraph("Deployment Information", heading_style))

    meta_data = [
        ['Deployment Date:', metadata.get('deployment_date', 'N/A')],
        ['Service:', metadata.get('service', 'N/A')],
        ['Release:', metadata.get('release', 'N/A')],
        ['Ansible Config Tag:', metadata.get('ansible_config_tag', 'N/A')],
        ['Ticket:', metadata.get('ticket', 'N/A')],
        ['Jenkins:', metadata.get('jenkins_url', 'N/A')]
    ]

    meta_table = Table(meta_data, colWidths=[2*inch, 5*inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e9ecef')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 0.3*inch))

    # Summary section
    elements.append(Paragraph("Summary", heading_style))

    total_pops = len(pops)
    deployment_success = sum(1 for pop_data in pops.values() if pop_data.get('deployment', {}).get('status') == 'SUCCESS')
    validation_passed = sum(1 for pop_data in pops.values() if pop_data.get('post_validation', {}).get('status') == 'PASSED')
    pdv_passed = sum(1 for pop_data in pops.values() if pop_data.get('pdv_testing', {}).get('status') == 'PASSED')

    # Determine overall status
    if deployment_success == total_pops and validation_passed == total_pops and pdv_passed == total_pops:
        overall_status = "✅ FULLY OPERATIONAL"
        overall_color = colors.HexColor('#28a745')
    elif deployment_success < total_pops:
        overall_status = "❌ DEPLOYMENT FAILED"
        overall_color = colors.HexColor('#dc3545')
    else:
        overall_status = "⚠️ ATTENTION REQUIRED"
        overall_color = colors.HexColor('#ffc107')

    summary_data = [
        ['Total POPs:', f"{total_pops} ({', '.join(pops.keys())})"],
        ['Deployment Status:', f"{deployment_success}/{total_pops} {get_status_symbol('SUCCESS' if deployment_success == total_pops else 'FAILED')}"],
        ['Post-Deployment Validation:', f"{validation_passed}/{total_pops} {get_status_symbol('PASSED' if validation_passed == total_pops else 'FAILED')}"],
        ['Production PDV Testing:', f"{pdv_passed}/{total_pops} {get_status_symbol('PASSED' if pdv_passed == total_pops else 'PARTIAL')}"],
        ['Overall Status:', overall_status]
    ]

    summary_table = Table(summary_data, colWidths=[2.5*inch, 4.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e9ecef')),
        ('BACKGROUND', (1, 4), (1, 4), overall_color),
        ('TEXTCOLOR', (0, 0), (-1, 3), colors.black),
        ('TEXTCOLOR', (1, 4), (1, 4), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTNAME', (1, 4), (1, 4), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.4*inch))

    # Detailed results by POP
    elements.append(Paragraph("Detailed Results by POP", heading_style))
    elements.append(Spacer(1, 0.1*inch))

    for pop_name, pop_data in pops.items():
        # POP heading
        elements.append(Paragraph(f"POP: {pop_name.upper()}", subheading_style))

        # Deployment status
        deployment = pop_data.get('deployment', {})
        deploy_status = deployment.get('status', 'UNKNOWN')
        deploy_symbol = get_status_symbol(deploy_status)

        elements.append(Paragraph(f"<b>1. Jenkins Deployment:</b> {deploy_symbol} {deploy_status}", normal_style))
        if deployment:
            deploy_details = [
                f"   • Build #{deployment.get('build_number', 'N/A')}",
                f"   • Duration: {deployment.get('duration', 'N/A')}",
                f"   • URL: {deployment.get('build_url', 'N/A')}",
                f"   • Timestamp: {deployment.get('timestamp', 'N/A')}"
            ]
            for detail in deploy_details:
                elements.append(Paragraph(detail, normal_style))
        elements.append(Spacer(1, 0.1*inch))

        # Post-deployment validation
        validation = pop_data.get('post_validation', {})
        val_status = validation.get('status', 'UNKNOWN')
        val_symbol = get_status_symbol(val_status)

        elements.append(Paragraph(f"<b>2. Post-Deployment Validation:</b> {val_symbol} {val_status}", normal_style))
        if validation and 'nodes' in validation:
            for node, node_status in validation['nodes'].items():
                node_symbol = get_status_symbol(node_status)
                elements.append(Paragraph(f"   • {node}: {node_symbol} {node_status}", normal_style))
            elements.append(Paragraph(f"   • Timestamp: {validation.get('timestamp', 'N/A')}", normal_style))
        elements.append(Spacer(1, 0.1*inch))

        # PDV testing
        pdv = pop_data.get('pdv_testing', {})
        pdv_status = pdv.get('status', 'UNKNOWN')
        pdv_symbol = get_status_symbol(pdv_status)

        elements.append(Paragraph(f"<b>3. Production PDV Testing:</b> {pdv_symbol} {pdv_status}", normal_style))

        if pdv:
            # Job 1
            job1 = pdv.get('job1', {})
            job1_status = job1.get('status', 'UNKNOWN')
            job1_symbol = get_status_symbol(job1_status)
            elements.append(Paragraph(f"   • Job 1 (Node 02 - dst {job1.get('tunnel_dst', 'N/A')}): {job1_symbol} {job1_status}", normal_style))
            if job1:
                elements.append(Paragraph(f"      - Node: {job1.get('node', 'N/A')}", normal_style))
                elements.append(Paragraph(f"      - Jenkins: {job1.get('jenkins', 'N/A')}", normal_style))
                elements.append(Paragraph(f"      - Tunnel: {job1.get('tunnel', 'N/A')}", normal_style))
                elements.append(Paragraph(f"      - Traffic: {job1.get('traffic', 'N/A')}", normal_style))

            # Job 2
            job2 = pdv.get('job2', {})
            job2_status = job2.get('status', 'UNKNOWN')
            job2_symbol = get_status_symbol(job2_status)
            elements.append(Paragraph(f"   • Job 2 (Node 01 - dst {job2.get('tunnel_dst', 'N/A')}): {job2_symbol} {job2_status}", normal_style))
            if job2:
                elements.append(Paragraph(f"      - Node: {job2.get('node', 'N/A')}", normal_style))
                elements.append(Paragraph(f"      - Jenkins: {job2.get('jenkins', 'N/A')}", normal_style))
                elements.append(Paragraph(f"      - Tunnel: {job2.get('tunnel', 'N/A')}", normal_style))
                elements.append(Paragraph(f"      - Traffic: {job2.get('traffic', 'N/A')}", normal_style))

            elements.append(Paragraph(f"   • Timestamp: {pdv.get('timestamp', 'N/A')}", normal_style))

        # Overall POP status
        pop_overall = "✅ FULLY OPERATIONAL"
        pop_overall_color = colors.HexColor('#28a745')

        if deploy_status != 'SUCCESS':
            pop_overall = "❌ DEPLOYMENT FAILED"
            pop_overall_color = colors.HexColor('#dc3545')
        elif val_status != 'PASSED' or pdv_status != 'PASSED':
            pop_overall = "⚠️ DEPLOYMENT OK, VALIDATION ISSUES"
            pop_overall_color = colors.HexColor('#ffc107')

        status_para = Paragraph(f"<b>Status: {pop_overall}</b>", normal_style)
        elements.append(Spacer(1, 0.1*inch))
        elements.append(status_para)

        # Separator
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("─" * 80, normal_style))
        elements.append(Spacer(1, 0.2*inch))

    # Issues section (if any)
    issues = []
    for pop_name, pop_data in pops.items():
        deployment = pop_data.get('deployment', {})
        validation = pop_data.get('post_validation', {})
        pdv = pop_data.get('pdv_testing', {})

        if deployment.get('status') != 'SUCCESS':
            issues.append(f"❌ {pop_name.upper()} - Deployment FAILED")
        elif validation.get('status') != 'PASSED':
            issues.append(f"⚠️ {pop_name.upper()} - Post-Deployment Validation FAILED")
        elif pdv.get('status') != 'PASSED':
            issues.append(f"⚠️ {pop_name.upper()} - Production PDV Testing FAILED")

    if issues:
        elements.append(Paragraph("Issues Requiring Attention", heading_style))
        for issue in issues:
            elements.append(Paragraph(issue, normal_style))
            elements.append(Spacer(1, 0.05*inch))
        elements.append(Spacer(1, 0.2*inch))

    # Next steps
    elements.append(Paragraph("Next Steps", heading_style))
    if not issues:
        elements.append(Paragraph("✅ All deployments completed successfully. No action required.", normal_style))
    else:
        elements.append(Paragraph("⚠️ The following actions are recommended:", normal_style))
        elements.append(Spacer(1, 0.1*inch))
        for pop_name, pop_data in pops.items():
            if pop_data.get('deployment', {}).get('status') != 'SUCCESS':
                elements.append(Paragraph(f"• {pop_name.upper()}: Investigate deployment failure and retry", normal_style))
            elif pop_data.get('post_validation', {}).get('status') != 'PASSED':
                elements.append(Paragraph(f"• {pop_name.upper()}: Review post-deployment validation errors", normal_style))
            elif pop_data.get('pdv_testing', {}).get('status') != 'PASSED':
                elements.append(Paragraph(f"• {pop_name.upper()}: Investigate PDV testing failure and re-run", normal_style))

    # Footer with generation timestamp
    elements.append(Spacer(1, 0.4*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    elements.append(Paragraph(f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))

    # Build PDF
    doc.build(elements)
    print(f"✅ PDF report generated: {output_path}")


def main():
    """Main function to handle command-line execution."""
    if len(sys.argv) < 2:
        print("Usage: python3 generate_report.py <deployment_data_json_file>")
        print("\nExample:")
        print("  python3 generate_report.py /tmp/deployment_data.json")
        sys.exit(1)

    json_file = sys.argv[1]

    if not os.path.exists(json_file):
        print(f"❌ Error: File not found: {json_file}")
        sys.exit(1)

    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON format: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        sys.exit(1)

    # Extract metadata for filename
    metadata = data.get('metadata', {})
    service = metadata.get('service', 'unknown')
    date = metadata.get('deployment_date', datetime.now().strftime('%Y-%m-%d'))
    pops = list(data.get('pops', {}).keys())
    pops_str = '-'.join(pops) if pops else 'unknown'

    # Create reports directory
    reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
    os.makedirs(reports_dir, exist_ok=True)

    # Generate output filename
    output_filename = f"production_deployment_report_{service}_{date}_{pops_str}.pdf"
    output_path = os.path.join(reports_dir, output_filename)

    # Generate PDF
    try:
        generate_pdf_report(data, output_path)
        print(f"\n📄 Report saved to: {output_path}")
        print(f"\nTo view: open \"{output_path}\"")
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
