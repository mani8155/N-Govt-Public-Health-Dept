import requests
import json
from datetime import datetime
from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from django.shortcuts import render
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.platypus import Spacer
from user_management.views import API_STUDIO_URL


def final_report_download(request, psk_id):
    url = f"{API_STUDIO_URL}getapi/phpm02_application_301_master_dc1/{psk_id}"
    headers = {}
    master_response = requests.get(url, headers=headers)

    if master_response.status_code == 200:
        parent_data = master_response.json()
        document_date = parent_data.get('document_date')
        date_str = document_date  # Use .get() to avoid KeyError
        if not date_str or date_str == 'NA':  # Check for None or 'NA'
            formatted_date = 'NA'
        else:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%d-%m-%Y")
        institution_psk_id = parent_data.get('institution_psk_id')
        course_id = parent_data.get('course_type_psk_id')
        # return HttpResponse("Failed to fetch data for psk_id", status=500)

    url = f"{API_STUDIO_URL}getapi/phpm02_institution_59/{institution_psk_id}"
    headers = {}
    institution_response = requests.get(url, headers=headers)

    if institution_response.status_code == 200:
        institution_data = institution_response.json()
        institution_name = institution_data.get('institution_name')
        institution_address_text = institution_data.get('institution_address_text')
        institution_distirict_psk_id = institution_data.get('institution_distirict_psk_id')

    url = f"{API_STUDIO_URL}getapi/phpm02_course_55/{course_id}"
    headers = {}
    course_response = requests.get(url, headers=headers)

    if course_response.status_code == 200:
        course_data = course_response.json()
        course_name = course_data.get('course_name')
        course_type = course_data.get('course_type')
        course_duration = course_data.get('course_duration')

    url = f"{API_STUDIO_URL}getapi/phpm02_district_51/{institution_distirict_psk_id}"
    headers = {}
    district_response = requests.get(url, headers=headers)

    if district_response.status_code == 200:
        district_data = district_response.json()
        district_name = district_data.get('district_name').capitalize()

    url = f"{API_STUDIO_URL}getapi/phpm02_application_303_phc_dc3"

    payload = json.dumps({
        "queries": [
            {
                "field": "parent_psk_id",
                "value": psk_id,
                "operation": "equal"
            }
        ],
        "search_type": "first"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code == 200:
        app_data = response.json()

        parent_psk_id = app_data.get('parent_psk_id', 'NA')
        phc_psk_id = app_data.get('name_of_phc_pskid', 'NA')

    url = f"{API_STUDIO_URL}getapi/phpm02_phc_54/{phc_psk_id}"
    headers = {}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        phc_data = response.json()
        phc_name = phc_data.get('phc_name')

    url = f"{API_STUDIO_URL}getapi/phpm02_application_308_final_order_dc8"

    headers = {'Content-Type': 'application/json'}

    # Payload should be sent only for POST requests
    payload = json.dumps({
        "queries": [{"field": "parent_psk_id", "value": psk_id, "operation": "equal"}],
        "search_type": "all"
    })

    # Sending POST request
    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        final_order = response.json()
        final_order_id = final_order[0].get('final_order_id')
        order_date = final_order[0].get('final_order_date')
        date_str = order_date  # Use .get() to avoid KeyError
        if not date_str or date_str == 'NA':  # Check for None or 'NA'
            final_order_date = 'NA'
        else:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            final_order_date = date_obj.strftime("%d-%m-%Y")

    url = f"{API_STUDIO_URL}getapi/phpm02_application_302_student_dc2"

    headers = {'Content-Type': 'application/json'}

    # Payload should be sent only for POST requests
    payload = json.dumps({
        "queries": [{"field": "parent_psk_id", "value": psk_id, "operation": "equal"}],
        "search_type": "all"
    })

    # Sending POST request
    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        student_data = response.json()
        year_or_semester_list = [year['year_or_semester'] for year in student_data]
        starting_year = year_or_semester_list[0]
        final_year = year_or_semester_list[-1]


    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Define the styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], fontName='Times-Bold', fontSize=14, leading=24,
                                 alignment=0, spaceAfter=0)
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontName='Times-Roman', fontSize=14, leading=18,
                                  alignment=0, spaceBefore=2, spaceAfter=2, leftIndent=-27.5)
    text_indent_style = ParagraphStyle('Normal', parent=styles['Normal'], fontName='Times-Roman', fontSize=14,
                                       leading=18, alignment=0, spaceBefore=2, spaceAfter=2, leftIndent=25,
                                       firstLineIndent=-30)
    list_indent_style = ParagraphStyle('Normal', parent=styles['Normal'], fontName='Times-Roman', fontSize=14,
                                       leading=18, alignment=0, spaceBefore=2, spaceAfter=2, leftIndent=45,
                                       firstLineIndent=-50)
    para_style = ParagraphStyle('Normal', parent=styles['Normal'], fontName='Times-Roman', fontSize=13, leading=18,
                                alignment=0, spaceBefore=2, spaceAfter=2, leftIndent=15)
    table_style = ParagraphStyle('Normal', parent=styles['Normal'], fontName='Times-Roman', fontSize=14, leading=15,
                                 alignment=0, spaceBefore=0, spaceAfter=0, leftIndent=15)

    table_data = [
        ["", ""],
        ["From", "To"],
        ["The Concerned District Health", "The Chairman/ Principal,"],
        ["Officer,", "{}".format(institution_name)],
        ["{}".format(district_name), "{}".format(institution_address_text)],
    ]

    margin_left, margin_top, margin_right, margin_bottom = 50, 20, 50, 20
    content_width = letter[0] - margin_left - margin_right
    content_height = letter[1] - margin_top - margin_bottom
    col_widths = [content_width * 0.5, content_width * 0.5]

    # Create the table with wrapped text for each column
    for i in range(1, len(table_data)):  # Skip the header row (index 0)
        for j in range(len(table_data[i])):
            table_data[i][j] = Paragraph(table_data[i][j], table_style)  # Wrap text in paragraphs

    table = Table(table_data, colWidths=col_widths)

    # Apply styles to the table
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),  # Header background color
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Header text color
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Align text to the left
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Roman'),  # Bold font for headers
        ('FONTSIZE', (0, 0), (-1, -1), 12),  # Font size for all cells
        ('BOTTOMPADDING', (0, 0), (-1, 0), 2),  # Padding for header row
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),  # Row background color
        ('GRID', (0, 0), (-1, -1), 1, colors.white),  # Table border
        ('PADDING', (0, 0), (-1, -1), 2),  # Padding for all cells
        ('ROWHEIGHT', (0, 0), (-1, -1), -1),  # Set row height
    ]))

    # Add space and title
    title = Paragraph("DEPARTMENT OF PUBLIC HEALTH AND PREVENTIVE MEDICINE", title_style)
    spacer1 = Spacer(1, 10)
    Plain_text5 = Paragraph(
        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;R. No. <b>{final_order_id}</b>,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Dated: <b>{final_order_date}</b>",
        text_indent_style)
    spacer2 = Spacer(1, 10)
    Plain_text6 = Paragraph(f"Sir/ Madam,", text_indent_style)
    spacer3 = Spacer(1, 10)
    Plain_text7 = Paragraph(
        f"Sub:&nbsp;Public Health and Preventive Medicine - Nursing/School Education - {institution_name}, {institution_address_text}, {district_name} - Tie-up arrangements for Community level Training with Rural Primary Health Centre <b>{phc_name}</b> and Urban Primary Health Centre <b>{district_name}</b> for their {course_type} for {course_duration} years from the academic year to Permission granted - regarding.",
        text_indent_style)
    Plain_text8 = Paragraph(
        f"Public Health and Preventive Medicine - Nursing/School Education - {institution_name}, {institution_address_text}, {district_name} - Tie-up arrangements for Community level Training with Rural Primary Health Centre <b>{phc_name}</b> and Urban Primary Health Centre <b>{phc_name}</b> {district_name} for their DGNM, B.Sc., (N), M.Sc.,(N) and P.B.B.Sc.,(N) for {course_duration} years from the academic year to Permission granted - regarding.",
        text_indent_style)
    spacer4 = Spacer(1, 10)
    Plain_text8 = Paragraph(
        f"Ref: 1. G.O.(Ms) No.{parent_data.get('permitted_in_phc_gov_no', 'NA')}, Health and Family Welfare (PME-2) Department, Dated: {parent_data.get('permitted_in_phc_gov_date', 'NA')}.",
        list_indent_style)
    Plain_text9 = Paragraph(
        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. Letter from Chairman/Principal, {institution_name}, {institution_address_text}, dated: {final_order_date}. Dated: {final_order_date}.",
        list_indent_style)
    spacer5 = Spacer(1, 10)
    Plain_text10 = Paragraph(
        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;******",
        text_indent_style)
    spacer6 = Spacer(1, 10)
    Plain_text11 = Paragraph(
        f"In response to the letter 2nd cited, I have to state that permission is accorded to the Principal, <b>{institution_name}</b>, {institution_address_text}, {district_name} to have Tie-up arrangements with Rural Primary Health Centre <b>{phc_name}</b> and Urban Primary Health Centre <b>{phc_name}</b>, {district_name} for Community Level Training of their <b>{course_name}</b>  for {course_duration} years from the academic years <b>{starting_year}</b> to <b>{final_year}</b> subject to the following conditions:-",
        normal_style)
    spacer7 = Spacer(1, 10)
    Plain_text12 = Paragraph(
        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;i.&nbsp;&nbsp;The Faculty of the Institution should accompany the trainees.",
        list_indent_style)
    Plain_text13 = Paragraph(
        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ii.&nbsp;&nbsp;Students should be deputed in small batches.",
        list_indent_style)
    Plain_text14 = Paragraph(
        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;iii.&nbsp;Training should be given without any hindrance to the normal functioning of the Rural Primary Health Centre <b>{phc_name}</b> and Urban Primary Health Centre, {district_name} and without any financial implications to the Government.",
        list_indent_style)
    Plain_text15 = Paragraph(
        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;iv.&nbsp;The Institution should pay the prescribed fees for the students who are deputed for training as per G.O.(D) No.{parent_data.get('permitted_in_phc_gov_no', 'NA')}, Health and Family welfare (PME. 1) Department, dated: {parent_data.get('permitted_in_phc_gov_date', 'NA')} and obey the conditions stipulated in G. O. (D) No. {parent_data.get('permitted_in_phc_gov_no', 'NA')}, Health and Family Welfare (MCA.2) Department, dated: {parent_data.get('permitted_in_phc_gov_date', 'NA')}.",
        list_indent_style)
    Plain_text16 = Paragraph(
        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;v.&nbsp;The Primary Health centre should maintain 1:3 student to Patient ratio every day during Training based on rotation.",
        list_indent_style)
    Plain_text17 = Paragraph(
        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;vi.&nbsp;Trainees may be utilised in the Field after having given adequate briefing.",
        list_indent_style)
    Plain_text18 = Paragraph(
        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;vii.&nbsp;The Institution should construct a Multipurpose Hall to the trainees for the purpose of conducting training class in the Primary Health Centre <b>{phc_name}</b>, ------------------, {district_name} or do its equivalent.",
        list_indent_style)
    spacer8 = Spacer(1, 30)
    Plain_text19 = Paragraph(
        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Concerned District Health Officer,",
        normal_style)
    Plain_text20 = Paragraph(
        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;District.",
        normal_style)
    Plain_text21 = Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Copy to", normal_style)
    Plain_text22 = Paragraph(
        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. The Block Medical Officer,",
        normal_style)
    Plain_text23 = Paragraph(
        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{phc_name},",
        normal_style)
    Plain_text24 = Paragraph(
        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{district_name}.",
        normal_style)
    spacer9 = Spacer(1, 15)
    Plain_text25 = Paragraph(
        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. The Medical Officer,,",
        normal_style)
    Plain_text26 = Paragraph(
        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{phc_name},",
        normal_style)
    Plain_text27 = Paragraph(
        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{district_name}.",
        normal_style)
    spacer10 = Spacer(1, 15)
    Plain_text28 = Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Copy to", normal_style)
    Plain_text29 = Paragraph(
        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The Director of Public Health and Preventive Medicine,",
        normal_style)
    Plain_text30 = Paragraph(
        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Chennai-06.",
        normal_style)

    doc.build([title, table, spacer1, Plain_text5, spacer2, Plain_text6, spacer3, Plain_text7, spacer4, Plain_text8,
               Plain_text9, spacer5, Plain_text10, spacer6, Plain_text11, spacer7, Plain_text12, Plain_text13,
               Plain_text14, Plain_text15, Plain_text16, Plain_text17, Plain_text18, spacer8, Plain_text19,
               Plain_text20, Plain_text21, Plain_text22, Plain_text23, Plain_text24, spacer9, Plain_text25,
               Plain_text26, Plain_text27, spacer10, Plain_text28, Plain_text29, Plain_text30])

    # 

    # Save the PDF to the buffer
    buffer.seek(0)
    document_id = "document"
    file_name = f"{document_id}.pdf"

    # Create the response with the PDF content
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'

    return response
