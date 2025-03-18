import json
import random

from django.contrib import messages
from django.shortcuts import render
import requests
from django.http import JsonResponse

from user_management.settings_views import user_bundle_settings
from vas1 import institution

API_STUDIO_URL = user_bundle_settings()


def generate_unique_id():
    return str(random.randint(10000, 99999))


def razorpay_page(request):
    return render(request, 'razor_pay/razor-pay.html')


def process_razorpay_gateway(request):
    if request.method == "POST":

        razor_payment_id = request.POST.get('razorpay_payment_id')
        applicant_id = request.POST.get('applicant_id')
        totalamount = request.POST.get('totalamount')

        razorpay_key = 'rzp_test_VAMCpzqFjfqgDK'
        razorpay_secret = 'gixpUaUjW6WWZvP5wfHF1Mtk'
        url = f"https://api.razorpay.com/v1/payments/{razor_payment_id}"
        auth = (razorpay_key, razorpay_secret)
        response = requests.get(url, auth=auth)
        if response.status_code == 200:
            res_data = response.json()
            json_payload_readable_str = json.dumps(res_data)
            paymentstatus = res_data.get('status')
            razorpay_id = res_data.get('id')
            amount = res_data.get('amount')
            currency = res_data.get('currency')
            description = res_data.get('description')
            wallet = res_data.get('wallet')
            contact = res_data.get('contact')
            method = res_data.get('method')

        if paymentstatus == 'authorized':

            url = f"{API_STUDIO_URL}postapi/create/svv02_payment_history_09"

            payload = json.dumps({

                "data": {
                    "phone_number": contact,
                    "uuid": razorpay_id,
                    "payment_amount": amount,
                    "payment_status": paymentstatus,
                    "parent_psk_id": applicant_id,
                    "payment_description": description,
                    "payment_mode": wallet,
                    "refund_amount": "0.00",
                    "payment_currency": currency,
                    "json_payload_readable": json_payload_readable_str
                }

            })

            headers = {
                'Content-Type': 'application/json'
            }

            # print("PAYLOAD:", payload)

            response = requests.request("POST", url, headers=headers, data=payload)

            if response.status_code == 200:

                response_data = {
                    'payment_status': "success",
                    'payment_detail': res_data,
                }
                return JsonResponse(response_data)
            else:
                response_data = {
                    'payment_status': "failure",
                    'payment_detail': paymentstatus,
                }
                return JsonResponse(response_data)



        else:

            url = f"{API_STUDIO_URL}postapi/create/svv02_payment_history_09"

            payload = json.dumps({
                "data": {
                    "parent_psk_id": applicant_id,
                    "phone_number": contact,
                    "uuid": razorpay_id,
                    "payment_amount": amount,
                    "payment_status": paymentstatus,
                    "payment_description": description,
                    "payment_mode": wallet,
                    "refund_amount": "0.00",
                    "payment_currency": currency,
                    "json_payload_readable": json_payload_readable_str

                }

            })

            # print("PAYLOAD:", payload)

            headers = {
                'Content-Type': 'application/json'
            }

        if response.status_code == 200:

            response_data = {
                'payment_status': "success",
                'payment_detail': res_data,
            }
            return JsonResponse(response_data)
        else:
            response_data = {
                'payment_status': "failure",
                'payment_detail': paymentstatus,
            }
            return JsonResponse(response_data)


# def payment_success(request, applicant_id):
#     messages.success(request, "Payment successfully proceed")
#
#     # institution.work_flow_table_insert(request, applicant_id, status="Submitted")
#     # institution.application_status_update(applicant_id, "Submitted")
#
#     url = f"{API_STUDIO_URL}auth/token?secret_key=9L5pkiVSkPY0WXCEqXMj4403SyKaKAaN"
#
#     payload = {}
#     headers = {}
#
#     response = requests.request("POST", url, headers=headers, data=payload)
#     # print(response)
#     if response.status_code == 200:
#         res_data = response.json()
#         access_token = res_data.get('access_token')
#         token_type = res_data.get('token_type')
#         # print(token_type)
#     url = f"{API_STUDIO_URL}coreapi/api/phpm0218"
#
#     payload = json.dumps({
#         "data": {
#             "applicant_id": applicant_id
#         }
#     })
#
#     headers = {
#         'Content-Type': 'application/json',
#         'Authorization': f'{token_type} {access_token}'
#     }
#
#     response = requests.request("POST", url, headers=headers, data=payload)
#
#     if response.status_code == 200:
#         main_api_data = response.json()
#
#     context = {
#
#         'main_api_data': main_api_data,
#         'applicant_id': applicant_id,
#         "menu": "application",
#     }
#
#     return render(request, "razor_pay/payment_success.html", context)
#
#
# def payment_failure(request, applicant_id):
#     url = f"{API_STUDIO_URL}auth/token?secret_key=9L5pkiVSkPY0WXCEqXMj4403SyKaKAaN"
#
#     payload = {}
#     headers = {}
#
#     response = requests.request("POST", url, headers=headers, data=payload)
#     if response.status_code == 200:
#         res_data = response.json()
#         access_token = res_data.get('access_token')
#         token_type = res_data.get('token_type')
#     url = f"{API_STUDIO_URL}coreapi/api/phpm0218"
#
#     payload = json.dumps({
#         "data": {
#             "applicant_id": applicant_id
#         }
#     })
#
#     headers = {
#         'Content-Type': 'application/json',
#         'Authorization': f'{token_type} {access_token}'
#     }
#
#     response = requests.request("POST", url, headers=headers, data=payload)
#
#     if response.status_code == 200:
#         main_api_data = response.json()
#
#     context = {
#
#         'main_api_data': main_api_data,
#         'applicant_id': applicant_id,
#     }
#     return render(request, "razor_pay/payment_failure.html", context)


def payment_success(request, applicant_id):
    messages.success(request, "Payment successfully proceed")

    institution.work_flow_table_insert(request, applicant_id, status="Submitted")
    institution.application_status_update(applicant_id, "Submitted")

    url = f"{API_STUDIO_URL}auth/token?secret_key=9L5pkiVSkPY0WXCEqXMj4403SyKaKAaN"
    payload = {}
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        res_data = response.json()
        access_token = res_data.get('access_token')
        token_type = res_data.get('token_type')
    url = f"{API_STUDIO_URL}coreapi/api/phpm0218"

    payload = json.dumps({
        "data": {
            "applicant_id": applicant_id
        }
    })

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'{token_type} {access_token}'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code == 200:
        main_api_data = response.json()

    url = f"{API_STUDIO_URL}getapi/svv02_payment_history_09"
    payload = json.dumps({
        "queries": [
            {
                "field": "parent_psk_id",
                "value": applicant_id,
                "operation": "equal"
            },
            {
                "field": "payment_status",
                "value": "authorized",
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
        razorpaydetails = response.json()
        print("----",razorpaydetails)
        pay_amount = (razorpaydetails.get('payment_amount') / 100)
    context = {

        'main_api_data': main_api_data,
        'applicant_id': applicant_id,
        'razorpaydetails': razorpaydetails,
        'pay_amount': pay_amount,
        "menu": "application",
    }

    return render(request, "razor_pay/payment_success.html", context)


def payment_failure(request, applicant_id):
    url = f"{API_STUDIO_URL}auth/token?secret_key=9L5pkiVSkPY0WXCEqXMj4403SyKaKAaN"

    payload = {}
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        res_data = response.json()
        access_token = res_data.get('access_token')
        token_type = res_data.get('token_type')
    url = f"{API_STUDIO_URL}coreapi/api/phpm0218"

    payload = json.dumps({
        "data": {
            "applicant_id": applicant_id
        }
    })

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'{token_type} {access_token}'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code == 200:
        main_api_data = response.json()

    url = f"{API_STUDIO_URL}getapi/svv02_payment_history_09"

    payload = json.dumps({
        "queries": [
            {
                "field": "parent_psk_id",
                "value": applicant_id,
                "operation": "equal"
            },
            {
                "field": "payment_status",
                "value": "authorized",
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
        razorpaydetails = response.json()
    pay_amount = (razorpaydetails.get('payment_amount') / 100)
    context = {

        'main_api_data': main_api_data,
        'applicant_id': applicant_id,
        'payment_detail': razorpaydetails,
        'pay_amount': pay_amount
    }
    return render(request, "razor_pay/payment_failure.html", context)

