from datetime import datetime

import requests
from django.contrib import messages
from django.shortcuts import render, redirect
import requests as req
from user_management.views import API_STUDIO_URL
from vas1 import institution
from vas1.applicant_user_master import get_applicant_user_data
import json

from vas1.mbbs_proforma import nursing_student_data_get, ApplicationStudentTable, ApplicationTableName, \
    ApplicationPHCTable, get_file_psk_id, ApplicationCheckListTable, insert_application_phc
import fitz
import os
from io import BytesIO


def dgmn_application_navigation(request):
    saved_username = request.COOKIES.get('saved_username', None)
    applicant_data = get_applicant_user_data(request, username=saved_username)
    institution_id = applicant_data.get('institution_name')
    check_app = institution.check_application(institution_id)

    for check in check_app:
        course_master_obj = institution.course_id_data_get(check.get('course_type_psk_id'))
        # Ensure course_master_obj is not None and has 'course_type'
        if course_master_obj and course_master_obj.get('course_type') == "DGMN":
            return redirect('dgmn_update', check['psk_id'])

    # If no application matches the condition, redirect to 'anm_application'
    return redirect('dgmn_application')


def dgmn_application(request):
    saved_username = request.COOKIES.get('saved_username', None)
    applicant_data = get_applicant_user_data(request, username=saved_username)
    institution_id = applicant_data.get('institution_name')
    # psk_id = applicant_data.get('psk_id')

    institution_obj = institution.institution_id_data_get(int(institution_id))
    course_data = institution.course_data_get(_type="DGMN")
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
        tnnmc_gov_upload_uid = request.FILES.get("tnnmc_gov_upload_uid")
        affiliation_mgr_university_acc_date = request.POST.get("affiliation_mgr_university_acc_date")

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

        # 7. Willingness to pay fees for training
        pay_fees_by_upload_uid = request.FILES.get("pay_fees_by_upload_uid")

        # 8. Own Hospital Detail (MOU)
        own_hospital_mou_upload_uid = request.FILES.get("own_hospital_mou_upload_uid")

        # 9. Own Hospital Detail (Clinical Establishment Act Registration)
        own_hospital_clinical_establishment_upload_uid = request.FILES.get(
            "own_hospital_clinical_establishment_upload_uid")

        # 10. Previous Tie-Up with Public Health Department
        previous_tieup_gov_no = request.POST.get("previous_tieup_gov_no")
        previous_tieup_gov_date = request.POST.get("previous_tieup_gov_date")
        pervious_tieup_upload_uid = request.FILES.get("pervious_tieup_upload_uid")

        # 11. No due certificate for previous batch internship fees
        no_dues_certificate_upload_uid = request.FILES.get("no_dues_certificate_upload_uid")

        # 12. Consent Letter for 1000 Sq.Ft building
        consent_letter_building_upload_uid = request.FILES.get("consent_letter_building_upload_uid")

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

                # 4. Recognized Colleges in Tamil Nadu Nurses and Midwives Council Website
                "recognized_colleges_list_tn_gov_no": recognized_colleges_list_tn_gov_no,
                "recognized_colleges_list_tn_gov_date": recognized_colleges_list_tn_gov_date,

                # 5. Recognized Colleges in Indian Nursing Council
                "recognized_colleges_list_inc_gov_no": recognized_colleges_list_inc_gov_no,
                "recognized_colleges_list_inc_gov_date": recognized_colleges_list_inc_gov_date,

                # 6. List of Recognized Colleges in the Indian Nursing Council Website
                "inc_council_website_go_no": inc_council_website_go_no,
                # "inc_council_website_go_date": inc_council_website_go_date,

                # 10. Previous Tie-Up with Public Health Department
                "previous_tieup_gov_no": previous_tieup_gov_no,

                "affiliation_mgr_university_acc_date": affiliation_mgr_university_acc_date,
                "recognized_colleges_list_tn_gov_acc_date": recognized_colleges_list_tn_gov_acc_date,
                "recognized_colleges_list_inc_acc_date": recognized_colleges_list_inc_acc_date,
                "inc_council_website_go_acc_date": inc_council_website_go_acc_date,

                "application_status": "Draft",
                "created_by": saved_username,

            }
        }

        if permitted_in_phc_gov_date:
            payload["data"]["permitted_in_phc_gov_date"] = permitted_in_phc_gov_date

        if inc_council_website_go_date:
            payload["data"]["inc_council_website_go_date"] = inc_council_website_go_date

        # if previous_tieup_gov_date:
        #     payload["data"]["previous_tieup_gov_date"] = previous_tieup_gov_date

        # Send POST request to API to save application data
        dc1url = f"{API_STUDIO_URL}postapi/create/{ApplicationTableName}"

        headers = {'Content-Type': 'application/json'}
        response = req.post(dc1url, headers=headers, data=json.dumps(payload))

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
                # ('pay_fees_by_upload_uid', pay_fees_by_upload_uid),
                ('own_hospital_mou_upload_uid', own_hospital_mou_upload_uid),
                ('own_hospital_clinical_establishment_upload_uid', own_hospital_clinical_establishment_upload_uid),
                # ('pervious_tieup_upload_uid', pervious_tieup_upload_uid),
                ('no_dues_certificate_upload_uid', no_dues_certificate_upload_uid),
                ('consent_letter_building_upload_uid', consent_letter_building_upload_uid),

            ]

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
            return redirect('dgmn_student', rec_parent_id)

    context = {"obj": institution_obj, "course_data": course_data, "company": company, "current_date": current_date}
    return render(request, "proforma/dgmn/dgmn_application.html", context)


def dgmn_change_course(request, psk_id):
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
    return redirect('dgmn_student', psk_id)


def dgmn_update(request, psk_id):
    saved_username = request.COOKIES.get('saved_username', None)
    applicant_data = get_applicant_user_data(request, username=saved_username)
    institution_id = applicant_data.get('institution_name')
    institution_obj = institution.institution_id_data_get(int(institution_id))
    course_data = institution.course_data_get("DGMN")
    company = institution.company_master_data_get()[0]
    obj = institution.application_id_data_get(psk_id)

    media_obj = institution.application_media_data_get(psk_id)
    existing_files = {item["file_name"] for item in media_obj}

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
        tnnmc_gov_upload_uid = request.FILES.get("tnnmc_gov_upload_uid")

        # 4. Recognized Colleges in Tamil Nadu Nurses and Midwives Council Web site
        recognized_colleges_list_tn_gov_no = request.POST.get("recognized_colleges_list_tn_gov_no")
        recognized_colleges_list_tn_gov_date = request.POST.get("recognized_colleges_list_tn_gov_date")
        recognized_colleges_list_tn_upload_uid = request.FILES.get("recognized_colleges_list_tn_upload_uid")

        # 5. Recognized Colleges in Indian Nursing Council
        recognized_colleges_list_inc_gov_no = request.POST.get("recognized_colleges_list_inc_gov_no")
        recognized_colleges_list_inc_gov_date = request.POST.get("recognized_colleges_list_inc_gov_date")
        recognized_colleges_list_inc_upload_uid = request.FILES.get("recognized_colleges_list_inc_upload_uid")

        # 6. List of Recognized Colleges in the Indian Nursing Council Web site
        inc_council_website_go_no = request.POST.get("inc_council_website_go_no")
        inc_council_website_go_date = request.POST.get("inc_council_website_go_date")
        inc_council_website_upload_uid = request.FILES.get("inc_council_website_upload_uid")

        # 7. Willingness to pay fees for training
        pay_fees_by_upload_uid = request.FILES.get("pay_fees_by_upload_uid")

        # 8. Own Hospital Detail (MOU)
        own_hospital_mou_upload_uid = request.FILES.get("own_hospital_mou_upload_uid")

        # 9. Own Hospital Detail (Clinical Establishment Act Registration)
        own_hospital_clinical_establishment_upload_uid = request.FILES.get(
            "own_hospital_clinical_establishment_upload_uid")

        # 10. Previous Tie-Up with Public Health Department
        previous_tieup_gov_no = request.POST.get("previous_tieup_gov_no")
        previous_tieup_gov_date = request.POST.get("previous_tieup_gov_date")
        pervious_tieup_upload_uid = request.FILES.get("pervious_tieup_upload_uid")

        # 11. No due certificate for previous batch internship fees
        no_dues_certificate_upload_uid = request.FILES.get("no_dues_certificate_upload_uid")

        # 12. Consent Letter for 1000 Sq.Ft building
        consent_letter_building_upload_uid = request.FILES.get("consent_letter_building_upload_uid")

        required_files = [
            "gov_order_upload_uid", "tnnmc_gov_upload_uid",
            "recognized_colleges_list_tn_upload_uid", "recognized_colleges_list_inc_upload_uid",
            "pay_fees_by_upload_uid", "own_hospital_mou_upload_uid",
            "own_hospital_clinical_establishment_upload_uid",
            "no_dues_certificate_upload_uid",

        ]

        # Optional files
        optional_files = [
            "permitted_in_phc_upload_uid",
            "pervious_tieup_upload_uid",
            "inc_council_website_upload_uid",
            "consent_letter_building_upload_uid",

        ]

        missing_files = []

        for file_field in required_files:
            if file_field not in request.FILES and file_field not in existing_files:
                missing_files.append(file_field)

        if missing_files:
            messages.error(request, f"The following files are required but missing: {', '.join(missing_files)}")
            return redirect('dgmn_update', psk_id)

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

                # 4. Recognized Colleges in Tamil Nadu Nurses and Midwives Council Website
                "recognized_colleges_list_tn_gov_no": recognized_colleges_list_tn_gov_no,
                "recognized_colleges_list_tn_gov_date": recognized_colleges_list_tn_gov_date,

                # 5. Recognized Colleges in Indian Nursing Council
                "recognized_colleges_list_inc_gov_no": recognized_colleges_list_inc_gov_no,
                "recognized_colleges_list_inc_gov_date": recognized_colleges_list_inc_gov_date,

                # 6. List of Recognized Colleges in the Indian Nursing Council Website
                "inc_council_website_go_no": inc_council_website_go_no,
                # "inc_council_website_go_date": inc_council_website_go_date,

                # 10. Previous Tie-Up with Public Health Department
                "previous_tieup_gov_no": previous_tieup_gov_no,

                "application_status": "Draft",

            }
        }

        if permitted_in_phc_gov_date:
            payload["data"]["permitted_in_phc_gov_date"] = permitted_in_phc_gov_date

        if inc_council_website_go_date:
            payload["data"]["inc_council_website_go_date"] = inc_council_website_go_date

        if previous_tieup_gov_date:
            payload["data"]["previous_tieup_gov_date"] = previous_tieup_gov_date

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
                "pay_fees_by_upload_uid", "own_hospital_mou_upload_uid",
                "own_hospital_clinical_establishment_upload_uid", "pervious_tieup_upload_uid",
                "no_dues_certificate_upload_uid",
                "consent_letter_building_upload_uid",

            ]

            media_existing_ids = institution.media_table_get_data(psk_id)

            headers = {}

            MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB in bytes

            for field in file_fields:
                uploaded_file = request.FILES.get(field)

                if uploaded_file:
                    # Check if the uploaded file is a PDF and exceeds 2MB
                    if uploaded_file.content_type == "application/pdf" and uploaded_file.size > MAX_FILE_SIZE:
                        messages.info(request, "Oops! Your file is too large (max 2MB). Please choose a smaller PDF "
                                               "and try again.")
                        return redirect('dgmn_update', psk_id)  # Skip processing this file

                    psk_id = get_file_psk_id(field, media_existing_ids)
                    if psk_id:
                        update_url = f"{API_STUDIO_URL}crudapp/upload/media/phpm02_application_301_master_dc1_media/{psk_id}"
                        payload = {'api_name': 'phpm02_application_301_master_dc1_media',
                                   'psk_id': str(psk_id),
                                   'parent_psk_id': str(parent_id)}

                        files = [('media', (field, uploaded_file, uploaded_file.content_type))]

                        response = requests.put(update_url, headers=headers, data=payload, files=files)
                        print(response.text)
                    else:
                        url = f"{API_STUDIO_URL}crudapp/upload/media/{ApplicationTableName}_media"
                        payload = {'parent_psk_id': parent_id}

                        files = {
                            'media': (field, uploaded_file, 'image/png')
                        }

                        headers = {}  # Include any necessary headers

                        response = req.request("POST", url, headers=headers, data=payload, files=files)
                        print("Creating new media entry for", response.text)

            # messages.success(request, message="Successfully updated or navigated")
            return redirect('dgmn_student', parent_id)

        else:

            messages.error(request, response.json().get('detail', response.text))

    context = {"obj": obj, "rec_parent_id": psk_id, "institution_obj": institution_obj, "company": company,
               "course_data": course_data, "media_obj": media_obj, "PlatformURL": API_STUDIO_URL}
    return render(request, 'proforma/dgmn/dgmn_update.html', context)


def delete_dgmn_student(request, psk_id, rec_parent_id):
    url = f"{API_STUDIO_URL}deleteapi/delete/phpm02_application_302_student_dc2/{psk_id}"
    response = requests.delete(url)

    if response.status_code == 200:
        messages.success(request, message="Deleted Successfully")
        redirect_url = 'dgmn_student'
    else:
        error_message = "Delete Api not working, Contact Administrator"
        messages.error(requests, message=error_message)
        redirect_url = 'dgmn_student'

    return redirect(redirect_url, rec_parent_id)


def dgmn_student(request, rec_parent_id):
    saved_username = request.COOKIES.get('saved_username', None)
    application = institution.application_id_data_get(rec_parent_id)
    # document_id = application['document_id']
    accademic_year = application['accademic_year']
    course_id = application['course_type_psk_id']
    course = institution.course_id_data_get(course_id)
    course_name = course['course_name']
    course_duration = course['course_duration']

    start_year, end_year = map(int, accademic_year.split('-'))
    course_years_list = [f"{start_year + i}-{end_year + i}" for i in range(course_duration)]

    student_data = nursing_student_data_get(request, rec_parent_id, ApplicationStudentTable)

    if request.method == 'POST':
        year_or_semester = request.POST.get('year_or_semester')
        no_of_students = request.POST.get('no_of_students')
        training_period = request.POST.get('training_period')
        no_of_period = request.POST.get('no_of_period')

        # validation for student details
        check_obj = institution.check_dup_student(rec_parent_id, year_or_semester)
        if check_obj:
            messages.info(request, f" Academic year '{year_or_semester}' already exists.")
            return redirect('dgmn_student', rec_parent_id)

        payload = {
            "data": {
                "parent_psk_id": rec_parent_id,
                # "document_id": document_id,
                "course_name_pskid": course_id,
                "year_or_semester": year_or_semester,
                "no_of_students": no_of_students,
                "training_period": training_period,
                "no_of_period": no_of_period,
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
            return redirect('dgmn_student', rec_parent_id=rec_parent_id)

    context = {"student_data": student_data, "rec_parent_id": rec_parent_id,
               "course_name": course_name, "course_years_list": course_years_list, "application_obj": application}

    return render(request, "proforma/dgmn/dgmn_student.html", context)


def delete_dgmn_phc(request, psk_id, rec_parent_id):
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
        redirect_url = 'dgmn_phc_form'
    else:
        error_message = "Delete Api not working, Contact Administrator"
        messages.error(requests, message=error_message)
        redirect_url = 'dgmn_phc_form'

    return redirect(redirect_url, rec_parent_id)


def dgmn_phc_form(request, rec_parent_id):
    saved_username = request.COOKIES.get('saved_username', None)
    app_phc_data = nursing_student_data_get(request, rec_parent_id, ApplicationPHCTable)
    application = institution.application_id_data_get(rec_parent_id)
    institution_psk_id = application['institution_psk_id']
    institution_obj = institution.institution_id_data_get(institution_psk_id)
    block_id = institution_obj['institution_block_psk_id']
    phc_data = institution.block_against_phc_allocated_load(block_id)

    if request.method == 'POST':
        name_of_phc = request.POST.get('name_of_phc_pskid')
        check_phc = institution.phc_id_data_get(name_of_phc)
        phc_details = {"institution_ids": [institution_psk_id]}

        if check_phc['phc_status'] == "UN-ALLOCATED":
            response = insert_application_phc(rec_parent_id, name_of_phc, saved_username, ApplicationPHCTable)

            if response.status_code == 200:
                institution.update_phc_status(name_of_phc, "ALLOCATED", json.dumps(phc_details, indent=4))
                messages.success(request, message='Data Added successfully!')
                return redirect('dgmn_phc_form', rec_parent_id=rec_parent_id)

        elif check_phc['phc_status'] == "ALLOCATED":
            check_dub = institution.check_phc_parent_id_to_data(rec_parent_id, name_of_phc)

            if not check_dub:
                response = insert_application_phc(rec_parent_id, name_of_phc, saved_username, ApplicationPHCTable)

                if response.status_code == 200:
                    institution.update_phc_status(name_of_phc, "ALLOCATED", json.dumps(phc_details, indent=4))
                    messages.success(request, message='Data Added successfully!')
                    return redirect('dgmn_phc_form', rec_parent_id=rec_parent_id)
            else:
                messages.info(request, message="Duplicate entries are not allowed.")
        else:
            messages.info(request,
                          message=f"PHC '{check_phc['phc_name']}' is already allocated. Please use an unallocated PHC")

    context = {"app_phc_data": app_phc_data, "rec_parent_id": rec_parent_id, "phc_data": phc_data,
               "application_obj": application}

    return render(request, "proforma/dgmn/dgmn_phc_form.html", context)


def dgmn_check_list(request, rec_parent_id):
    saved_username = request.COOKIES.get('saved_username', None)
    applicant_data = get_applicant_user_data(request, username=saved_username)
    applicant_user_id = applicant_data.get('psk_id')

    application = institution.application_id_data_get(rec_parent_id)

    institution_id = applicant_data.get('institution_name')
    institution_obj = institution.institution_id_data_get(int(institution_id))
    institution_hud_psk_id = institution_obj['institution_hud_psk_id']

    check1 = institution.check_list_make_data(rec_parent_id, 'gov_order_upload_uid')
    check2 = institution.check_list_make_data(rec_parent_id, 'permitted_in_phc_upload_uid')
    check3 = institution.check_list_make_data(rec_parent_id, 'tnnmc_gov_upload_uid')
    check4 = institution.check_list_make_data(rec_parent_id, 'recognized_colleges_list_tn_upload_uid')

    check5 = institution.check_list_make_data(rec_parent_id, 'recognized_colleges_list_inc_upload_uid')
    check6 = institution.check_list_make_data(rec_parent_id, 'inc_council_website_upload_uid')
    # check7 = institution.check_list_make_data(rec_parent_id, 'affiliation_mgr_university_upload_uid')
    check8 = institution.check_list_make_data(rec_parent_id, 'pay_fees_by_upload_uid')
    check9 = institution.check_list_make_data(rec_parent_id, 'own_hospital_mou_upload_uid')
    check10 = institution.check_list_make_data(rec_parent_id, 'own_hospital_clinical_establishment_upload_uid')
    check11 = institution.check_list_make_data(rec_parent_id, 'pervious_tieup_upload_uid')
    check12 = institution.check_list_make_data(rec_parent_id, 'no_dues_certificate_upload_uid')
    check13 = institution.check_list_make_data(rec_parent_id, 'consent_letter_building_upload_uid')

    check_list_data = {

        "check1": {
            "label": "1.Copy of G.O in which the institution was permitted to start Para Medical Course",
            "go_number": application['gov_order_number'],
            "date": application['gov_order_date'],
            "pdf_uploaded": check1['pdf_uploaded'],
            "pdf_page_count": check1['pdf_page_count'],
            "pdf_size": check1['pdf_size']
        },
        "check2": {
            "label": "2. Whether the students of the institution were already permitted for the practical training in "
                     "PHC. If so copies enclosed.",
            "go_number": application['permitted_in_phc_gov_no'],
            "date": application['permitted_in_phc_gov_date'],
            "pdf_uploaded": check2['pdf_uploaded'],
            "pdf_page_count": check2['pdf_page_count'],
            "pdf_size": check2['pdf_size']
        },
        "check3": {
            "label": "3. In case of Degree DGNM students, whether Tamil Nadu Nurses and Midwives Council has "
                     "granted recognition to the institution to conduct Degree in DGNM course (Evidence Produced). ",
            "go_number": application['tnnmc_gov_no'],
            "date": application['tnnmc_gov_date'],
            "pdf_uploaded": check3['pdf_uploaded'],
            "pdf_page_count": check3['pdf_page_count'],
            "pdf_size": check3['pdf_size']
        },
        "check4": {
            "label": "4. Copy of the List of Recognized Colleges in the Tamil Nadu Nurses and Midwives Council Web "
                     "site (Evidence Produced).",
            "go_number": application['recognized_colleges_list_tn_gov_no'],
            "date": application['recognized_colleges_list_tn_gov_date'],
            "pdf_uploaded": check4['pdf_uploaded'],
            "pdf_page_count": check4['pdf_page_count'],
            "pdf_size": check4['pdf_size']
        },
        "check5": {
            "label": "5. In case of Degree DGNM students, whether Indian DGNM Council has granted recognition "
                     "to the institution to conduct Degree in DGNM course (Evidence Produced)",
            "go_number": application['recognized_colleges_list_inc_gov_no'],
            "date": application['recognized_colleges_list_inc_gov_date'],
            "pdf_uploaded": check5['pdf_uploaded'],
            "pdf_page_count": check5['pdf_page_count'],
            "pdf_size": check5['pdf_size']
        },
        "check6": {
            "label": "6. Copy of the List of Recognized Colleges in the Indian DGNM Council Web site (Evidence "
                     "Produced).",
            "go_number": application['inc_council_website_go_no'],
            "date": application['inc_council_website_go_date'],
            "pdf_uploaded": check6['pdf_uploaded'],
            "pdf_page_count": check6['pdf_page_count'],
            "pdf_size": check6['pdf_size']
        },

        "check8": {
            "label": "7. Whether the Management is willing to pay the fees prescribed by the Government to impart "
                     "training to their Medical students.",
            "go_number": "NA",
            "date": "NA",
            "pdf_uploaded": check8['pdf_uploaded'],
            "pdf_page_count": check8['pdf_page_count'],
            "pdf_size": check8['pdf_size']
        },
        "check9": {
            "label": "8. Own Hospital Detail (Copy of Memorandum of Understanding [MOU]) ",
            "go_number": "NA",
            "date": "NA",
            "pdf_uploaded": check9['pdf_uploaded'],
            "pdf_page_count": check9['pdf_page_count'],
            "pdf_size": check9['pdf_size']
        },
        "check10": {
            "label": "9. Own Hospital Detail (Certificate of Registration of Clinical Establishment Act.)",
            "go_number": "NA",
            "date": "NA",
            "pdf_uploaded": check10['pdf_uploaded'],
            "pdf_page_count": check10['pdf_page_count'],
            "pdf_size": check10['pdf_size']
        },
        "check11": {
            "label": "10. Previous Tie-Up with Public Health Department G.O and G.O date",
            "go_number": application['previous_tieup_gov_no'],
            "date": application['previous_tieup_gov_date'],
            "pdf_uploaded": check11['pdf_uploaded'],
            "pdf_page_count": check11['pdf_page_count'],
            "pdf_size": check11['pdf_size']
        },
        "check12": {
            "label": "11. No due certificate of your previous batch of the internship training fees payment (Model "
                     "Enclosed) along with a copy of the challan duly authenticated by the Chairman of the Trust *",
            "go_number": "NA",
            "date": "NA",
            "pdf_uploaded": check12['pdf_uploaded'],
            "pdf_page_count": check12['pdf_page_count'],
            "pdf_size": check12['pdf_size']
        },
        "check13": {
            "label": "12. Consent Letter for 1000 Sq.Ft building.",
            "go_number": "NA",
            "date": "NA",
            "pdf_uploaded": check13['pdf_uploaded'],
            "pdf_page_count": check13['pdf_page_count'],
            "pdf_size": check13['pdf_size']
        },
        "check14": {
            "label": "13. List of Students studied currently in your Institutions (1st, 2nd, 3rd, 4th and 5th)",
            "go_number": "NA",
            "date": "NA",
            "pdf_uploaded": "NA",
            "pdf_page_count": "NA",
            "pdf_size": "NA"
        },
        "check15": {
            "label": "14. In case, whether the students were already permitted to avail facilities in PHC and more "
                     "than 3 years for Medical courses whether the institution is willing to remit double the rate of "
                     "fee structure to each student for continuance of permission.",
            "go_number": "NA",
            "date": "NA",
            "pdf_uploaded": "NA",
            "pdf_page_count": "NA",
            "pdf_size": "NA"
        },

    }

    if request.method == 'POST':

        # Call check_application_final before processing the form
        final_check_result = institution.check_application_final(rec_parent_id)

        if final_check_result.get("final_check") is not True:
            messages.error(request, final_check_result["final_check"])
            return redirect('dgmn_check_list', rec_parent_id)

        for key, data in check_list_data.items():
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
            print(response.text)

            if response.status_code == 200:
                print(f"Success: {data.get('label')}")
            else:
                institution.check_list_failure_case(rec_parent_id)
                messages.error(request, message="Server error, please resubmit.")
                return redirect('nursing_check_list', rec_parent_id)

        institution.work_flow_table_insert(request, rec_parent_id, status="Submitted")
        institution.application_status_update(rec_parent_id, "Submitted")

        messages.success(request, 'Successfully Submitted Application')
        return redirect('downloadapplication')

    context = {"rec_parent_id": rec_parent_id, "check_list_data": check_list_data, "application_obj": application}
    return render(request, 'proforma/dgmn/dgmn_check_list.html', context)
