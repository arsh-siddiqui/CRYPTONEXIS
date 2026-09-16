import os
import json
import logging
import datetime
from typing import Optional, Dict, Any
from analysis.case_models import Case
from services.case_service import CaseService

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

logger = logging.getLogger(__name__)

class ReportService:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.output_dir = os.path.join(os.getcwd(), "reports")
        os.makedirs(self.output_dir, exist_ok=True)
        self.case_service = CaseService()

    def _get_explorer_link(self, blockchain: str, address: Optional[str] = None, tx_hash: Optional[str] = None) -> str:
        bc = blockchain.upper() if blockchain else ""
        if bc == "BITCOIN":
            if tx_hash: return f"https://www.blockchain.com/explorer/transactions/btc/{tx_hash}"
            if address: return f"https://www.blockchain.com/explorer/addresses/btc/{address}"
        elif bc == "ETHEREUM":
            if tx_hash: return f"https://etherscan.io/tx/{tx_hash}"
            if address: return f"https://etherscan.io/address/{address}"
        elif bc == "BSC":
            if tx_hash: return f"https://bscscan.com/tx/{tx_hash}"
            if address: return f"https://bscscan.com/address/{address}"
        return ""

    def _get_safe_filename(self, case: Case, ext: str) -> str:
        case_num = case.case_number.replace("/", "_").replace("\\", "_")
        return os.path.join(self.output_dir, f"{case_num}_investigation_report.{ext}")

    def generate_pdf(self, case_id: int) -> Optional[str]:
        if not REPORTLAB_AVAILABLE:
            logger.error("reportlab not installed, PDF generation disabled.")
            return None

        case = self.case_service.get_case(case_id)
        if not case:
            return None

        filepath = self._get_safe_filename(case, "pdf")
        
        doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=16, alignment=1, spaceAfter=20)
        heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=14, spaceBefore=15, spaceAfter=10, textColor=colors.HexColor("#2C3E50"))
        normal_style = styles['Normal']
        normal_style.fontSize = 10
        normal_style.spaceAfter = 6
        alert_style = ParagraphStyle('Alert', parent=styles['Normal'], fontSize=12, textColor=colors.red, alignment=1, spaceAfter=15)
        
        story = []
        
        # Title
        story.append(Paragraph("CRYPTONEXIS", title_style))
        story.append(Paragraph("Blockchain OSINT & Cryptocurrency Forensic Intelligence Report", ParagraphStyle('SubTitle', parent=title_style, fontSize=12)))
        
        data_mode = self.config.get("DATA_MODE", "LIVE").upper()
        if data_mode == "DEMO":
            story.append(Paragraph("<b>*** DEMO DATA - NOT ACTUAL BLOCKCHAIN EVIDENCE ***</b>", alert_style))

        # Case Information
        story.append(Paragraph("Case Information", heading_style))
        case_info = [
            ["Case Number:", case.case_number],
            ["Title:", case.title],
            ["Status:", case.status],
            ["Priority:", case.priority],
            ["Created:", case.created_at],
            ["Primary Wallet:", case.primary_wallet or "N/A"],
            ["Blockchain:", case.primary_blockchain or "N/A"]
        ]
        t = Table(case_info, colWidths=[120, 400])
        t.setStyle(TableStyle([
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(t)
        
        # Investigation Scope
        story.append(Paragraph("Investigation Scope", heading_style))
        story.append(Paragraph(case.description or "No description provided.", normal_style))
        story.append(Paragraph(f"<b>Data Mode:</b> {data_mode}", normal_style))
        
        # Wallets Investigated
        story.append(Paragraph("Wallets Investigated", heading_style))
        if case.wallets:
            wallet_data = [["Address", "Blockchain", "Role", "Label"]]
            for w in case.wallets:
                wallet_data.append([w.wallet_address, w.blockchain, w.role, w.label or ""])
            wt = Table(wallet_data, colWidths=[240, 80, 80, 120])
            wt.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#34495E")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 6),
                ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ]))
            story.append(wt)
        else:
            story.append(Paragraph("No wallets attached to this case.", normal_style))

        # Evidence Index
        story.append(Paragraph("Evidence Index", heading_style))
        if case.evidence:
            ev_data = [["Type", "Title", "Source", "Date"]]
            for ev in case.evidence:
                ev_data.append([ev.evidence_type, ev.title, ev.source, ev.created_at[:10] if ev.created_at else ""])
            evt = Table(ev_data, colWidths=[100, 240, 100, 80])
            evt.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#34495E")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 6),
                ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ]))
            story.append(evt)
        else:
            story.append(Paragraph("No evidence items attached.", normal_style))

        # Limitations & Data Provenance
        story.append(Paragraph("Limitations & Data Provenance", heading_style))
        disclaimer = (
            "This report is generated from the current snapshot of the Cryptonexis investigation state. "
            "All findings reflect application-observed data or provider-reported data at the time of recording. "
            "Explorer links are provided as navigation references and do not by themselves constitute evidence. "
            "Application-generated risk assessments are analytical indicators, not definitive proof of criminality."
        )
        story.append(Paragraph(disclaimer, normal_style))
        
        if data_mode == "DEMO":
            story.append(Paragraph("<b>DEMO MODE ACTIVE:</b> The data presented here is synthesized for demonstration purposes and does not represent actual blockchain intelligence.", normal_style))
            
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"Report Generated: {datetime.datetime.now(datetime.timezone.utc).isoformat()}", normal_style))

        try:
            doc.build(story)
            return filepath
        except Exception as e:
            logger.error(f"Failed to build PDF: {e}")
            return None

    def generate_html(self, case_id: int) -> Optional[str]:
        case = self.case_service.get_case(case_id)
        if not case:
            return None

        filepath = self._get_safe_filename(case, "html")
        data_mode = self.config.get("DATA_MODE", "LIVE").upper()
        
        demo_warning = ""
        if data_mode == "DEMO":
            demo_warning = "<div class='alert'>*** DEMO DATA - NOT ACTUAL BLOCKCHAIN EVIDENCE ***</div>"
            
        wallet_rows = ""
        for w in case.wallets:
            link = self._get_explorer_link(w.blockchain, address=w.wallet_address)
            anchor = f"<a href='{link}' target='_blank'>{w.wallet_address}</a>" if link else w.wallet_address
            wallet_rows += f"<tr><td>{anchor}</td><td>{w.blockchain}</td><td>{w.role}</td><td>{w.label or ''}</td></tr>"
            
        evidence_rows = ""
        for ev in case.evidence:
            evidence_rows += f"<tr><td>{ev.evidence_type}</td><td>{ev.title}</td><td>{ev.description}</td><td>{ev.source}</td></tr>"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>CRYPTONEXIS Report - {case.case_number}</title>
            <style>
                body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #333; line-height: 1.6; margin: 40px auto; max-width: 900px; padding: 20px; }}
                h1, h2, h3 {{ color: #2C3E50; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 14px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #34495E; color: white; }}
                .alert {{ background-color: #e74c3c; color: white; padding: 15px; text-align: center; font-weight: bold; margin-bottom: 20px; }}
                .meta-table td {{ border: none; padding: 4px; }}
                .meta-table {{ width: auto; margin-bottom: 0; }}
                .footer {{ margin-top: 40px; font-size: 12px; color: #7f8c8d; border-top: 1px solid #eee; padding-top: 20px; }}
            </style>
        </head>
        <body>
            <center>
                <h1>CRYPTONEXIS</h1>
                <h3>Blockchain OSINT & Cryptocurrency Forensic Intelligence Report</h3>
            </center>
            
            {demo_warning}
            
            <h2>Case Information</h2>
            <table class="meta-table">
                <tr><td><b>Case Number:</b></td><td>{case.case_number}</td></tr>
                <tr><td><b>Title:</b></td><td>{case.title}</td></tr>
                <tr><td><b>Status:</b></td><td>{case.status}</td></tr>
                <tr><td><b>Priority:</b></td><td>{case.priority}</td></tr>
                <tr><td><b>Created:</b></td><td>{case.created_at}</td></tr>
            </table>

            <h2>Investigation Scope</h2>
            <p>{case.description or "No description provided."}</p>
            <p><b>Data Mode:</b> {data_mode}</p>
            
            <h2>Wallets Investigated</h2>
            <table>
                <tr><th>Address</th><th>Blockchain</th><th>Role</th><th>Label</th></tr>
                {wallet_rows}
            </table>
            
            <h2>Evidence Index</h2>
            <table>
                <tr><th>Type</th><th>Title</th><th>Description</th><th>Source</th></tr>
                {evidence_rows}
            </table>
            
            <h2>Limitations & Data Provenance</h2>
            <p>This report is generated from the current snapshot of the Cryptonexis investigation state. All findings reflect application-observed data or provider-reported data at the time of recording. Explorer links are provided as navigation references and do not by themselves constitute evidence. Application-generated risk assessments are analytical indicators, not definitive proof of criminality.</p>
            
            <div class="footer">
                Report Generated: {datetime.datetime.now(datetime.timezone.utc).isoformat()}
            </div>
        </body>
        </html>
        """
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return filepath
        except Exception as e:
            logger.error(f"Failed to write HTML report: {e}")
            return None
