import requests as req
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
import json

from user_management.views import API_STUDIO_URL
from vas1.institution import district_data_get, hud_id_data_get, hud_data_get


def designation_role():
    designation_url = f"{API_STUDIO_URL}getapi/asa0501_01_01/all"
    designation_response = req.get(designation_url)
    if designation_response.status_code == 200:
        designation_data = designation_response.json()
    else:
        designation_data = []
    return designation_data


def inspection_master():
    inspection_url = f"{API_STUDIO_URL}getapi/phpm02_inspection_officer_57/all"
    inspection_response = req.get(inspection_url)
    if inspection_response.status_code == 200:
        inspection_data = inspection_response.json()
    else:
        inspection_data = []
    return inspection_data


def inspection_id_data_get(psk_id):
    url_hud = f"{API_STUDIO_URL}getapi/phpm02_inspection_officer_57/{psk_id}"
    inspection_response = req.get(url_hud)

    if inspection_response.status_code == 200:
        inspection = inspection_response.json()
    else:
        inspection = {}
    return inspection


def ajax_hud_designation(request):
    if request.method == "GET":
        designation = request.GET['designation']
        district_psk_id = request.GET['district_psk_id']
        hud_data = hud_id_data_get(district_psk_id)
        hud_code = hud_data['hud_code']

        inspection_data = inspection_master()

        if not inspection_data:
            auto_user_id = hud_code + designation + "001"
            data = {"auto_user_id": auto_user_id}
            return JsonResponse(data)

        check_user = hud_code + designation

        count = 1  # Default starting count
        for obj in inspection_data:
            officer_name = obj.get('officer_name', '')

            if officer_name.startswith(check_user):
                count += 1  # Increment count if similar ID exists

        auto_user_id = f"{check_user}{str(count).zfill(3)}"
        return JsonResponse({"auto_user_id": auto_user_id})


def phpm_Inspection_create(request):
    districts = district_data_get()
    designation_data = designation_role()
    if request.method == 'POST':
        active = True
        designation = request.POST['designation']
        hud_district_psk_id = request.POST['officer_district_psk_id']
        officer_name = request.POST['officer_name']
        officer_mobile = request.POST['officer_mobile']
        officer_email = request.POST['officer_email']
        officer_password = request.POST['officer_password']

        url_post = f"{API_STUDIO_URL}postapi/create/phpm02_inspection_officer_57"

        payload = json.dumps({
            "data": {
                "active": active,
                "officer_contact_no": officer_mobile,
                "officer_designation": designation,
                "officer_district_psk_id": hud_district_psk_id,
                "officer_name": officer_name,
                "officer_email": officer_email,
                "officer_password": officer_password,
            }
        })

        headers = {
            'Content-Type': 'application/json'
        }

        response = req.post(url_post, headers=headers, data=payload)

        if response.status_code == 200:
            messages.success(request, "uSER created successfully.")
            return redirect('phpm_Inspection_list')
        else:
            messages.error(request, f"Error: {response.text}")

    context = {
        'districts': districts,
        "designation_data": designation_data
    }

    return render(request, 'Inspection_Master/create_inspection.html', context)


def phpm_Inspection_update(request, psk_id):
    districts = district_data_get()
    obj = inspection_id_data_get(psk_id)

    if request.method == 'POST':
        designation = request.POST['designation']
        hud_district_psk_id = request.POST['officer_district_psk_id']
        officer_name = request.POST['officer_name']
        officer_mobile = request.POST['officer_mobile']
        officer_email = request.POST['officer_email']
        officer_password = request.POST['officer_password']
        active = request.POST.get('active') == 'on'

        update_url = f"{API_STUDIO_URL}updateapi/update/phpm02_inspection_officer_57/{psk_id}"

        payload = json.dumps({
            "data": {
                "active": active,
                "officer_contact_no": officer_mobile,
                "officer_designation": designation,
                "officer_district_psk_id": hud_district_psk_id,
                "officer_name": officer_name,
                "officer_email": officer_email,
                "officer_password": officer_password,
            }
        })

        headers = {
            'Content-Type': 'application/json'
        }

        response = req.put(update_url, headers=headers, data=payload)

        if response.status_code == 200:
            messages.success(request, message="User Updated Successfully")
            return redirect('phpm_Inspection_list')
        else:
            messages.error(request, f"Error: {response.text}")

    context = {
        'districts': districts,
        'obj': obj
    }
    return render(request, 'Inspection_Master/update_inspection.html', context)


def phpm_Inspection_list(request):
    inspection = inspection_master()
    hud_data = hud_data_get()

    context = {
        'response_data': inspection,
        "hud_data": hud_data
    }
    return render(request, 'Inspection_Master/inspection_list.html', context)


def phpm_Inspection_delete(request, psk_id):
    url = f"{API_STUDIO_URL}deleteapi/delete/phpm02_inspection_officer_57/{psk_id}"

    payload = {}
    headers = {}

    response = req.request("DELETE", url, headers=headers, data=payload)

    if response.status_code == 200:
        messages.success(request, "Deleted Successfully")
        return redirect('phpm_Inspection_list')
    else:
        error_msg = response.json()
        messages.error(request, message=f"{error_msg['detail']}")

    return HttpResponse("Deleted Successfully")
