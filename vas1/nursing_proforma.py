import requests
from django.contrib import messages
from django.shortcuts import render, redirect
import requests as req
from user_management.views import API_STUDIO_URL
from vas1.applicant_user_master import get_applicant_user_data
import json
from datetime import datetime
from vas1 import institution
from vas1.mbbs_proforma import ApplicationTableName, ApplicationStudentTable, get_file_psk_id, nursing_student_data_get, \
    ApplicationPHCTable, ApplicationCheckListTable, insert_application_phc
import fitz
import os
from io import BytesIO


def nursing_application_navigation(request):
    saved_username = request.COOKIES.get('saved_username', None)
    applicant_data = get_applicant_user_data(request, username=saved_username)
    institution_id = applicant_data.get('institution_name')
    check_app = institution.check_application(institution_id)

    for check in check_app:
        course_master_obj = institution.course_id_data_get(check.get('course_type_psk_id'))

        # Ensure course_master_obj is not None and has 'course_type'
        if course_master_obj and course_master_obj.get('course_type') == "Nursing":
            return redirect('nursing_update', check['psk_id'])

    # If no application matches the condition, redirect to 'anm_application'
    return redirect('nursingapplication')


def nursingapplication(request):
    saved_username = request.COOKIES.get('saved_username', None)
    applicant_data = get_applicant_user_data(request, username=saved_username)
    institution_id = applicant_data.get('institution_name')
    psk_id = applicant_data.get('psk_id')

    institution_obj = institution.institution_id_data_get(int(institution_id))
    course_data = institution.course_data_get(_type="Nursing")
    print(course_data)
    company = institution.company_master_data_get()[0]

    current_date = datetime.now().strftime("%Y-%m-%d")

    if request.method == "POST":

        # upper Card data
        institution_psk_id = institution_id
        year_of_establishment = request.POST.get("year_of_establishment")
        course_type_psk_id = request.POST.get("course_type_psk_id")
        academic_year = request.POST.get("academic_year")
        document_id = request.POST.get("document_id")
        document_date = request.POST.get("document_date")

        # 1. Copy of G.O in which the institution was permitted to start MBBS., MD., MS., Medical Course
        gov_order_number = request.POST.get("gov_order_number")
        gov_order_date = request.POST.get("gov_order_date")
        gov_order_upload_uid = request.FILES.get("gov_order_upload_uid")

        # 2.Whether the students of the institution were already permitted for the practical training in PHC. If so
        # copies enclosed.
        permitted_select = request.POST.get("permitted_select")

        if permitted_select == "yes":
            permitted_in_phc_gov_no = request.POST.get("permitted_in_phc_gov_no")
            permitted_in_phc_gov_date = request.POST.get("permitted_in_phc_gov_date")
            permitted_in_phc_upload_uid = request.FILES.get("permitted_in_phc_upload_uid")
        else:
            permitted_in_phc_gov_no = None
            permitted_in_phc_gov_date = None
            permitted_in_phc_upload_uid = None

        # 3 . nursing Tamil Nadu Nurses and Midwives Council
        tnnmc_gov_no = request.POST.get("tnnmc_gov_no")
        tnnmc_gov_date = request.POST.get("tnnmc_gov_date")
        affiliation_mgr_university_acc_date = request.POST.get("affiliation_mgr_university_acc_date")
        tnnmc_gov_upload_uid = request.FILES.get("tnnmc_gov_upload_uid")

        # 4. Recognized Colleges in Tamil Nadu Nurses and Midwives Council Web site
        recognized_colleges_list_tn_gov_no = request.POST.get("recognized_colleges_list_tn_gov_no")
        recognized_colleges_list_tn_gov_date = request.POST.get("recognized_colleges_list_tn_gov_date")
        recognized_colleges_list_tn_gov_acc_date = request.POST.get("recognized_colleges_list_tn_gov_acc_date")
        recognized_colleges_list_tn_upload_uid = request.FILES.get("recognized_colleges_list_tn_upload_uid")

        # 5. Recognized Colleges in Indian Nursing Council
        recognized_colleges_list_inc_gov_no = request.POST.get("recognized_colleges_list_inc_gov_no")
        recognized_colleges_list_inc_gov_date = request.POST.get("recognized_colleges_list_inc_gov_date")
        recognized_colleges_list_inc_acc_date = request.POST.get("recognized_colleges_list_inc_acc_date")
        recognized_colleges_list_inc_upload_uid = request.FILES.get("recognized_colleges_list_inc_upload_uid")

        # 6. List of Recognized Colleges in the Indian Nursing Council Web site
        inc_council_website_go_no = request.POST.get("inc_council_website_go_no")
        inc_council_website_go_date = request.POST.get("inc_council_website_go_date")
        inc_council_website_go_acc_date = request.POST.get("inc_council_website_go_acc_date")
        inc_council_website_upload_uid = request.FILES.get("inc_council_website_upload_uid")

        # 7. Provisional affiliation granted by Tamil Nadu MGR Medical University
        affiliation_mgr_university_gov_no = request.POST.get("affiliation_mgr_university_gov_no")
        affiliation_mgr_university_gov_date = request.POST.get("affiliation_mgr_university_gov_date")
        affiliation_mgr_university_gov_acc_date = request.POST.get("affiliation_mgr_university_gov_acc_date")
        affiliation_mgr_university_upload_uid = request.FILES.get("affiliation_mgr_university_upload_uid")

        # 8. Willingness to pay fees for training
        # pay_fees_by_upload_uid = request.FILES.get("pay_fees_by_upload_uid")
        pay_fees_by_upload = request.POST.get("pay_fees_by_upload")

        # 9. In case, whether the students were already permitted to avail facilities in PHC and more than 3 years
        # for Medical courses whether the institution is willing to remit double the rate of fee structure to each
        # student for continuance of permission.
        double_rate_fees = request.POST.get("double_rate_fees")

        # 9. Own Hospital Detail (MOU)
        own_hospital_mou_upload_uid = request.FILES.get("own_hospital_mou_upload_uid")

        # 10. Own Hospital Detail (Clinical Establishment Act Certificate)
        own_hospital_clinical_establishment_upload_uid = request.FILES.get(
            "own_hospital_clinical_establishment_upload_uid")

        # 11. Previous Tie-Up with Public Health Department
        # previous_tieup_gov_no = request.POST.get("previous_tieup_gov_no")
        # previous_tieup_gov_date = request.POST.get("previous_tieup_gov_date")
        # pervious_tieup_upload_uid = request.FILES.get("pervious_tieup_upload_uid")

        # 12. No due certificate for internship training fees payment
        no_dues_certificate_upload_uid = request.FILES.get("no_dues_certificate_upload_uid")

        # 13. Consent Letter for 1000 Sq.Ft building
        consent_letter_building_upload_uid = request.FILES.get("consent_letter_building_upload_uid")

        # Now process and save the data as required

        payload = {
            "data": {
                "institution_psk_id": institution_psk_id,
                "year_of_establishment": year_of_establishment,
                "course_type_psk_id": course_type_psk_id,
                "accademic_year": academic_year,
                "document_id": document_id,
                "document_date": document_date,

                # 1. Copy of G.O in which the institution was permitted to start MBBS., MD., MS., Medical Course
                "gov_order_number": gov_order_number,
                "gov_order_date": gov_order_date,

                # 2. Whether the students of the institution were already permitted for the practical training in
                # PHC. If so copies enclosed.
                "permitted_in_phc_gov_no": permitted_in_phc_gov_no,
                # "permitted_in_phc_gov_date": permitted_in_phc_gov_date,

                # 3. Nursing Tamil Nadu Nurses and Midwives Council
                "tnnmc_gov_no": tnnmc_gov_no,
                "tnnmc_gov_date": tnnmc_gov_date,
                "affiliation_mgr_university_acc_date": affiliation_mgr_university_acc_date,

                # 4. Recognized Colleges in Tamil Nadu Nurses and Midwives Council Website
                "recognized_colleges_list_tn_gov_no": recognized_colleges_list_tn_gov_no,
                "recognized_colleges_list_tn_gov_date": recognized_colleges_list_tn_gov_date,
                "recognized_colleges_list_tn_gov_acc_date": recognized_colleges_list_tn_gov_acc_date,

                # 5. Recognized Colleges in Indian Nursing Council
                "recognized_colleges_list_inc_gov_no": recognized_colleges_list_inc_gov_no,
                "recognized_colleges_list_inc_gov_date": recognized_colleges_list_inc_gov_date,
                "recognized_colleges_list_inc_acc_date": recognized_colleges_list_inc_acc_date,

                # 6. List of Recognized Colleges in the Indian Nursing Council Website
                "inc_council_website_go_no": inc_council_website_go_no,
                "inc_council_website_go_acc_date": inc_council_website_go_acc_date,
                # "inc_council_website_go_date": inc_council_website_go_date,

                # 7. Provisional affiliation granted by Tamil Nadu MGR Medical University
                "affiliation_mgr_university_gov_no": affiliation_mgr_university_gov_no,
                "affiliation_mgr_university_gov_date": affiliation_mgr_university_gov_date,
                "affiliation_mgr_university_gov_acc_date": affiliation_mgr_university_gov_acc_date,

                "pay_fees_by_upload_uid": pay_fees_by_upload,
                "pervious_tieup_upload_uid": double_rate_fees,

                "application_status": "Draft",
                "created_by": saved_username,

            }
        }

        if permitted_in_phc_gov_date:
            payload["data"]["permitted_in_phc_gov_date"] = permitted_in_phc_gov_date

        if inc_council_website_go_date:
            payload["data"]["inc_council_website_go_date"] = inc_council_website_go_date

        # Send POST request to API to save application data
        dc1url = f"{API_STUDIO_URL}postapi/create/{ApplicationTableName}"

        headers = {'Content-Type': 'application/json'}
        response = req.post(dc1url, headers=headers, data=json.dumps(payload))
        print(response.text)

        if response.status_code == 200:
            # If successful, handle file uploads
            res_data = response.json()
            rec_parent_id = res_data['psk_id']

            file_fields = [

                ('gov_order_upload_uid', gov_order_upload_uid),
                ('permitted_in_phc_upload_uid', permitted_in_phc_upload_uid),
                ('tnnmc_gov_upload_uid', tnnmc_gov_upload_uid),
                ('recognized_colleges_list_tn_upload_uid', recognized_colleges_list_tn_upload_uid),
                ('recognized_colleges_list_inc_upload_uid', recognized_colleges_list_inc_upload_uid),
                ('inc_council_website_upload_uid', inc_council_website_upload_uid),
                ('affiliation_mgr_university_upload_uid', affiliation_mgr_university_upload_uid),
                # ('pay_fees_by_upload_uid', pay_fees_by_upload_uid),
                ('own_hospital_mou_upload_uid', own_hospital_mou_upload_uid),
                ('own_hospital_clinical_establishment_upload_uid', own_hospital_clinical_establishment_upload_uid),
                # ('pervious_tieup_upload_uid', pervious_tieup_upload_uid),
                ('no_dues_certificate_upload_uid', no_dues_certificate_upload_uid),
                ('consent_letter_building_upload_uid', consent_letter_building_upload_uid),

            ]

            # 2Mb condition

            for field_name, upload_file in file_fields:
                if not upload_file:  # Skip if no file is uploaded
                    continue

                url = f"{API_STUDIO_URL}crudapp/upload/media/v3/{ApplicationTableName}_media"

                upload_file.seek(0)  # Ensure cursor is at the start
                file_stream = BytesIO(upload_file.read())  # Convert to BytesIO

                # Open PDF from byte stream
                pdf_document = fitz.open("pdf", file_stream)
                pdf_page_count = pdf_document.page_count
                pdf_document.close()

                # Get file size in KB
                upload_file.seek(0, os.SEEK_END)
                pdf_size_kb = upload_file.tell() / 1024  # Convert bytes to KB
                upload_file.seek(0)  # Reset cursor

                # Prepare attachment content
                attach_content = {
                    "pdf_name": upload_file.name,
                    "pdf_page_count": pdf_page_count,
                    "pdf_size": round(pdf_size_kb, 2),
                    "pdf_uploaded": "Yes"
                }

                payload = {'parent_psk_id': rec_parent_id, 'attachment_content': json.dumps(attach_content)}

                files = {
                    'media': (field_name, upload_file, 'image/png')
                }

                headers = {}  # Include any necessary headers

                response = req.request("POST", url, headers=headers, data=payload, files=files)
                print(response.text)

                if response.status_code == 200:
                    print(f"Successfully uploaded {field_name}")
                else:
                    print("fail")
                    print(response.text)

            institution.work_flow_table_insert(request, rec_parent_id, status="Draft")

            messages.success(request, message="Successfully registered. Enter the next details.")
            return redirect('nursing_student', rec_parent_id)

    context = {"obj": institution_obj, "course_data": course_data, "company": company, "current_date": current_date}
    return render(request, "proforma/nursing/nursingapplication.html", context)


def nursing_change_course(request, psk_id):
    course_id = request.GET.get('course', None)
    document_id = request.GET.get('document_id', None)

    institution.update_course_id_in_application_dc1(psk_id, course_id, document_id)

    students_fil_objs = institution.student_details_filter_id_base_get(psk_id)

    for student in students_fil_objs:
        student_id = student['psk_id']
        url2 = f"{API_STUDIO_URL}deleteapi/delete/phpm02_application_302_student_dc2/{student_id}"
        response1 = req.request("DELETE", url2)
        if response1.status_code == 200:
            print("student_id")

    messages.info(request, "Please add student details")
    return redirect('nursing_student', psk_id)


def nursing_update(request, psk_id):
    saved_username = request.COOKIES.get('saved_username', None)
    applicant_data = get_applicant_user_data(request, username=saved_username)
    institution_id = applicant_data.get('institution_name')
    institution_obj = institution.institution_id_data_get(int(institution_id))
    course_data = institution.course_data_get("Nursing")
    company = institution.company_master_data_get()[0]
    obj = institution.application_id_data_get(psk_id)

    media_obj = institution.application_media_data_get_V3(psk_id)

    for item in media_obj:
        if 'attachment_content' in item and item['attachment_content']:
            attachment_data = json.loads(item['attachment_content'])  # Convert JSON string to dict
            item['pdf_name'] = attachment_data.get('pdf_name')  # Extract

    # existing_files = {item["file_name"] for item in media_obj}

    check_delete_obj = institution.media_table_get_data(psk_id)

    filed_2 = False
    for item in check_delete_obj:
        if 'permitted_in_phc_upload_uid' == item['file_name']:
            filed_2 = True

    if request.method == "POST":

        institution_psk_id = institution_id
        year_of_establishment = request.POST.get("year_of_establishment")
        # course_type_psk_id = request.POST.get("course_type_psk_id")
        academic_year = request.POST.get("academic_year")
        # document_id = request.POST.get("document_id")
        document_date = request.POST.get("document_date")

        # 1. Copy of G.O in which the institution was permitted to start MBBS., MD., MS., Medical Course
        gov_order_number = request.POST.get("gov_order_number")
        gov_order_date = request.POST.get("gov_order_date")
        gov_order_upload_uid = request.FILES.get("gov_order_upload_uid")

        # 2.Whether the students of the institution were already permitted for the practical training in PHC. If so
        # copies enclosed.
        permitted_in_phc_gov_no = request.POST.get("permitted_in_phc_gov_no")
        permitted_in_phc_gov_date = request.POST.get("permitted_in_phc_gov_date")
        permitted_in_phc_upload_uid = request.FILES.get("permitted_in_phc_upload_uid")

        # 3 . nursing Tamil Nadu Nurses and Midwives Council
        tnnmc_gov_no = request.POST.get("tnnmc_gov_no")
        tnnmc_gov_date = request.POST.get("tnnmc_gov_date")
        affiliation_mgr_university_acc_date = request.POST.get("affiliation_mgr_university_acc_date")
        tnnmc_gov_upload_uid = request.FILES.get("tnnmc_gov_upload_uid")

        # 4. Recognized Colleges in Tamil Nadu Nurses and Midwives Council Web site
        recognized_colleges_list_tn_gov_no = request.POST.get("recognized_colleges_list_tn_gov_no")
        recognized_colleges_list_tn_gov_date = request.POST.get("recognized_colleges_list_tn_gov_date")
        recognized_colleges_list_tn_gov_acc_date = request.POST.get("recognized_colleges_list_tn_gov_acc_date")
        recognized_colleges_list_tn_upload_uid = request.FILES.get("recognized_colleges_list_tn_upload_uid")

        # 5. Recognized Colleges in Indian Nursing Council
        recognized_colleges_list_inc_gov_no = request.POST.get("recognized_colleges_list_inc_gov_no")
        recognized_colleges_list_inc_gov_date = request.POST.get("recognized_colleges_list_inc_gov_date")
        recognized_colleges_list_inc_acc_date = request.POST.get("recognized_colleges_list_inc_acc_date")
        recognized_colleges_list_inc_upload_uid = request.FILES.get("recognized_colleges_list_inc_upload_uid")

        # 6. List of Recognized Colleges in the Indian Nursing Council Web site
        inc_council_website_go_no = request.POST.get("inc_council_website_go_no")
        inc_council_website_go_date = request.POST.get("inc_council_website_go_date")
        inc_council_website_go_acc_date = request.POST.get("inc_council_website_go_acc_date")
        inc_council_website_upload_uid = request.FILES.get("inc_council_website_upload_uid")

        # 7. Provisional affiliation granted by Tamil Nadu MGR Medical University
        affiliation_mgr_university_gov_no = request.POST.get("affiliation_mgr_university_gov_no")
        affiliation_mgr_university_gov_date = request.POST.get("affiliation_mgr_university_gov_date")
        affiliation_mgr_university_gov_acc_date = request.POST.get("affiliation_mgr_university_gov_acc_date")
        affiliation_mgr_university_upload_uid = request.FILES.get("affiliation_mgr_university_upload_uid")

        # 8. Willingness to pay fees for training
        # pay_fees_by_upload_uid = request.FILES.get("pay_fees_by_upload_uid")
        pay_fees_by_upload = "yes"

        # 9. In case, whether the students were already permitted to avail facilities in PHC and more than 3 years
        # for Medical courses whether the institution is willing to remit double the rate of fee structure to each
        # student for continuance of permission.
        double_rate_fees = "yes"

        # 10. Own Hospital Detail (MOU)
        own_hospital_mou_upload_uid = request.FILES.get("own_hospital_mou_upload_uid")

        # 11. Own Hospital Detail (Clinical Establishment Act Certificate)
        own_hospital_clinical_establishment_upload_uid = request.FILES.get(
            "own_hospital_clinical_establishment_upload_uid")

        # 11. Previous Tie-Up with Public Health Department
        # previous_tieup_gov_no = request.POST.get("previous_tieup_gov_no")
        # previous_tieup_gov_date = request.POST.get("previous_tieup_gov_date")
        # pervious_tieup_upload_uid = request.FILES.get("pervious_tieup_upload_uid")

        # 12. No due certificate for internship training fees payment
        no_dues_certificate_upload_uid = request.FILES.get("no_dues_certificate_upload_uid")

        # 13. Consent Letter for 1000 Sq.Ft building
        consent_letter_building_upload_uid = request.FILES.get("consent_letter_building_upload_uid")

        # Required file fields except the two that are optional
        file_fields = [
            "gov_order_upload_uid", "tnnmc_gov_upload_uid",
            "recognized_colleges_list_tn_upload_uid", "recognized_colleges_list_inc_upload_uid",
            "affiliation_mgr_university_upload_uid", "pay_fees_by_upload_uid", "own_hospital_mou_upload_uid",
            "own_hospital_clinical_establishment_upload_uid",
            "no_dues_certificate_upload_uid",
            "consent_letter_building_upload_uid",

        ]

        payload = {
            "data": {
                "institution_psk_id": institution_psk_id,
                "year_of_establishment": year_of_establishment,
                # "course_type_psk_id": course_type_psk_id,
                "accademic_year": academic_year,
                # "document_id": document_id,
                "document_date": document_date,

                # 1. Copy of G.O in which the institution was permitted to start MBBS., MD., MS., Medical Course
                "gov_order_number": gov_order_number,
                "gov_order_date": gov_order_date,

                # 2. Whether the students of the institution were already permitted for the practical training in
                # PHC. If so copies enclosed.
                "permitted_in_phc_gov_no": permitted_in_phc_gov_no,
                # "permitted_in_phc_gov_date": permitted_in_phc_gov_date,

                # 3. Nursing Tamil Nadu Nurses and Midwives Council
                "tnnmc_gov_no": tnnmc_gov_no,
                "tnnmc_gov_date": tnnmc_gov_date,
                "affiliation_mgr_university_acc_date": affiliation_mgr_university_acc_date,

                # 4. Recognized Colleges in Tamil Nadu Nurses and Midwives Council Website
                "recognized_colleges_list_tn_gov_no": recognized_colleges_list_tn_gov_no,
                "recognized_colleges_list_tn_gov_date": recognized_colleges_list_tn_gov_date,
                "recognized_colleges_list_tn_gov_acc_date": recognized_colleges_list_tn_gov_acc_date,

                # 5. Recognized Colleges in Indian Nursing Council
                "recognized_colleges_list_inc_gov_no": recognized_colleges_list_inc_gov_no,
                "recognized_colleges_list_inc_gov_date": recognized_colleges_list_inc_gov_date,
                "recognized_colleges_list_inc_acc_date": recognized_colleges_list_inc_acc_date,

                # 6. List of Recognized Colleges in the Indian Nursing Council Website
                "inc_council_website_go_no": inc_council_website_go_no,
                "inc_council_website_go_acc_date": inc_council_website_go_acc_date,
                # "inc_council_website_go_date": inc_council_website_go_date,

                # 7. Provisional affiliation granted by Tamil Nadu MGR Medical University
                "affiliation_mgr_university_gov_no": affiliation_mgr_university_gov_no,
                "affiliation_mgr_university_gov_date": affiliation_mgr_university_gov_date,
                "affiliation_mgr_university_gov_acc_date": affiliation_mgr_university_gov_acc_date,

                "pay_fees_by_upload_uid": pay_fees_by_upload,
                "pervious_tieup_upload_uid": double_rate_fees,

                "application_status": "Draft",

            }
        }

        if permitted_in_phc_gov_date:
            payload["data"]["permitted_in_phc_gov_date"] = permitted_in_phc_gov_date

        if inc_council_website_go_date:
            payload["data"]["inc_council_website_go_date"] = inc_council_website_go_date
        #
        # if previous_tieup_gov_date:
        #     payload["data"]["previous_tieup_gov_date"] = previous_tieup_gov_date

        parent_id = psk_id
        # Send POST request to API to save application data
        dc1url = f"{API_STUDIO_URL}updateapi/update/{ApplicationTableName}/{parent_id}"

        headers = {'Content-Type': 'application/json'}
        response = req.put(dc1url, headers=headers, data=json.dumps(payload))
        print(response.text)

        if response.status_code == 200:

            file_fields = [
                "gov_order_upload_uid", "permitted_in_phc_upload_uid", "tnnmc_gov_upload_uid",
                "recognized_colleges_list_tn_upload_uid", "recognized_colleges_list_inc_upload_uid",
                "inc_council_website_upload_uid",
                "affiliation_mgr_university_upload_uid", "pay_fees_by_upload_uid", "own_hospital_mou_upload_uid",
                "own_hospital_clinical_establishment_upload_uid", "pervious_tieup_upload_uid",
                "no_dues_certificate_upload_uid",
                "consent_letter_building_upload_uid",

            ]
            media_existing_ids = institution.media_table_get_data(psk_id)

            headers = {}

            for field in file_fields:
                print(field)
                uploaded_file = request.FILES.get(field)

                if uploaded_file:

                    psk_id = get_file_psk_id(field, media_existing_ids)
                    if psk_id:
                        update_url = f"{API_STUDIO_URL}crudapp/upload/media/v3/phpm02_application_301_master_dc1_media/{psk_id}"

                        uploaded_file.seek(0)  # Ensure cursor is at the start
                        file_stream = BytesIO(uploaded_file.read())  # Convert to BytesIO

                        # Open PDF from byte stream
                        pdf_document = fitz.open("pdf", file_stream)
                        pdf_page_count = pdf_document.page_count
                        pdf_document.close()

                        # Get file size in KB
                        uploaded_file.seek(0, os.SEEK_END)
                        pdf_size_kb = uploaded_file.tell() / 1024  # Convert bytes to KB
                        uploaded_file.seek(0)  # Reset cursor

                        # Prepare attachment content
                        attach_content = {
                            "pdf_name": uploaded_file.name,
                            "pdf_page_count": pdf_page_count,
                            "pdf_size": round(pdf_size_kb, 2),
                            "pdf_uploaded": "Yes"
                        }

                        payload = {'api_name': 'phpm02_application_301_master_dc1_media',
                                   'psk_id': str(psk_id),
                                   'attachment_content': json.dumps(attach_content)}

                        files = [('media', (field, uploaded_file, uploaded_file.content_type))]

                        response = requests.put(update_url, headers=headers, data=payload, files=files)
                        print("dfgd", response.text)
                    else:
                        url = f"{API_STUDIO_URL}crudapp/upload/media/v3/{ApplicationTableName}_media"

                        uploaded_file.seek(0)  # Ensure cursor is at the start
                        file_stream = BytesIO(uploaded_file.read())  # Convert to BytesIO

                        # Open PDF from byte stream
                        pdf_document = fitz.open("pdf", file_stream)
                        pdf_page_count = pdf_document.page_count
                        pdf_document.close()

                        # Get file size in KB
                        uploaded_file.seek(0, os.SEEK_END)
                        pdf_size_kb = uploaded_file.tell() / 1024  # Convert bytes to KB
                        uploaded_file.seek(0)  # Reset cursor

                        # Prepare attachment content
                        attach_content = {
                            "pdf_name": uploaded_file.name,
                            "pdf_page_count": pdf_page_count,
                            "pdf_size": round(pdf_size_kb, 2),
                            "pdf_uploaded": "Yes"
                        }

                        payload = {'parent_psk_id': parent_id, 'attachment_content': json.dumps(attach_content)}

                        files = {
                            'media': (field, uploaded_file, 'image/png')
                        }

                        headers = {}  # Include any necessary headers

                        response = req.request("POST", url, headers=headers, data=payload, files=files)
                        print(response.text)

            # messages.success(request, message="Successfully updated or navigated")
            return redirect('nursing_student', parent_id)

        else:

            messages.error(request, response.json().get('detail', response.text))

    context = {"media_obj": media_obj, "PlatformURL": API_STUDIO_URL, "filed_2": filed_2, "obj": obj,
               "rec_parent_id": psk_id, "institution_obj": institution_obj, "company": company,
               "course_data": course_data}
    return render(request, 'proforma/nursing/nursing_update.html', context)


def delete_nursing_student(request, psk_id, rec_parent_id):
    url = f"{API_STUDIO_URL}deleteapi/delete/phpm02_application_302_student_dc2/{psk_id}"
    response = requests.delete(url)

    if response.status_code == 200:
        messages.success(request, message="Deleted Successfully")
        redirect_url = 'nursing_student'
    else:
        error_message = "Delete Api not working, Contact Administrator"
        messages.error(requests, message=error_message)
        redirect_url = 'nursing_student'

    return redirect(redirect_url, rec_parent_id)


def nursing_student(request, rec_parent_id):
    saved_username = request.COOKIES.get('saved_username', None)
    application = institution.application_id_data_get(rec_parent_id)
    # document_id = application['document_id']
    accademic_year = application['accademic_year']
    course_id = application['course_type_psk_id']
    course = institution.course_id_data_get(course_id)
    course_name = course['course_name']
    # course_duration = course['course_duration']

    # start_year, end_year = map(int, accademic_year.split('-'))
    # course_years_list = [f"{start_year + i}-{end_year + i}" for i in range(course_duration)]

    print(accademic_year)

    start_year = int(accademic_year.split('-')[0])

    # Create the list of current and previous academic year
    year_list = [f"{start_year - i}-{start_year - i + 1}" for i in range(2)]

    print(year_list)

    student_data = nursing_student_data_get(request, rec_parent_id, ApplicationStudentTable)
    print(len(student_data))

    if request.method == 'POST':
        if len(student_data) != 0:
            messages.error(request, message="Only one entry is allowed.")
            return redirect('nursing_student', rec_parent_id)

        year_or_semester = request.POST.get('year_or_semester')
        # no_of_students = request.POST.get('no_of_students')
        # training_period = request.POST.get('training_period')
        # no_of_period = request.POST.get('no_of_period')

        intake_per_go = request.POST.get('intake_per_go')
        intake_per_inc = request.POST.get('intake_per_inc')
        intake_per_tnnmc = request.POST.get('intake_per_tnnmc')

        # # validation for student details
        # check_obj = institution.check_dup_student(rec_parent_id, year_or_semester)
        # if check_obj:
        #     messages.info(request, f" Academic year '{year_or_semester}' already exists.")
        #     return redirect('mbbs_student', rec_parent_id)

        payload = {
            "data": {
                "parent_psk_id": rec_parent_id,
                # "document_id": document_id,
                "course_name_pskid": course_id,
                "year_or_semester": year_or_semester,

                # "no_of_students": no_of_students,
                # "training_period": training_period,
                # "no_of_period": no_of_period,

                "intake_per_go": intake_per_go,
                "intake_per_inc": intake_per_inc,
                "intake_per_tnnmc": intake_per_tnnmc,

                "created_by": saved_username,
            }
        }

        # API endpoint URL
        dc1url = f"{API_STUDIO_URL}postapi/create/{ApplicationStudentTable}"
        headers = {'Content-Type': 'application/json'}

        # Sending POST request
        response = req.post(dc1url, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            # Displaying success message and redirecting
            messages.success(request, message='Data Added successfully!')
            return redirect('nursing_student', rec_parent_id=rec_parent_id)

    context = {"student_data": student_data, "rec_parent_id": rec_parent_id,
               "course_name": course_name, "course_years_list": year_list, "application_obj": application}

    return render(request, "proforma/nursing/nursing_student.html", context)


def delete_nursing_phc(request, psk_id, rec_parent_id):
    url2 = f"{API_STUDIO_URL}getapi/phpm02_application_303_phc_dc3/{psk_id}"
    url2_response = requests.get(url2)
    res_data = url2_response.json()
    phc_id = res_data['name_of_phc_pskid']

    check_phc_deatils = institution.phc_id_data_get(phc_id)
    phc_details = check_phc_deatils['phc_deatils']
    status = check_phc_deatils['phc_status']
    details = phc_details if phc_details is not None else None

    url = f"{API_STUDIO_URL}deleteapi/delete/phpm02_application_303_phc_dc3/{psk_id}"
    response = requests.delete(url)

    if response.status_code == 200:
        institution.update_phc_status(phc_id, status, details)
        messages.success(request, message="Deleted Successfully")
        redirect_url = 'nursing_phc_form'
    else:
        error_message = "Delete Api not working, Contact Administrator"
        messages.error(requests, message=error_message)
        redirect_url = 'nursing_phc_form'

    return redirect(redirect_url, rec_parent_id)


def nursing_phc_form(request, rec_parent_id):
    saved_username = request.COOKIES.get('saved_username', None)
    app_phc_data = nursing_student_data_get(request, rec_parent_id, ApplicationPHCTable)
    application = institution.application_id_data_get(rec_parent_id)
    institution_psk_id = application['institution_psk_id']
    institution_obj = institution.institution_id_data_get(institution_psk_id)

    district_data = institution.district_data_get()
    hud_data = institution.hud_data_get()
    block_data = institution.block_data_get()
    phc_data = institution.phc_data_get()

    if request.method == 'POST':
        district_psk_id = request.POST.get('district_psk_id')
        hud_psk_id = request.POST.get('institution_hud_psk_id')
        block_psk_id = request.POST.get('institution_block_psk_id')
        name_of_phc = request.POST.get('name_of_phc_pskid')

        check_phc = institution.phc_id_data_get(name_of_phc)
        existing_phc_details = check_phc.get('phc_deatils')

        if not existing_phc_details:
            phc_details = {"institution_ids": [institution_psk_id]}
        else:
            try:
                existing_phc_details = json.loads(existing_phc_details)
            except json.JSONDecodeError:
                existing_phc_details = {}

            existing_institution_ids = existing_phc_details.get('institution_ids', [])
            if not isinstance(existing_institution_ids, list):
                existing_institution_ids = []

            if institution_psk_id not in existing_institution_ids:
                existing_institution_ids.append(institution_psk_id)

            phc_details = {"institution_ids": existing_institution_ids}

        if check_phc.get('phc_status') != "ALLOCATED":
            check_dub = institution.check_phc_parent_id_to_data(rec_parent_id, name_of_phc)

            if not check_dub:
                response = insert_application_phc(
                    rec_parent_id,
                    district_psk_id,
                    hud_psk_id,
                    block_psk_id,
                    name_of_phc,
                    saved_username,
                    ApplicationPHCTable
                )

                if response.status_code == 200:
                    institution.update_phc_status(name_of_phc, "APPLIED", json.dumps(phc_details, indent=4))
                    messages.success(request, message='Data added successfully!')
                    return redirect('nursing_phc_form', rec_parent_id=rec_parent_id)
            else:
                messages.error(request, message="Duplicate entries are not allowed")
        else:
            messages.info(
                request,
                message=f"PHC '{check_phc.get('phc_name')}' is already allocated. "
                        f"Please use an 'unallocated' or 'applied' PHC"
            )

    context = {
        "app_phc_data": app_phc_data,
        "rec_parent_id": rec_parent_id,
        "phc_data": phc_data,
        "hud_data": hud_data,
        "block_data": block_data,
        "application_obj": application,
        'districts': district_data,
    }

    return render(request, "proforma/nursing/nursing_phc_form.html", context)


def nursing_check_list(request, rec_parent_id):
    saved_username = request.COOKIES.get('saved_username', None)
    applicant_data = get_applicant_user_data(request, username=saved_username)
    applicant_user_id = applicant_data.get('psk_id')

    application = institution.application_id_data_get(rec_parent_id)

    institution_id = applicant_data.get('institution_name')
    institution_obj = institution.institution_id_data_get(int(institution_id))
    institution_hud_psk_id = institution_obj['institution_hud_psk_id']

    all_media_data = institution.media_information_get(rec_parent_id)

    # Create a dictionary for easy lookup: {file_name: parsed_attachment_content}
    media_map = {
        item['file_name']: {
            "attachment_data": json.loads(item['attachment_content']),
            "psk_id": item['psk_id'],
            "raw_attachment_content": item['attachment_content']  # Keep original string
        }
        for item in all_media_data
    }

    check_list_data = {

        "check1": {
            "label": "1. Copy of G.O in which the institution was permitted to start Nursing Medical Course",
            "go_number": application['gov_order_number'],
            "date": application['gov_order_date'],
            "pdf_uploaded": "",
            "pdf_page_count": "",
            "pdf_size": "",
            "pdf_name": ""
        },
        "check2": {
            "label": "2. Whether the students of the institution were already permitted for the practical training in "
                     "PHC. If so copies enclosed.",
            "go_number": application['permitted_in_phc_gov_no'],
            "date": application['permitted_in_phc_gov_date'],
            "pdf_uploaded": "",
            "pdf_page_count": "",
            "pdf_size": "",
            "pdf_name": ""
        },
        "check3": {
            "label": "3. In case of Degree Nursing students, whether Tamil Nadu Nurses and Midwives Council has "
                     "granted recognition to the institution to conduct Degree in Nursing course (Evidence Produced). ",
            "go_number": application['tnnmc_gov_no'],
            "date": application['tnnmc_gov_date'],
            "pdf_uploaded": "",
            "pdf_page_count": "",
            "pdf_size": "",
            "pdf_name": ""
        },
        "check4": {
            "label": "4. Copy of the List of Recognized Colleges in the Tamil Nadu Nurses and Midwives Council Web "
                     "site (Evidence Produced).",
            "go_number": application['recognized_colleges_list_tn_gov_no'],
            "date": application['recognized_colleges_list_tn_gov_date'],
            "pdf_uploaded": "",
            "pdf_page_count": "",
            "pdf_size": "",
            "pdf_name": ""
        },
        "check5": {
            "label": "5. In case of Degree Nursing students, whether Indian Nursing Council has granted recognition "
                     "to the institution to conduct Degree in Nursing course (Evidence Produced)",
            "go_number": application['recognized_colleges_list_inc_gov_no'],
            "date": application['recognized_colleges_list_inc_gov_date'],
            "pdf_uploaded": "",
            "pdf_page_count": "",
            "pdf_size": "",
            "pdf_name": ""
        },
        "check6": {
            "label": "6. Copy of the List of Recognized Colleges in the Indian Nursing Council Web site (Evidence "
                     "Produced).",
            "go_number": application['inc_council_website_go_no'],
            "date": application['inc_council_website_go_date'],
            "pdf_uploaded": "",
            "pdf_page_count": "",
            "pdf_size": "",
            "pdf_name": ""
        },
        "check7": {
            "label": "7. Continuance of provisional affiliation granted by the Tamil Nadu MGR Medical University ("
                     "Evidence Produced).",
            "go_number": application['affiliation_mgr_university_gov_no'],
            "date": application['affiliation_mgr_university_gov_date'],
            "pdf_uploaded": "",
            "pdf_page_count": "",
            "pdf_size": "",
            "pdf_name": ""
        },
        "check8": {
            "label": "8. Whether the Management is willing to pay the fees prescribed by the Government to impart training to their Medical students.",
            "go_number": "NA",
            "date": "NA",
            "pdf_uploaded": "Yes",
            "pdf_page_count": "NA",
            "pdf_size": "NA",
            "pdf_name": "NA"
        },
        "check9": {
            "label": "9. In case, whether the students were already permitted to avail facilities in PHC and more than 3 years for Medical courses whether the institution is willing to remit double the rate of fee structure to each student for continuance of permission. ",
            "go_number": "NA",
            "date": "NA",
            "pdf_uploaded": "Yes",
            "pdf_page_count": "NA",
            "pdf_size": "NA",
            "pdf_name": "NA"
        },

        "check10": {
            "label": "10. Own Hospital Detail (Copy of Memorandum of Understanding [MOU]) ",
            "go_number": "NA",
            "date": "NA",
            "pdf_uploaded": "",
            "pdf_page_count": "",
            "pdf_size": "",
            "pdf_name": ""
        },
        "check11": {
            "label": "11. Own Hospital Detail (Certificate of Registration of Clinical Establishment Act.)",
            "go_number": "NA",
            "date": "NA",
            "pdf_uploaded": "",
            "pdf_page_count": "",
            "pdf_size": "",
            "pdf_name": ""
        },

        "check12": {
            "label": "12. No due certificate of your previous batch of the internship training fees payment (Model "
                     "Enclosed) along with a copy of the challan duly authenticated by the Chairman of the Trust *",
            "go_number": "NA",
            "date": "NA",
            "pdf_uploaded": "",
            "pdf_page_count": "",
            "pdf_size": "",
            "pdf_name": ""
        },
        "check13": {
            "label": "13. Consent Letter for 1000 Sq.Ft building.",
            "go_number": "NA",
            "date": "NA",
            "pdf_uploaded": "",
            "pdf_page_count": "",
            "pdf_size": "",
            "pdf_name": ""
        },
        "check14": {
            "label": "14. List of Students studied currently in your Institutions (1st, 2nd, 3rd, 4th and 5th)",
            "go_number": "NA",
            "date": "NA",
            "pdf_uploaded": "NA",
            "pdf_page_count": "NA",
            "pdf_size": "NA"
        },
        "check15": {
            "label": "15. In case, whether the students were already permitted to avail facilities in PHC and more "
                     "than 3 years for Medical courses whether the institution is willing to remit double the rate of "
                     "fee structure to each student for continuance of permission.",
            "go_number": "NA",
            "date": "NA",
            "pdf_uploaded": "NA",
            "pdf_page_count": "NA",
            "pdf_size": "NA"
        },

    }

    checklist_to_file = {
        "check1": "gov_order_upload_uid",
        "check2": "permitted_in_phc_upload_uid",
        "check3": "tnnmc_gov_upload_uid",
        "check4": "recognized_colleges_list_tn_upload_uid",
        "check5": "recognized_colleges_list_inc_upload_uid",
        "check6": "inc_council_website_upload_uid",
        "check7": "affiliation_mgr_university_upload_uid",

        "check10": "own_hospital_mou_upload_uid",
        "check11": "own_hospital_clinical_establishment_upload_uid",
        "check12": "no_dues_certificate_upload_uid",
        "check13": "consent_letter_building_upload_uid",
    }

    # Merge media info into checklist
    for check_key, file_key in checklist_to_file.items():
        media_entry = media_map.get(file_key)
        if media_entry:
            attachment_data = media_entry['attachment_data']
            check_list_data[check_key].update(attachment_data)
            check_list_data[check_key]['psk_id'] = media_entry['psk_id']
            check_list_data[check_key]['pdf_name'] = attachment_data.get("pdf_name", "")  # ✅ Only assign pdf_name

    student_tbl = institution.student_details_filter_id_base_get(rec_parent_id)
    phc_tbl = institution.phc_parent_id_filter(rec_parent_id)

    check_list_data["check14"]["pdf_uploaded"] = "Yes" if student_tbl else ""
    check_list_data["check15"]["pdf_uploaded"] = "Yes" if phc_tbl else ""

    if request.method == 'POST':

        final_check_result = institution.check_application_final(rec_parent_id)

        if final_check_result.get("final_check") is not True:
            messages.error(request, final_check_result["final_check"])
            return redirect('nursing_check_list', rec_parent_id)

        for key, data in check_list_data.items():
            print(data)
            print(data.get('label'))
            checklist_status = bool(request.POST.get(key))

            payload = {
                "data": {
                    "parent_psk_id": rec_parent_id,
                    "checklist_name": data.get('label'),
                    "checklist_status": checklist_status,
                    "created_by": saved_username,
                }
            }

            # API endpoint URL
            dc1url = f"{API_STUDIO_URL}postapi/create/{ApplicationCheckListTable}"
            headers = {'Content-Type': 'application/json'}

            # Sending POST request
            response = requests.post(dc1url, headers=headers, data=json.dumps(payload))

            if response.status_code == 200:
                print(f"Success: {data.get('label')}")
            else:
                institution.check_list_failure_case(rec_parent_id)
                messages.error(request, message="Server error, please resubmit.")
                return redirect('nursing_check_list', rec_parent_id)

        # institution.work_flow_table_insert(request, rec_parent_id, status="Submitted")
        # institution.application_status_update(rec_parent_id, "Submitted")

        messages.success(request, 'Please proceed with the next payment process.')
        return redirect('nursing_razor_pay', rec_parent_id)

    context = {"rec_parent_id": rec_parent_id, "check_list_data": check_list_data, "application_obj": application}
    return render(request, 'proforma/nursing/nursing_check_list.html', context)


def nursing_razor_pay(request, rec_parent_id):
    saved_username = request.COOKIES.get('saved_username', None)
    applicant_data = get_applicant_user_data(request, username=saved_username)
    applicant_user_id = applicant_data.get('psk_id')

    application = institution.application_id_data_get(rec_parent_id)

    institution_id = applicant_data.get('institution_name')
    institution_obj = institution.institution_id_data_get(int(institution_id))
    institution_hud_psk_id = institution_obj['institution_hud_psk_id']

    all_media_data = institution.media_information_get(rec_parent_id)

    # Create a dictionary for easy lookup: {file_name: parsed_attachment_content}
    media_map = {
        item['file_name']: {
            "attachment_data": json.loads(item['attachment_content']),
            "psk_id": item['psk_id'],
            "raw_attachment_content": item['attachment_content']  # Keep original string
        }
        for item in all_media_data
    }

    check_list_data = {

        "check1": {
            "label": "1. Copy of G.O in which the institution was permitted to start Nursing Medical Course",
            "go_number": application['gov_order_number'],
            "date": application['gov_order_date'],
            "pdf_uploaded": "",
            "pdf_page_count": "",
            "pdf_size": "",
            "pdf_name": ""
        },
        "check2": {
            "label": "2. Whether the students of the institution were already permitted for the practical training in "
                     "PHC. If so copies enclosed.",
            "go_number": application['permitted_in_phc_gov_no'],
            "date": application['permitted_in_phc_gov_date'],
            "pdf_uploaded": "",
            "pdf_page_count": "",
            "pdf_size": "",
            "pdf_name": ""
        },
        "check3": {
            "label": "3. In case of Degree Nursing students, whether Tamil Nadu Nurses and Midwives Council has "
                     "granted recognition to the institution to conduct Degree in Nursing course (Evidence Produced). ",
            "go_number": application['tnnmc_gov_no'],
            "date": application['tnnmc_gov_date'],
            "pdf_uploaded": "",
            "pdf_page_count": "",
            "pdf_size": "",
            "pdf_name": ""
        },
        "check4": {
            "label": "4. Copy of the List of Recognized Colleges in the Tamil Nadu Nurses and Midwives Council Web "
                     "site (Evidence Produced).",
            "go_number": application['recognized_colleges_list_tn_gov_no'],
            "date": application['recognized_colleges_list_tn_gov_date'],
            "pdf_uploaded": "",
            "pdf_page_count": "",
            "pdf_size": "",
            "pdf_name": ""
        },
        "check5": {
            "label": "5. In case of Degree Nursing students, whether Indian Nursing Council has granted recognition "
                     "to the institution to conduct Degree in Nursing course (Evidence Produced)",
            "go_number": application['recognized_colleges_list_inc_gov_no'],
            "date": application['recognized_colleges_list_inc_gov_date'],
            "pdf_uploaded": "",
            "pdf_page_count": "",
            "pdf_size": "",
            "pdf_name": ""
        },
        "check6": {
            "label": "6. Copy of the List of Recognized Colleges in the Indian Nursing Council Web site (Evidence "
                     "Produced).",
            "go_number": application['inc_council_website_go_no'],
            "date": application['inc_council_website_go_date'],
            "pdf_uploaded": "",
            "pdf_page_count": "",
            "pdf_size": "",
            "pdf_name": ""
        },
        "check7": {
            "label": "7. Continuance of provisional affiliation granted by the Tamil Nadu MGR Medical University ("
                     "Evidence Produced).",
            "go_number": application['affiliation_mgr_university_gov_no'],
            "date": application['affiliation_mgr_university_gov_date'],
            "pdf_uploaded": "",
            "pdf_page_count": "",
            "pdf_size": "",
            "pdf_name": ""
        },
        "check8": {
            "label": "8. Whether the Management is willing to pay the fees prescribed by the Government to impart training to their Medical students.",
            "go_number": "NA",
            "date": "NA",
            "pdf_uploaded": "Yes",
            "pdf_page_count": "NA",
            "pdf_size": "NA",
            "pdf_name": "NA"
        },
        "check9": {
            "label": "9. In case, whether the students were already permitted to avail facilities in PHC and more than 3 years for Medical courses whether the institution is willing to remit double the rate of fee structure to each student for continuance of permission. ",
            "go_number": "NA",
            "date": "NA",
            "pdf_uploaded": "Yes",
            "pdf_page_count": "NA",
            "pdf_size": "NA",
            "pdf_name": "NA"
        },

        "check10": {
            "label": "10. Own Hospital Detail (Copy of Memorandum of Understanding [MOU]) ",
            "go_number": "NA",
            "date": "NA",
            "pdf_uploaded": "",
            "pdf_page_count": "",
            "pdf_size": "",
            "pdf_name": ""
        },
        "check11": {
            "label": "11. Own Hospital Detail (Certificate of Registration of Clinical Establishment Act.)",
            "go_number": "NA",
            "date": "NA",
            "pdf_uploaded": "",
            "pdf_page_count": "",
            "pdf_size": "",
            "pdf_name": ""
        },

        "check12": {
            "label": "12. No due certificate of your previous batch of the internship training fees payment (Model "
                     "Enclosed) along with a copy of the challan duly authenticated by the Chairman of the Trust *",
            "go_number": "NA",
            "date": "NA",
            "pdf_uploaded": "",
            "pdf_page_count": "",
            "pdf_size": "",
            "pdf_name": ""
        },
        "check13": {
            "label": "13. Consent Letter for 1000 Sq.Ft building.",
            "go_number": "NA",
            "date": "NA",
            "pdf_uploaded": "",
            "pdf_page_count": "",
            "pdf_size": "",
            "pdf_name": ""
        },
        "check14": {
            "label": "14. List of Students studied currently in your Institutions (1st, 2nd, 3rd, 4th and 5th)",
            "go_number": "NA",
            "date": "NA",
            "pdf_uploaded": "NA",
            "pdf_page_count": "NA",
            "pdf_size": "NA"
        },
        "check15": {
            "label": "15. In case, whether the students were already permitted to avail facilities in PHC and more "
                     "than 3 years for Medical courses whether the institution is willing to remit double the rate of "
                     "fee structure to each student for continuance of permission.",
            "go_number": "NA",
            "date": "NA",
            "pdf_uploaded": "NA",
            "pdf_page_count": "NA",
            "pdf_size": "NA"
        },

    }

    checklist_to_file = {
        "check1": "gov_order_upload_uid",
        "check2": "permitted_in_phc_upload_uid",
        "check3": "tnnmc_gov_upload_uid",
        "check4": "recognized_colleges_list_tn_upload_uid",
        "check5": "recognized_colleges_list_inc_upload_uid",
        "check6": "inc_council_website_upload_uid",
        "check7": "affiliation_mgr_university_upload_uid",

        "check10": "own_hospital_mou_upload_uid",
        "check11": "own_hospital_clinical_establishment_upload_uid",
        "check12": "no_dues_certificate_upload_uid",
        "check13": "consent_letter_building_upload_uid",
    }

    # Merge media info into checklist
    for check_key, file_key in checklist_to_file.items():
        media_entry = media_map.get(file_key)
        if media_entry:
            attachment_data = media_entry['attachment_data']
            check_list_data[check_key].update(attachment_data)
            check_list_data[check_key]['psk_id'] = media_entry['psk_id']
            check_list_data[check_key]['pdf_name'] = attachment_data.get("pdf_name", "")  # ✅ Only assign pdf_name

    student_tbl = institution.student_details_filter_id_base_get(rec_parent_id)
    phc_tbl = institution.phc_parent_id_filter(rec_parent_id)

    check_list_data["check14"]["pdf_uploaded"] = "Yes" if student_tbl else ""
    check_list_data["check15"]["pdf_uploaded"] = "Yes" if phc_tbl else ""

    context = {"rec_parent_id": rec_parent_id, "check_list_data": check_list_data, "application_obj": application}
    return render(request, 'proforma/nursing/nursing_check_razor.html', context)
