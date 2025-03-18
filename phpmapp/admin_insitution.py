import json
import requests

import requests as req
from django.contrib import messages
from django.shortcuts import redirect, render

from user_management.views import API_STUDIO_URL
from vas1.institution import block_data_get, hud_data_get, district_data_get, institution_id_data_get

def ins_media_data_get(psk_id):
    url_block = f"{API_STUDIO_URL}crudapp/get/media/phpm02_institution_59_media/parent/{psk_id}"
    block_response = requests.get(url_block)

    if block_response.status_code == 200:
        block = block_response.json()
    else:
        block = []
    return block


def institution_list_view(request):
    url = f"{API_STUDIO_URL}getapi/phpm02_institution_59/all"

    payload = ""
    headers = {}

    response = req.request("GET", url, headers=headers, data=payload)

    if response.status_code == 200:
        institution_list = response.json()

    context = {"institution_list": institution_list}
    return render(request, "Instituion_master/list_institution.html", context)


def admin_create_institution(request):
    block_data = block_data_get()
    hud_data = hud_data_get()
    district_data = district_data_get()

    if request.method == 'POST':
        active = True
        institution_code = request.POST['institution_code']
        institution_trust_name = request.POST['institution_trust_name']
        institution_name = request.POST['institution_name']
        institution_address = request.POST.get('institution_addr')
        institution_distirict_psk_id = request.POST['institution_distirict_psk_id']
        institution_hud_psk_id = request.POST['institution_hud_psk_id']
        institution_block_psk_id = request.POST['institution_block_psk_id']
        institution_pincode = request.POST['institution_pincode']
        # institution_date_of_incorporation = request.POST['institution_date_of_incorporation']
        # institution_gstin = request.POST['institution_gstin']
        year_of_established = request.POST['year_of_established']

        # contact_type = request.POST['contact_type']
        contact_name = request.POST['contact_name']
        contact_no = request.POST['contact_no']
        contact_email = request.POST['contact_email']

        institution_email = request.POST['institution_email']
        institution_phone_number = request.POST['institution_phone_number']
        umis = request.POST['umis']

        # company_logo = request.FILES.get('file')

        contact_details = {"contact_details": [
            {"contact_type": "Principal", "contact_name": contact_name, "contact_no": contact_no,
             "contact_email": contact_email}]}

        url_post = f"{API_STUDIO_URL}postapi/create/phpm02_institution_59"

        # Prepare payload for the API request
        payload = json.dumps({
            "data": {
                "active": active,
                "institution_code": institution_code,
                "institution_trust_name": institution_trust_name,
                "institution_name": institution_name,
                "institution_address_text": institution_address,
                "institution_distirict_psk_id": institution_distirict_psk_id,
                "institution_hud_psk_id": institution_hud_psk_id,
                "institution_block_psk_id": institution_block_psk_id,
                "year_of_established": year_of_established,

                "institution_pincode": institution_pincode,
                "institution_address": institution_phone_number,
                # "institution_date_of_incorporation": institution_date_of_incorporation,
                # "institution_gstin": institution_gstin,
                "contact_details_text": json.dumps(contact_details, indent=4),

                "umis": umis,
                "institution_email": institution_email,
            }
        })

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.post(url_post, headers=headers, data=payload)

        if response.status_code == 200:
            res_data = response.json()
            psk_id = res_data.get('psk_id')

            # if company_logo:
            #     url = f"{API_STUDIO_URL}crudapp/upload/media/phpm02_institution_59_media"
            #
            #     payload = {'parent_psk_id': psk_id}
            #     files = [
            #         ('media', (company_logo.name, company_logo, company_logo.content_type))
            #     ]
            #     headers = {
            #         'api_name': 'phpm02_institution_59_media'
            #     }
            #
            #     response = requests.request("POST", url, headers=headers, data=payload, files=files)
            #
            #     if response.status_code == 200:
            #         messages.success(request, "Institution details Register successfully")
            #         return redirect('institution_list_view')
            #     else:
            #         messages.success(request, "Failed to upload logo")
            # else:
            #     return redirect('institution_list_view')

            messages.success(request, "Institution details Register successfully")
            return redirect('institution_list_view')

        else:
            messages.error(request, f"Error: {response.text}")

    context = {
        'block_data': block_data,
        'hud_data': hud_data,
        'districts': district_data
    }

    return render(request, 'institution/create_institution.html', context)


def admin_update_institution(request, psk_id):
    block_data = block_data_get()
    hud_data = hud_data_get()
    district_data = district_data_get()

    obj = institution_id_data_get(psk_id)
    contact_details_text = obj['contact_details_text']

    # Convert JSON string to Python dictionary (if needed)
    if isinstance(contact_details_text, str):
        contact_details_text = json.loads(contact_details_text)

    # Extract Principal's contact details
    principal_details = next(
        (contact for contact in contact_details_text.get("contact_details", []) if
         contact["contact_type"] == "Principal"),
        None
    )

    obj['contact_name'] = principal_details['contact_name']
    obj['contact_no'] = principal_details['contact_no']
    obj['contact_email'] = principal_details['contact_email']

    # media_obj = ins_media_data_get(psk_id)
    # print(media_obj)

    if request.method == 'POST':
        institution_code = request.POST['institution_code']
        institution_trust_name = request.POST['institution_trust_name']
        institution_name = request.POST['institution_name']
        institution_address = request.POST.get('institution_addr')
        institution_distirict_psk_id = request.POST['institution_distirict_psk_id']
        institution_hud_psk_id = request.POST['institution_hud_psk_id']
        institution_block_psk_id = request.POST['institution_block_psk_id']
        institution_pincode = request.POST['institution_pincode']
        # institution_date_of_incorporation = request.POST['institution_date_of_incorporation']
        # institution_gstin = request.POST['institution_gstin']
        year_of_established = request.POST['year_of_established']

        # active = request.POST.get('active') == 'on'

        # contact_type = request.POST['contact_type']
        contact_name = request.POST['contact_name']
        contact_no = request.POST['contact_no']
        contact_email = request.POST['contact_email']

        institution_email = request.POST['institution_email']
        institution_phone_number = request.POST['institution_phone_number']
        umis = request.POST['umis']

        # company_logo = request.FILES.get('file')

        contact_details = {"contact_details": [
            {"contact_type": "Principal", "contact_name": contact_name, "contact_no": contact_no,
             "contact_email": contact_email}]}

        update_url = f"{API_STUDIO_URL}updateapi/update/phpm02_institution_59/{psk_id}"

        # Prepare payload for the API request
        payload = json.dumps({
            "data": {
                # "active": active,
                "institution_code": institution_code,
                "institution_trust_name": institution_trust_name,
                "institution_name": institution_name,
                "institution_address_text": institution_address,
                "institution_address": institution_phone_number,
                "institution_distirict_psk_id": institution_distirict_psk_id,
                "institution_hud_psk_id": institution_hud_psk_id,
                "institution_block_psk_id": institution_block_psk_id,
                "year_of_established": year_of_established,

                "institution_pincode": institution_pincode,
                # "institution_date_of_incorporation": institution_date_of_incorporation,
                # "institution_gstin": institution_gstin,
                "contact_details_text": json.dumps(contact_details, indent=4),

                "umis": umis,
                "institution_email": institution_email,
            }
        })

        headers = {
            'Content-Type': 'application/json'
        }

        response = req.put(update_url, headers=headers, data=payload)

        if response.status_code == 200:

            # media_url = f"{API_STUDIO_URL}crudapp/get/media/phpm02_institution_59_media/parent/{psk_id}"
            # media_url_response = requests.get(media_url, headers={}, data={})
            #
            # if not media_url_response.json() and company_logo:
            #     url = f"{API_STUDIO_URL}crudapp/upload/media/phpm02_institution_59_media"
            #
            #     payload = {'parent_psk_id': psk_id}
            #     files = [
            #         ('media', (company_logo.name, company_logo, company_logo.content_type))
            #     ]
            #     headers = {
            #         'api_name': 'phpm02_institution_59_media'
            #     }
            #
            #     response = requests.request("POST", url, headers=headers, data=payload, files=files)
            #
            #     if response.status_code == 200:
            #         messages.success(request, "Institution details Register successfully")
            #         return redirect('institution_list_view')
            #     else:
            #         messages.success(request, "Failed to upload logo")
            # else:
            #
            #     already_image_res = media_url_response.json()[0]
            #
            #     if company_logo:
            #
            #         url = f"{API_STUDIO_URL}crudapp/upload/media/phpm02_institution_59_media/{already_image_res['psk_id']}"
            #
            #         payload = {'parent_psk_id': psk_id}
            #         files = [
            #
            #             ('media', (company_logo.name, company_logo, company_logo.content_type))
            #         ]
            #         headers = {}
            #
            #         response = req.request("PUT", url, headers=headers, data=payload, files=files)
            #         if response.status_code == 200:
            #             messages.success(request, message=f"profile photo was updated successfully.")

            return redirect('institution_list_view')

        else:
            messages.error(request, f"Error: {response.text}")

    context = {
        'block_data': block_data,
        'hud_data': hud_data,
        'districts': district_data,
        "obj": obj,
        # "media": media_obj[0],
        "API_STUDIO_URL": API_STUDIO_URL,
    }
    return render(request, 'Instituion_master/admin_update_institution.html', context)
