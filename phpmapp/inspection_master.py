import requests as req
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
import json, hashlib

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


def designation_role_id(designation):
    designation_url = f"{API_STUDIO_URL}getapi/asa0501_01_01"
    payload = json.dumps({
        "queries": [
            {
                "field": "user_role",
                "value": designation.capitalize(),
                "operation": "equal"
            }
        ],
        "search_type": "first"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = req.request("POST", designation_url, headers=headers, data=payload)
    if response.status_code == 200:
        designation_id = response.json()['psk_id']

    else:
        designation_id = None

    return designation_id


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
    districts = hud_data_get()
    designation_data = designation_role()

    if request.method == 'POST':
        active = True
        designation = request.POST['designation']
        print("designation : ", designation)
        hud_district_psk_id = request.POST['officer_district_psk_id']
        officer_name = request.POST['officer_name']
        officer_mobile = request.POST['officer_mobile']
        officer_email = request.POST['officer_email']
        officer_password = request.POST['officer_password']
        usertype = "user"

        designation_id = designation_role_id(designation)
        convert_designation_id = str({designation_id})

        md5_hash = hashlib.md5(officer_password.encode()).hexdigest()

        if not User.objects.filter(username=officer_name).exists():
            obj = User(
                username=officer_name,
                password=md5_hash,
                first_name=usertype,
                email=officer_email
            )
            obj.save()

            url_post = f"{API_STUDIO_URL}postapi/create/phpm02_inspection_officer_57"

            payload = json.dumps({
                "data": {
                    "active": active,
                    "officer_contact_no": officer_mobile,
                    "officer_designation": designation,
                    "officer_district_psk_id": hud_district_psk_id,
                    "officer_name": officer_name,
                    "officer_email": officer_email,
                    # "officer_password": md5_hash,
                    "officer_password": officer_password,
                }
            })

            headers = {'Content-Type': 'application/json'}
            response = req.post(url_post, headers=headers, data=payload)

            if response.status_code != 200:
                # API failed, delete the created user
                obj.delete()
                messages.error(request, f"Error: {response.text}")
                return redirect('phpm_Inspection_create')

            # Proceed with second API call
            create_user_api_url = f"{API_STUDIO_URL}postapi/create/asa0504_01_01"

            payload = json.dumps({
                "data": {
                    "username": officer_name,
                    "password": obj.password,
                    "user_type": usertype,
                    "email": officer_email,
                    "user_roles": convert_designation_id,
                    "active": True
                }
            })

            response = req.post(create_user_api_url, headers=headers, data=payload)

            if response.status_code == 200:
                res_data = response.json()
                obj.last_name = res_data['psk_id']
                obj.save()
                messages.success(request, f"The user '{officer_name}' was created successfully.")
                return redirect('phpm_Inspection_list')

            else:
                # If second API fails, delete the user
                obj.delete()
                messages.error(request, f"Error: {response.text}")
                return redirect('phpm_Inspection_create')

    context = {
        'districts': districts,
        "designation_data": designation_data
    }

    return render(request, 'Inspection_Master/create_inspection.html', context)


def phpm_Inspection_update(request, psk_id):
    districts = hud_data_get()
    obj = inspection_id_data_get(psk_id)

    officer_name = obj.get('officer_name', '')  # Avoid KeyError

    dj_obj = User.objects.filter(username=officer_name).first()
    pykit_user_id = dj_obj.last_name if dj_obj else None  # Avoid AttributeError

    usertype = "user"

    if request.method == 'POST':
        designation = request.POST.get('designation', '')
        hud_district_psk_id = request.POST.get('officer_district_psk_id', '')
        officer_name = request.POST.get('officer_name', '')
        officer_mobile = request.POST.get('officer_mobile', '')
        officer_email = request.POST.get('officer_email', '')
        officer_password = request.POST.get('officer_password', '')
        active = request.POST.get('active') == 'on'

        designation_id = designation_role_id(designation)
        convert_designation_id = str({designation_id})

        # Securely hash the password before storing
        md5_hash = hashlib.md5(officer_password.encode()).hexdigest()

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

        headers = {'Content-Type': 'application/json'}

        response = req.put(update_url, headers=headers, data=payload)

        if response.status_code != 200:
            messages.error(request, f"Error: {response.text}")
            return redirect('phpm_Inspection_update', psk_id)

        # Proceed with second API call
        if pykit_user_id:
            create_user_api_url = f"{API_STUDIO_URL}updateapi/update/asa0504_01_01/{int(pykit_user_id)}"

            payload = json.dumps({
                "data": {
                    "username": officer_name,
                    "password": md5_hash,  # Use hashed password
                    "user_type": usertype,
                    "email": officer_email,
                    "user_roles": convert_designation_id,
                    "active": active
                }
            })

            response = req.put(create_user_api_url, headers=headers, data=payload)

            if response.status_code == 200 and dj_obj:
                dj_obj.password = md5_hash
                dj_obj.first_name = usertype
                dj_obj.email = officer_email
                dj_obj.save()
                messages.success(request, f"The user '{officer_name}' was updated successfully.")
                return redirect('phpm_Inspection_list')
            else:
                messages.error(request, f"Error: {response.text}")
                return redirect('phpm_Inspection_update', psk_id)

    designation_data = designation_role()

    context = {
        'districts': districts,
        'obj': obj,
        "designation_data": designation_data
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
    obj = inspection_id_data_get(psk_id)
    officer_name = obj.get('officer_name', '')

    dj_obj = User.objects.filter(username=officer_name).first()
    pykit_user_id = dj_obj.last_name if dj_obj else None

    url1 = f"{API_STUDIO_URL}deleteapi/delete/phpm02_inspection_officer_57/{psk_id}"
    url2 = f"{API_STUDIO_URL}deleteapi/delete/asa0504_01_01/{int(pykit_user_id)}"

    response1 = req.request("DELETE", url1)
    response2 = req.request("DELETE", url2) if response1.status_code == 200 else None

    if response1.status_code == 200 and response2 and response2.status_code == 200:
        if dj_obj:
            dj_obj.delete()
        messages.success(request, "Deleted Successfully")
    else:
        error_msg = response1.json() if response1.status_code != 200 else response2.json()
        messages.error(request, f"{error_msg.get('detail', 'Deletion failed')}")

    return redirect('phpm_Inspection_list')