import re
from datetime import datetime
from collections import defaultdict
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

class LogAuditor:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
        self.connections = []
        self.performance_issues = []
        self.security_events = []
        self.database_queries = []
        self.api_calls = []
        
    def analyze_line(self, line, timestamp=None):
        line_lower = line.lower()
        
        if 'error' in line_lower or 'exception' in line_lower:
            self.errors.append({'time': timestamp, 'message': line})
        elif 'warning' in line_lower or 'warn' in line_lower:
            self.warnings.append({'time': timestamp, 'message': line})
        else:
            self.info.append({'time': timestamp, 'message': line})
        
        if 'conectado' in line_lower or 'connected' in line_lower:
            ip_match = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', line)
            if ip_match:
                self.connections.append({'time': timestamp, 'ip': ip_match.group(), 'message': line})
        
        if 'timeout' in line_lower or 'slow' in line_lower or 'latency' in line_lower:
            self.performance_issues.append({'time': timestamp, 'message': line})
        
        if 'authentication' in line_lower or 'login' in line_lower or 'unauthorized' in line_lower:
            self.security_events.append({'time': timestamp, 'message': line})
        
        if 'select' in line_lower or 'insert' in line_lower or 'update' in line_lower or 'delete' in line_lower:
            self.database_queries.append({'time': timestamp, 'message': line})
        
        if 'api' in line_lower or 'rest' in line_lower or 'endpoint' in line_lower:
            self.api_calls.append({'time': timestamp, 'message': line})
    
    def get_statistics(self):
        return {
            'total_lines': len(self.errors) + len(self.warnings) + len(self.info),
            'errors': len(self.errors),
            'warnings': len(self.warnings),
            'info': len(self.info),
            'connections': len(self.connections),
            'performance_issues': len(self.performance_issues),
            'security_events': len(self.security_events),
            'database_queries': len(self.database_queries),
            'api_calls': len(self.api_calls)
        }
    
    def generate_pdf_report(self, filename, client, server, service, duration):
        doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        story.append(Paragraph("egSYS Monitor", title_style))
        story.append(Paragraph("Relatório de Auditoria de Logs", styles['Heading2']))
        story.append(Spacer(1, 0.3*inch))
        
        info_data = [
            ['Cliente:', client.upper()],
            ['Servidor:', server.upper()],
            ['Serviço:', service.upper()],
            ['Data:', datetime.now().strftime('%d/%m/%Y %H:%M:%S')],
            ['Duração:', f'{duration}s']
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph("Resumo Executivo", heading_style))
        
        stats = self.get_statistics()
        stats_data = [
            ['Métrica', 'Quantidade', 'Status'],
            ['Total de Linhas', str(stats['total_lines']), '✓'],
            ['Erros', str(stats['errors']), '✗' if stats['errors'] > 0 else '✓'],
            ['Avisos', str(stats['warnings']), '⚠' if stats['warnings'] > 0 else '✓'],
            ['Conexões', str(stats['connections']), '✓'],
            ['Problemas de Performance', str(stats['performance_issues']), '⚠' if stats['performance_issues'] > 0 else '✓'],
            ['Eventos de Segurança', str(stats['security_events']), '⚠' if stats['security_events'] > 0 else '✓'],
            ['Consultas ao Banco', str(stats['database_queries']), '✓'],
            ['Chamadas API', str(stats['api_calls']), '✓']
        ]
        
        stats_table = Table(stats_data, colWidths=[2.5*inch, 1.5*inch, 1*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 9)
        ]))
        
        story.append(stats_table)
        story.append(Spacer(1, 0.3*inch))
        
        if self.errors:
            story.append(PageBreak())
            story.append(Paragraph("Erros Críticos", heading_style))
            error_data = [['Timestamp', 'Mensagem']]
            for error in self.errors[:20]:
                error_data.append([
                    error['time'] or 'N/A',
                    error['message'][:100] + '...' if len(error['message']) > 100 else error['message']
                ])
            
            error_table = Table(error_data, colWidths=[1.5*inch, 4.5*inch])
            error_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d32f2f')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            story.append(error_table)
        
        if self.warnings:
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("Avisos", heading_style))
            warning_data = [['Timestamp', 'Mensagem']]
            for warning in self.warnings[:20]:
                warning_data.append([
                    warning['time'] or 'N/A',
                    warning['message'][:100] + '...' if len(warning['message']) > 100 else warning['message']
                ])
            
            warning_table = Table(warning_data, colWidths=[1.5*inch, 4.5*inch])
            warning_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f57c00')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            story.append(warning_table)
        
        if self.connections:
            story.append(PageBreak())
            story.append(Paragraph("Análise de Conexões", heading_style))
            conn_data = [['Timestamp', 'IP', 'Evento']]
            for conn in self.connections[:30]:
                conn_data.append([
                    conn['time'] or 'N/A',
                    conn.get('ip', 'N/A'),
                    conn['message'][:80] + '...' if len(conn['message']) > 80 else conn['message']
                ])
            
            conn_table = Table(conn_data, colWidths=[1.5*inch, 1.5*inch, 3*inch])
            conn_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#388e3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            story.append(conn_table)
        
        story.append(PageBreak())
        story.append(Paragraph("Recomendações", heading_style))
        
        recommendations = []
        if stats['errors'] > 10:
            recommendations.append("• Alto número de erros detectado. Investigar causas raiz imediatamente.")
        if stats['performance_issues'] > 5:
            recommendations.append("• Problemas de performance identificados. Revisar otimizações.")
        if stats['security_events'] > 0:
            recommendations.append("• Eventos de segurança detectados. Revisar políticas de acesso.")
        if not recommendations:
            recommendations.append("• Sistema operando dentro dos parâmetros normais.")
        
        for rec in recommendations:
            story.append(Paragraph(rec, styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(
            f"Relatório gerado automaticamente por egSYS Monitor em {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}",
            ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
        ))
        
        doc.build(story)
        return filename
