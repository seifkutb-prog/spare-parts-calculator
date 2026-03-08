from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime
import io

NAVY  = colors.HexColor('#0F3460')
RED_A = colors.HexColor('#FFD7D7')
AMB_B = colors.HexColor('#FFF3CD')
GRN_C = colors.HexColor('#D4EDDA')
LIGHT = colors.HexColor('#EFF6FF')

ABC_BG = {'A': RED_A, 'B': AMB_B, 'C': GRN_C}


def build_pdf(results, summary, station_name):
    """
    Generate a PDF report and return it as bytes.
    """
    buf    = io.BytesIO()
    doc    = SimpleDocTemplate(buf, pagesize=A4,
                               rightMargin=1.5*cm, leftMargin=1.5*cm,
                               topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story  = []

    title_style = ParagraphStyle('T', parent=styles['Title'],
                                  textColor=NAVY, fontSize=18, spaceAfter=4)
    sub_style   = ParagraphStyle('S', parent=styles['Normal'],
                                  textColor=colors.HexColor('#6B7280'), fontSize=10)
    head_style  = ParagraphStyle('H', parent=styles['Heading2'],
                                  textColor=NAVY, fontSize=12, spaceBefore=12)

    story.append(Paragraph('Spare Parts Intelligence Report', title_style))
    story.append(Paragraph(
        f'Station: {station_name}  |  Date: {datetime.today().strftime("%Y-%m-%d")}  |  Parts: {summary["total_parts"]}',
        sub_style))
    story.append(Spacer(1, 0.4*cm))

    # Summary table
    sum_data = [
        ['Total Parts', 'Class A', 'Class B', 'Class C', 'Stock Value (EGP)', 'Avg Turnover'],
        [summary['total_parts'], summary['class_a'], summary['class_b'],
         summary['class_c'], f"{summary['total_stock_value']:,.0f}", summary['avg_turnover']],
    ]
    st = Table(sum_data, colWidths=[2.5*cm]*6)
    st.setStyle(TableStyle([
        ('BACKGROUND', (0,0),(-1,0), NAVY), ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'), ('FONTSIZE',(0,0),(-1,-1),9),
        ('ALIGN',(0,0),(-1,-1),'CENTER'), ('GRID',(0,0),(-1,-1),0.3,colors.lightgrey),
        ('BACKGROUND',(0,1),(-1,1),LIGHT),
        ('FONTNAME',(0,1),(-1,1),'Helvetica-Bold'), ('FONTSIZE',(0,1),(-1,1),11),
    ]))
    story.append(st)
    story.append(Spacer(1, 0.4*cm))

    # Full parts table
    story.append(Paragraph('Parts Detail — Sorted by Annual Value (ABC Order)', head_style))
    headers = ['Part Name','ABC','Cons/Mo','ROP','SS','Rec Qty','EOQ','Turnover','Stock Val (EGP)']
    tdata   = [headers]
    for item in results:
        tdata.append([
            item['part_name'][:35],
            item.get('abc_class','?'),
            item['consumption_rate'],
            item['reorder_point'],
            item['safety_stock'],
            item['recommended_qty'],
            item['eoq'],
            item['turnover_rate'],
            f"{item['total_stock_value']:,.0f}",
        ])
    col_w = [5.2*cm,1.2*cm,1.8*cm,1.5*cm,1.2*cm,1.8*cm,1.2*cm,1.8*cm,2.5*cm]
    dt = Table(tdata, colWidths=col_w)
    style_cmds = [
        ('BACKGROUND',(0,0),(-1,0),NAVY), ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'), ('FONTSIZE',(0,0),(-1,-1),7),
        ('ALIGN',(0,0),(-1,-1),'CENTER'), ('ALIGN',(0,1),(0,-1),'LEFT'),
        ('GRID',(0,0),(-1,-1),0.2,colors.lightgrey),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[LIGHT, colors.white]),
    ]
    for i, item in enumerate(results, start=1):
        bg = ABC_BG.get(item.get('abc_class','C'), GRN_C)
        style_cmds.append(('BACKGROUND',(1,i),(1,i),bg))
        style_cmds.append(('FONTNAME',(1,i),(1,i),'Helvetica-Bold'))
    dt.setStyle(TableStyle(style_cmds))
    story.append(dt)

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()

