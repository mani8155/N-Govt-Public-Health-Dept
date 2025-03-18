from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import HttpResponse
import requests, json
from django.contrib import messages
import random
import string
import datetime

from user_management.settings_views import user_bundle_settings

API_STUDIO_URL = user_bundle_settings()


# Create your views here.

def user_menu(request):
    return render(request, 'phd_tieup_admin.html')


def phpm_create(request):
    if request.method == 'POST':
        company_academic_year = request.POST['company_academic_year']
        active = request.POST.get('active', 'off') == 'on'
        company_distirict = request.POST['company_distirict']
        company_address = request.POST['company_address']
        company_code = request.POST['company_code']
        company_logo = request.FILES.get('file')
        print("FILE:", company_logo)
        company_name = request.POST['company_name']
        company_gstin = request.POST['company_gstin']
        company_pincode = request.POST['company_pincode']

        url = f"{API_STUDIO_URL}postapi/create/phpm02_company_50"

        payload = json.dumps({
            "data": {
                "company_academic_year": company_academic_year,
                "active": active,
                "company_distirict": company_distirict,
                "company_address": company_address,
                "company_code": company_code,
                "company_name": company_name,
                "company_gstin": company_gstin,
                "company_pincode": company_pincode,
            }
        })

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            res_data = response.json()
            psk_id = res_data.get('psk_id')
            print("PSK_ID:", psk_id)
            # print("Res_Data:", res_data)

            url = f"{API_STUDIO_URL}crudapp/upload/media/phpm02_company_50_media"

            payload = {'parent_psk_id': psk_id}
            files = [
                ('media', (company_logo.name, company_logo, company_logo.content_type))
            ]
            headers = {
                'api_name': 'phpm02_company_50_media'
            }

            response = requests.request("POST", url, headers=headers, data=payload, files=files)

            if response.status_code == 200:
                messages.success(request, "Company details created successfully")
                return redirect('phpm_company_list')
            else:
                HttpResponse("Failed to upload logo")
        else:
            return HttpResponse("Failure: " + response.text)

    return render(request, 'Company/create_company.html')


def phpm_company_list(request):
    url = f"{API_STUDIO_URL}getapi/phpm02_company_50/all"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code == 200:
        response_data = response.json()
    else:
        return HttpResponse("API call is not working")

    # print(response.text)

    context = {
        'response_data': response_data
    }

    return render(request, 'Company/company_list.html', context)


def phpm_update_company(request, psk_id):
    # Get company data from API
    url = f"{API_STUDIO_URL}getapi/all_fields/phpm02_company_50/{psk_id}"

    active = request.POST.get('active') == 'on'

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    res_data = response.json()

    if response.status_code == 200:

        if request.method == 'POST':
            # Extract form data
            company_academic_year = request.POST['company_academic_year']
            company_distirict = request.POST['company_distirict']
            company_address = request.POST['company_address']
            company_code = request.POST['company_code']
            company_logo = request.FILES.get('file')  # Assuming the file input field is 'file'
            print("FILE:", company_logo)
            company_name = request.POST['company_name']
            company_gstin = request.POST['company_gstin']
            company_pincode = request.POST['company_pincode']

            # Prepare data for update request
            update_url = f"{API_STUDIO_URL}updateapi/update/phpm02_company_50/{psk_id}"

            payload = json.dumps({
                "data": {
                    "company_academic_year": company_academic_year,
                    "active": active,
                    "company_distirict": company_distirict,
                    "company_address": company_address,
                    "company_code": company_code,
                    "company_name": company_name,
                    "company_gstin": company_gstin,
                    "company_pincode": company_pincode,
                }
            })

            headers = {
                'Content-Type': 'application/json'
            }

            # Make PUT request to update the company data
            response = requests.put(update_url, headers=headers, data=payload)

            if response.status_code == 200:
                res_data = response.json()
                # print(f"Updated Company Response: {res_data}")
                # print(f"res_data type: {type(res_data)}")
                # print(f"res_data: {res_data}")

                # Fetch media details for the company
                url = f"{API_STUDIO_URL}crudapp/get/media/all/phpm02_company_50_media"
                response = requests.request("GET", url, headers=headers, data=payload)

                if response.status_code == 200:
                    response_data = response.json()
                    # print(f"Response Data for Media: {response_data}")

                    # Check if response is a list and extract the correct media psk_id
                    if isinstance(response_data, list) and len(response_data) > 0:
                        media_psk_id = response_data[0].get("psk_id")  # Assuming we want the first media item
                        # print("Media psk_id:", media_psk_id)
                    else:
                        print("No media found")

                    # Upload new media (company logo) associated with the company
                    url = f"{API_STUDIO_URL}crudapp/upload/media/phpm02_company_50_media/{media_psk_id}"
                    payload = {'parent_psk_id': psk_id}
                    files = [
                        ('media', (company_logo.name, company_logo, company_logo.content_type))
                    ]
                    headers = {
                        'api_name': 'phpm02_company_50_media',
                        'psk_id': str(media_psk_id)
                    }

                    # Send PUT request to upload media
                    response = requests.request("PUT", url, headers=headers, data=payload, files=files)

                    if response.status_code == 200:
                        messages.success(request, "Record and image updated successfully")
                        return redirect('phpm_company_list')
                    else:
                        return HttpResponse("Failed to update image")
                else:
                    messages.error(request, "Failed to fetch media records")
                    return render(request, 'Company/update_company.html')

            else:
                messages.error(request, "Failed to update company records")
                return render(request, 'Company/update_company.html')

        # In case the method is GET, show the existing company data
        context = {
            "object": res_data
        }

        return render(request, 'Company/update_company.html', context)

    else:
        # Handle the case where the initial API request fails
        messages.error(request, "Failed to fetch company data")
        return render(request, 'Company/update_company.html')


def phpm_delete_company(request, psk_id):
    url = f"{API_STUDIO_URL}deleteapi/delete/phpm02_company_50/{psk_id}"

    payload = {}
    headers = {}

    response = requests.request("DELETE", url, headers=headers, data=payload)

    if response.status_code == 200:
        messages.success(request, message="Deleted Successfully")
        return redirect('phpm_company_list')
    else:
        error_msg = response.json()
        messages.error(request, message=f"{error_msg['detail']}")


def phpm_course_list(request):
    url = f"{API_STUDIO_URL}getapi/phpm02_course_55/all"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code == 200:
        response_data = response.json()
    else:
        return HttpResponse("API call is not working")

    # print(response.text)

    context = {
        'response_data': response_data
    }

    return render(request, 'Course/course_list.html', context)


def phpm_company_create(request):
    if request.method == 'POST':
        active = request.POST.get('active', 'off') == 'on'
        course_code = request.POST['course_code']
        course_name = request.POST['course_name']
        course_type = request.POST['course_type']
        course_duration = request.POST['course_duration']

        url = f"{API_STUDIO_URL}postapi/create/phpm02_course_55"

        payload = json.dumps({
            "data": {
                "active": active,
                "course_code": course_code,
                "course_name": course_name,
                "course_type": course_type,
                "course_duration": course_duration,
            }
        })

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            messages.success(request, "Company details created successfully")
            return redirect('phpm_course_list')
        else:
            return HttpResponse("Failure: " + response.text)

    return render(request, 'Course/create_course.html')


def phpm_update_course(request, psk_id):
    url = f"{API_STUDIO_URL}getapi/all_fields/phpm02_course_55/{psk_id}"

    active = request.POST.get('active') == 'on'

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    res_data = response.json()

    if response.status_code == 200:

        if request.method == 'POST':

            course_code = request.POST['course_code']
            course_name = request.POST['course_name']
            course_type = request.POST['course_type']
            course_duration = request.POST['course_duration']

            update_url = f"{API_STUDIO_URL}updateapi/update/phpm02_course_55/{psk_id}"

            payload = json.dumps({
                "data": {
                    "active": active,
                    "course_code": course_code,
                    "course_name": course_name,
                    "course_type": course_type,
                    "course_duration": course_duration,
                }
            })

            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.put(update_url, headers=headers, data=payload)

            if response.status_code == 200:
                messages.success(request, message="Updated successfully.")
                return redirect('phpm_course_list')
            else:
                messages.error(request, message="Failed to update records")
                return render(request, 'Course/update_course.html')

        context = {
            "object": res_data
        }

    return render(request, 'Course/update_course.html', context)


def phpm_delete_course(request, psk_id):
    url = f"{API_STUDIO_URL}deleteapi/delete/phpm02_course_55/{psk_id}"

    payload = {}
    headers = {}

    response = requests.request("DELETE", url, headers=headers, data=payload)

    if response.status_code == 200:
        messages.success(request, "Deleted Successfully")
        return redirect('phpm_course_list')
    else:
        error_msg = response.json()
        messages.error(request, message=f"{error_msg['detail']}")





