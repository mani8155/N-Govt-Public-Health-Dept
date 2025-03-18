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

from user_management.settings_views import API_STUDIO_URL
from vas1 import institution


def download_pdf(request, psk_id):
    # fetch the master data
    url = f"{API_STUDIO_URL}getapi/phpm02_application_301_master_dc1/{psk_id}"
    headers = {}
    master_response = requests.get(url, headers=headers)

    if master_response.status_code != 200:
        return HttpResponse("Failed to fetch data for psk_id", status=500)

    master_data = master_response.json()
    document_id = master_data.get('document_id')
    print("document_id:", document_id)

    # Fetch institution data using psk_id
    institution_id = master_data.get('institution_psk_id')
    print("institution_id:", institution_id)
    institution_url = f"{API_STUDIO_URL}getapi/phpm02_institution_59/{institution_id}"
    institution_response = requests.get(institution_url, headers=headers)

    if institution_response.status_code != 200:
        return HttpResponse("Failed to fetch institution data", status=500)

    institution_data = institution_response.json()
    institution_name = institution_data.get('institution_name', 'N/A')  # Default to 'N/A' if not found
    institution_address_text = institution_data.get('institution_address_text', 'N/A')  # Default to 'N/A'

    # Fetch course data based on course_id
    course_id = master_data.get('course_type_psk_id')
    print("course_id:", course_id)
    course_url = f"{API_STUDIO_URL}getapi/phpm02_course_55/{course_id}"
    course_response = requests.get(course_url, headers=headers)

    if course_response.status_code != 200:
        return HttpResponse("Failed to fetch course data", status=500)

    course_data = course_response.json()
    print("course_data:", course_data)
    selected_course = course_data.get('course_type', 'Unknown Course')  # Default to 'Unknown Course' if not found


    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Sample styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    table_style = styles['Normal']

    # Set margin and content width
    margin_left, margin_top, margin_right, margin_bottom = 50, 20, 50, 20
    content_width = letter[0] - margin_left - margin_right
    content_height = letter[1] - margin_top - margin_bottom

    # Modify title_style to include space after the title
    title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], fontName='Times-Roman', fontSize=20, leading=24,
                                 alignment=1, spaceAfter=25)

    # Title paragraph (this will now have space after it)
    course_name = course_data.get('course_name')
    title = Paragraph(f"{course_name} Course Details", title_style)

    table_style = ParagraphStyle('Normal', parent=styles['Normal'], fontName='Times-Roman', fontSize=12, leading=18,
                                 alignment=0, spaceBefore=2, spaceAfter=2)

    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontName='Times-Roman', fontSize=12, leading=18,
                                  alignment=0, spaceBefore=2, spaceAfter=2, leftIndent=-27.5)

    signature_style = ParagraphStyle('Normal', parent=styles['Normal'], fontName='Times-Roman', fontSize=12, leading=18,
                                     alignment=2, spaceBefore=2, spaceAfter=2, leftIndent=-27.5)

    document_id = Paragraph(f"<b>Applicant ID:</b> {document_id}", normal_style)
    # print("document_id:", document_id)
    institution_name = Paragraph(f"<b>Institution Name:</b> {institution_name}", normal_style)
    institution_address_text = Paragraph(f"<b>Institution Address:</b> {institution_address_text}", normal_style)
    spacer1 = Spacer(1, 20)
    selected_course = course_data.get('course_type')
    print("selected_course:", selected_course)
    checklist_data = {}

    if selected_course == "MBBS":
        checklist_data = {
            "check1": {
                "label": "1. Copy of G.O in which the institution was permitted to start MBBS., MD., MS., Medical Course",
                "go_number": master_data.get('gov_order_number', 'NA'),
                "date": master_data.get('gov_order_date', 'NA'),
            },
            "check2": {
                "label": "2. Whether the students of the institution were already permitted for the practical training in PHC. If so copies enclosed.",
                "go_number": master_data.get('permitted_in_phc_gov_no', 'NA'),
                "date": master_data.get('permitted_in_phc_gov_date', 'NA'),
            },
            "check3": {
                "label": "3. Continuance of provisional affiliation granted by the Tamil Nadu MGR Medical University.",
                "go_number": master_data.get('affiliation_mgr_university_gov_no', 'NA'),
                "date": master_data.get('affiliation_mgr_university_gov_date', 'NA'),
            },
            "check4": {
                "label": "4. Whether the Management is willing to pay the fees prescribed by the Government to impart training to their Medical students.",
                "go_number": "NA",
                "date": "NA",
            },
            "check5": {
                "label": "5. Copy of Letter of Permission from the Medical Council of India New Delhi.",
                "go_number": master_data.get('letter_from_medical_council_gov_no', 'NA'),
                "date": master_data.get('letter_from_medical_council_gov_date', 'NA'),
            },
            "check6": {
                "label": "6. Copy of essentiality Certificate letter from the Health and Family Welfare Department.",
                "go_number": master_data.get('permitted_in_phc_gov_no', 'NA'),
                "date": master_data.get('permitted_in_phc_gov_date', 'NA'),
            },
            "check7": {
                "label": "7. Previous Tie-Up with Public Health Department G.O and G.O date.",
                "go_number": master_data.get('affiliation_mgr_university_gov_no', 'NA'),
                "date": master_data.get('affiliation_mgr_university_gov_date', 'NA'),
            },
            "check8": {
                "label": "8.No due certificate of your previous batch of the internship training fees payment along with a copy of the challan duly authenticated by the Chairman of the Trust.",
                "go_number": "NA",
                "date": "NA",
            },
            "check9": {
                "label": "9. Consent Letter for 1000 Sq.Ft building.",
                "go_number": master_data.get('permitted_in_phc_gov_no', 'NA'),
                "date": master_data.get('permitted_in_phc_gov_date', 'NA'),
            },
            "check10": {
                "label": "10. List of Students studied currently in your Institutions (1st, 2nd, 3rd, 4th and 5th)",
                "go_number": "NA",
                "date": "NA",
            },
            "check11": {
                "label": "11. In case, whether the students were already permitted to avail facilities in PHC and more than 3 years for Medical courses whether the institution is willing to remit double the rate of fee structure to each student for continuance of permission.",
                "go_number": "NA",
                "date": "NA",
            },
        }
    elif selected_course == "Nursing":
        checklist_data = {
            "check1": {
                "label": "1. Copy of G.O in which the institution was permitted to start Nursing Medical Course",
                "go_number": master_data.get('gov_order_number'),
                "date": master_data.get('gov_order_date'),
            },
            "check2": {
                "label": "2. Whether the students of the institution were already permitted for the practical training in "
                         "PHC. If so copies enclosed.",
                "go_number": master_data.get('permitted_in_phc_gov_no'),
                "date": master_data.get('permitted_in_phc_gov_date'),
            },
            "check3": {
                "label": "3. In case of Degree Nursing students, whether Tamil Nadu Nurses and Midwives Council has "
                         "granted recognition to the institution to conduct Degree in Nursing course (Evidence Produced). ",
                "go_number": master_data.get('tnnmc_gov_no'),
                "date": master_data.get('tnnmc_gov_date'),
            },
            "check4": {
                "label": "4. Copy of the List of Recognized Colleges in the Tamil Nadu Nurses and Midwives Council Web "
                         "site (Evidence Produced).",
                "go_number": master_data.get('recognized_colleges_list_tn_gov_no'),
                "date": master_data.get('recognized_colleges_list_tn_gov_date'),
            },
            "check5": {
                "label": "5. In case of Degree Nursing students, whether Indian Nursing Council has granted recognition "
                         "to the institution to conduct Degree in Nursing course (Evidence Produced)",
                "go_number": master_data.get('recognized_colleges_list_inc_gov_no'),
                "date": master_data.get('recognized_colleges_list_inc_gov_date'),
            },
            "check6": {
                "label": "6. Copy of the List of Recognized Colleges in the Indian Nursing Council Web site (Evidence "
                         "Produced).",
                "go_number": master_data.get('inc_council_website_go_no'),
                "date": master_data.get('inc_council_website_go_date'),
            },
            "check7": {
                "label": "7. Continuance of provisional affiliation granted by the Tamil Nadu MGR Medical University ("
                         "Evidence Produced).",
                "go_number": master_data.get('affiliation_mgr_university_gov_no'),
                "date": master_data.get('affiliation_mgr_university_gov_date'),
            },
            "check8": {
                "label": "8. Whether the Management is willing to pay the fees prescribed by the Government to impart "
                         "training to their Medical students.",
                "go_number": "NA",
                "date": "NA",
            },
            "check9": {
                "label": "9. Own Hospital Detail (Copy of Memorandum of Understanding [MOU]) ",
                "go_number": "NA",
                "date": "NA",
            },
            "check10": {
                "label": "10. Own Hospital Detail (Certificate of Registration of Clinical Establishment Act.)",
                "go_number": "NA",
                "date": "NA",
            },
            "check11": {
                "label": "11. Previous Tie-Up with Public Health Department G.O and G.O date",
                "go_number": master_data.get('previous_tieup_gov_no'),
                "date": master_data.get('previous_tieup_gov_date'),
            },
            "check12": {
                "label": "12. No due certificate of your previous batch of the internship training fees payment (Model "
                         "Enclosed) along with a copy of the challan duly authenticated by the Chairman of the Trust *",
                "go_number": "NA",
                "date": "NA",
            },
            "check13": {
                "label": "13. Consent Letter for 1000 Sq.Ft building.",
                "go_number": "NA",
                "date": "NA",
            },
            "check14": {
                "label": "14. List of Students studied currently in your Institutions (1st, 2nd, 3rd, 4th and 5th)",
                "go_number": "NA",
                "date": "NA",
            },
            "check15": {
                "label": "15. In case, whether the students were already permitted to avail facilities in PHC and more "
                         "than 3 years for Medical courses whether the institution is willing to remit double the rate of "
                         "fee structure to each student for continuance of permission.",
                "go_number": "NA",
                "date": "NA",
            },
        }
    elif selected_course == "DGMN":
        checklist_data = {
            "check1": {
                "label": "1.Copy of G.O in which the institution was permitted to start Para Medical Course",
                "go_number": master_data.get('gov_order_number'),
                "date": master_data.get('gov_order_date'),
            },
            "check2": {
                "label": "2. Whether the students of the institution were already permitted for the practical training in "
                         "PHC. If so copies enclosed.",
                "go_number": master_data.get('permitted_in_phc_gov_no'),
                "date": master_data.get('permitted_in_phc_gov_date'),
            },
            "check3": {
                "label": "3. In case of Degree DGNM students, whether Tamil Nadu Nurses and Midwives Council has "
                         "granted recognition to the institution to conduct Degree in DGNM course (Evidence Produced). ",
                "go_number": master_data.get('tnnmc_gov_no'),
                "date": master_data.get('tnnmc_gov_date'),
            },
            "check4": {
                "label": "4. Copy of the List of Recognized Colleges in the Tamil Nadu Nurses and Midwives Council Web "
                         "site (Evidence Produced).",
                "go_number": master_data.get('recognized_colleges_list_tn_gov_no'),
                "date": master_data.get('recognized_colleges_list_tn_gov_date'),
            },
            "check5": {
                "label": "5. In case of Degree DGNM students, whether Indian DGNM Council has granted recognition "
                         "to the institution to conduct Degree in DGNM course (Evidence Produced)",
                "go_number": master_data.get('recognized_colleges_list_inc_gov_no'),
                "date": master_data.get('recognized_colleges_list_inc_gov_date'),
            },
            "check6": {
                "label": "6. Copy of the List of Recognized Colleges in the Indian DGNM Council Web site (Evidence "
                         "Produced).",
                "go_number": master_data.get('inc_council_website_go_no'),
                "date": master_data.get('inc_council_website_go_date'),
            },

            "check8": {
                "label": "7. Whether the Management is willing to pay the fees prescribed by the Government to impart "
                         "training to their Medical students.",
                "go_number": "NA",
                "date": "NA",
            },
            "check9": {
                "label": "8. Own Hospital Detail (Copy of Memorandum of Understanding [MOU]) ",
                "go_number": "NA",
                "date": "NA",
            },
            "check10": {
                "label": "9. Own Hospital Detail (Certificate of Registration of Clinical Establishment Act.)",
                "go_number": "NA",
                "date": "NA",
            },
            "check11": {
                "label": "10. Previous Tie-Up with Public Health Department G.O and G.O date",
                "go_number": master_data.get('previous_tieup_gov_no'),
                "date": master_data.get('previous_tieup_gov_date'),
            },
            "check12": {
                "label": "11. No due certificate of your previous batch of the internship training fees payment (Model "
                         "Enclosed) along with a copy of the challan duly authenticated by the Chairman of the Trust *",
                "go_number": "NA",
                "date": "NA",
            },
            "check13": {
                "label": "12. Consent Letter for 1000 Sq.Ft building.",
                "go_number": "NA",
                "date": "NA",
            },
            "check14": {
                "label": "13. List of Students studied currently in your Institutions (1st, 2nd, 3rd, 4th and 5th)",
                "go_number": "NA",
                "date": "NA",
            },
            "check15": {
                "label": "14. In case, whether the students were already permitted to avail facilities in PHC and more "
                         "than 3 years for Medical courses whether the institution is willing to remit double the rate of "
                         "fee structure to each student for continuance of permission.",
                "go_number": "NA",
                "date": "NA",
            },
        }
    elif selected_course == "ANM":
        checklist_data = {
            "check1": {
                "label": "1.Copy of G.O in which the institution was permitted to start Para Medical Course",
                "go_number": master_data.get('gov_order_number'),
                "date": master_data.get('gov_order_date'),
            },
            "check2": {
                "label": "2. Whether the students of the institution were already permitted for the practical training in "
                         "PHC. If so copies enclosed.",
                "go_number": master_data.get('permitted_in_phc_gov_no'),
                "date": master_data.get('permitted_in_phc_gov_date'),
            },
            "check3": {
                "label": "3. In case of Certificate Course Nursing students, whether Tamil Nadu Nurses and Midwives "
                         "Council has granted recognition to the institution to conduct Certificate Course in Nursing "
                         "course (Evidence Produced) ",
                "go_number": master_data.get('tnnmc_gov_no'),
                "date": master_data.get('tnnmc_gov_date'),
            },
            "check4": {
                "label": "4. Copy of the List of Recognized Colleges in the Tamil Nadu Nurses and Midwives Council Web "
                         "site (Evidence Produced)",
                "go_number": master_data.get('recognized_colleges_list_tn_gov_no'),
                "date": master_data.get('recognized_colleges_list_tn_gov_date'),
            },

            "check8": {
                "label": "5. Whether the Management is willing to pay the fees prescribed by the Government to impart "
                         "training to their Medical students",
                "go_number": "NA",
                "date": "NA",
            },
            "check9": {
                "label": "6. Own Hospital Detail (copy of Memorandum of Understanding [MOU])",
                "go_number": "NA",
                "date": "NA",
            },
            "check10": {
                "label": "7. Own Hospital Detail (Certificate of Registration of Clinical Establishment Act.,)",
                "go_number": "NA",
                "date": "NA",
            },
            "check11": {
                "label": "8. Previous Tie-Up with Public Health Department G.O and G.O date",
                "go_number": master_data.get('previous_tieup_gov_no'),
                "date": master_data.get('previous_tieup_gov_date'),
            },
            "check12": {
                "label": "9. No due certificate of your previous batch of the internship training fees payment (Model "
                         "Enclosed) along with a copy of the challan duly authenticated by the Chairman of the Trust ",
                "go_number": "NA",
                "date": "NA",
            },
            "check13": {
                "label": "10. Consent Letter for 1000 Sq.Ft building.",
                "go_number": "NA",
                "date": "NA",
            },
            "check14": {
                "label": "11. List of Students studied currently in your Institutions (1st, 2nd, 3rd, 4th and 5th)",
                "go_number": "NA",
                "date": "NA",
            },
            "check15": {
                "label": "12. In case, whether the students were already permitted to avail facilities in PHC and more "
                         "than 3 years for Medical courses whether the institution is willing to remit double the rate of "
                         "fee structure to each student for continuance of permission.",
                "go_number": "NA",
                "date": "NA",
            },

        }

    elif selected_course == "MPHW(M)":
        checklist_data = {
            "check1": {
                "label": "1.Copy of G.O in which the institution was permitted to start Para Medical Course",
                "go_number": master_data.get('gov_order_number'),
                "date": master_data.get('gov_order_date'),
            },
            "check2": {
                "label": "2. Whether the students of the institution were already permitted for the practical training in "
                         "PHC. If so copies enclosed.",
                "go_number": master_data.get('permitted_in_phc_gov_no'),
                "date": master_data.get('permitted_in_phc_gov_date'),
            },

            "check8": {
                "label": "3. Whether the Management is willing to pay the fees prescribed by the Government to impart "
                         "training to their Medical students",
                "go_number": "NA",
                "date": "NA",
            },
            "check9": {
                "label": "4. Own Hospital Detail (copy of Memorandum of Understanding [MOU])",
                "go_number": "NA",
                "date": "NA",
            },
            "check10": {
                "label": "5. Own Hospital Detail (Certificate of Registration of Clinical Establishment Act.,)",
                "go_number": "NA",
                "date": "NA",
            },
            "check11": {
                "label": "6. Previous Tie-Up with Public Health Department G.O and G.O date",
                "go_number": master_data.get('previous_tieup_gov_no'),
                "date": master_data.get('previous_tieup_gov_date'),
            },
            "check12": {
                "label": "7. No due certificate of your previous batch of the internship training fees payment (Model "
                         "Enclosed) along with a copy of the challan duly authenticated by the Chairman of the Trust ",
                "go_number": "NA",
                "date": "NA",
            },
            "check13": {
                "label": "8. Consent Letter for 1000 Sq.Ft building.",
                "go_number": "NA",
                "date": "NA",
            },
            "check14": {
                "label": "9. List of Students studied currently in your Institutions (1st, 2nd, 3rd, 4th and 5th)",
                "go_number": "NA",
                "date": "NA",
            },
            "check15": {
                "label": "10. In case, whether the students were already permitted to avail facilities in PHC and more "
                         "than 3 years for Medical courses whether the institution is willing to remit double the rate of "
                         "fee structure to each student for continuance of permission.",
                "go_number": "NA",
                "date": "NA",
            },
        }

        # Table Data
    table_data = [["Description", "GO Number", "GO Date"], ]

    # Loop through the checklist data and add rows to table
    for key, value in checklist_data.items():
        date_str = value.get('date')  # Use .get() to avoid KeyError

        if not date_str or date_str == 'NA':  # Check for None or 'NA'
            formatted_date = 'NA'
        else:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%d-%m-%Y")
            except ValueError:
                formatted_date = 'Invalid Date'  # Handle invalid date formats
        table_data.append([value['label'], value['go_number'], formatted_date])

    col_widths = [content_width * 0.6, content_width * 0.2, content_width * 0.2]  # Increase the first column width
    table = Table(table_data, colWidths=col_widths)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),  # Header Background Color
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Header Text Color
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Align text horizontally and vertically in center
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Bold Font for headers
        ('FONTSIZE', (0, 0), (-1, -1), 14),  # Increased font size for all cells
        ('BOTTOMPADDING', (0, 0), (-1, 0), 15),  # Increased padding for header row
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),  # Row Background Color
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Border color and width
        ('PADDING', (0, 0), (-1, -1), 10),  # Padding for all cells (increased padding)
        ('ROWHEIGHT', (0, 0), (-1, -1), 40),  # Set row height to 40 (even row height for all rows)
    ]))

    # We can also handle wrapping text in specific columns using Paragraphs instead of plain strings
    # This ensures better text wrapping and control over long text in cells
    for i in range(1, len(table_data)):  # Skip the header row (index 0)
        for j in range(len(table_data[i])):
            table_data[i][j] = Paragraph(table_data[i][j], table_style)  # Wrap text in paragraphs

    # Recreate the table with wrapped text
    table = Table(table_data, colWidths=col_widths)

    # Apply styles again after updating the table with wrapped content
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Text alignment in center
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Roman'),  # Change font to Times New Roman
        ('FONTSIZE', (0, 0), (-1, -1), 14),  # Increased font size for all cells
        ('BOTTOMPADDING', (0, 0), (-1, 0), 15),  # Increased padding for header row
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('PADDING', (0, 0), (-1, -1), 20),  # Padding for all cells (increased padding)
        ('ROWHEIGHT', (0, 0), (-1, -1), 40),  # Set row height to 40 (even row height for all rows)
    ]))

    # Add signature and footer
    signature_style = ParagraphStyle('Normal', parent=styles['Normal'], fontName='Times-Roman', fontSize=12, leading=18,
                                     alignment=2, spaceBefore=2, spaceAfter=2)
    spacer = Spacer(1, 100)
    signature = Paragraph("Seal and Signature of the Principal, College Authority", signature_style)

    # doc.build([title, spacer, table, spacer, signature])
    # doc.build([title, spacer, document_id, institution_name, institution_address_text, spacer1, table, signature])
    doc.build([title, document_id, institution_name, institution_address_text, spacer1, table, spacer, signature])

    # Create filename
    document_id = master_data.get('document_id', 'default_filename')
    file_name = f"{document_id}_{course_name}.pdf"

    # Get PDF from buffer
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'

    institution.work_flow_table_insert(request, psk_id, status="Downloaded")
    institution.application_status_update(psk_id, "Downloaded")

    return response
