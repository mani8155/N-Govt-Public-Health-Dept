from django.contrib import messages
from django.shortcuts import render, redirect
from captcha.image import ImageCaptcha
import os
import uuid
from django.conf import settings
import hashlib
import string
import random
import json
import requests as req
from django.http import JsonResponse

from user_management.settings_views import user_bundle_settings

# Create your views here.

API_STUDIO_URL = user_bundle_settings()
ApplicantUserTableName = 'phpm02_user_master_01'


def get_applicant_user_data(request, username):
    url = f"{API_STUDIO_URL}getapi/{ApplicantUserTableName}"

    payload = json.dumps({
        "queries": [
            {
                "field": "username",
                "value": username,
                "operation": "equal"
            }
        ],
        "search_type": "first"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = req.request("GET", url, headers=headers, data=payload)
    # print(response.text)

    if response.status_code == 200:
        res_data = response.json()
        return res_data


def generate_captcha_text(length=6):
    return ''.join(random.choices(string.ascii_uppercase, k=5))  # Generate 5 random uppercase letters


# Create CAPTCHA image and save it in the static directory
def create_captcha_image(text, file_name):
    static_dir = os.path.join(settings.BASE_DIR, "static", "captcha_images")
    os.makedirs(static_dir, exist_ok=True)  # Ensure the directory exists
    file_path = os.path.join(static_dir, file_name)
    image = ImageCaptcha(width=280, height=90)
    captcha_image = image.generate_image(text)
    captcha_image.save(file_path)
    return f"captcha_images/{file_name}"  #


def username_pass_check(request, username):
    url = f"{API_STUDIO_URL}getapi/{ApplicantUserTableName}"

    payload = json.dumps({
        "queries": [
            {
                "field": "username",
                "value": username,
                "operation": "equal"
            }
        ],
        "search_type": "first"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = req.request("GET", url, headers=headers, data=payload)

    if response.status_code == 200:
        res_data = response.json()
        return res_data['password_hash'], res_data['psk_id']
    else:
        return False, False


def loginpage(request):
    # print("function working")
    captcha_text = generate_captcha_text()
    file_name = f"{uuid.uuid4().hex}.png"  # Unique file name for each CAPTCHA
    captcha_img = create_captcha_image(captcha_text, file_name)

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        md5_hash = hashlib.md5(password.encode()).hexdigest()
        captcha_text_input = request.POST.get('captcha_text_input', '')
        correct_captcha = request.POST.get('captcha_text', '')  # G

        if captcha_text_input != correct_captcha:
            messages.error(request, "Invalid CAPTCHA. Please try again.")
        else:
            check_password, user_id = username_pass_check(request, username)

            if not user_id:
                messages.error(request, message="Incorrect 'Username' or 'Password'")

            if check_password == md5_hash:
                # return redirect('help', user_id)
                response = redirect('application_navigation')  # Create a response object to set cookies
                response.set_cookie('saved_username', username, max_age=30 * 24 * 60 * 60)  # 30 days
                return response
            else:
                messages.error(request, message="Incorrect 'Username' or 'Password'")

    context = {"captcha_img": f"/static/{captcha_img}", "captcha_text": captcha_text}

    return render(request, "applicant_user_master/loginpage.html", context)


def random_num_generate():
    import random as r
    ph_no = []

    ph_no.append(r.randint(1, 9))
    for _ in range(8):
        ph_no.append(r.randint(0, 9))
    phone_number = "".join(map(str, ph_no))
    return phone_number


# def registerpage(request):
#     # Generate CAPTCHA
#     captcha_text = generate_captcha_text()
#     file_name = f"{uuid.uuid4().hex}.png"  # Unique file name for each CAPTCHA
#     captcha_img = create_captcha_image(captcha_text, file_name)
#
#     if request.method == "POST":
#         firstname = request.POST.get('firstname', '').strip()
#         lastname = request.POST.get('lastname', '').strip()
#         email = request.POST.get('email', '').strip()
#         mobile = request.POST.get('mobile', '').strip()
#         username = request.POST.get('username', '').strip()
#         password = request.POST.get('password', '').strip()
#         confirm_password = request.POST.get('confirmpassword', '').strip()
#         captcha_text_input = request.POST.get('captcha_text_input', '').strip()
#         correct_captcha = request.POST.get('captcha_text', '').strip()
#         application_type = request.POST.get('application_type', '').strip()
#
#         # Validate CAPTCHA
#         if captcha_text_input != correct_captcha:
#             messages.error(request, "Invalid CAPTCHA. Please try again.")
#         # Validate passwords match
#         elif password != confirm_password:
#             messages.error(request, "Passwords do not match.")
#         else:
#             # Hash the password using SHA-256
#             md5_hash = hashlib.md5(password.encode()).hexdigest()
#             member_id = random_num_generate()
#
#             # API URL
#             url = f"https://api.apistudio.app/postapi/create/{ApplicantUserTableName}"
#
#             # Data payload
#             payload = json.dumps({
#                 "data": {
#                     "firstname": firstname,
#                     "lastname": lastname,
#                     "email": email,
#                     "password_hash": md5_hash,
#                     "mobile": mobile,
#                     "username": username,
#                     "member_id": member_id,
#                     "application_type": application_type
#                 }
#             })
#             headers = {'Content-Type': 'application/json'}
#
#             try:
#                 # Make API request
#                 response = req.post(url, headers=headers, data=payload)
#                 print(response.text)
#                 if response.status_code == 200:
#                     resdata = response.json()
#                     psk_id = resdata['psk_id']
#                     messages.success(request, "Registration successful.")
#                     return redirect('applicant_verification', id=psk_id)
#                 else:
#                     resdata = response.json()
#                     messages.error(request, resdata['detail'])
#             except req.RequestException as e:
#                 messages.error(request, f"An error occurred: {e}")
#
#     # Context for the template
#     context = {
#         "captcha_img": f"/static/{captcha_img}",
#         "captcha_text": captcha_text
#     }
#
#     return render(request, "applicant_user_master/registerpage.html", context)


def institution_tbl_data_get():
    institution_url = f"{API_STUDIO_URL}getapi/phpm02_institution_59/all"
    institution_response = req.get(institution_url)

    if institution_response.status_code == 200:
        institution_data = institution_response.json()
    else:
        institution_data = []
    return institution_data


def registerpage(request):
    print("dsjhfsjdhfsjkdfhs")
    institution_data = institution_tbl_data_get()

    if request.method == "POST":
        institution_id = request.POST.get('institution_name', '').strip()
        email = request.POST.get('email', '').strip()
        mobile = request.POST.get('mobile', '').strip()
        # username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
        else:
            # Hash the password using SHA-256
            md5_hash = hashlib.md5(password.encode()).hexdigest()
            member_id = random_num_generate()

            # API URL
            url = f"{API_STUDIO_URL}postapi/create/{ApplicantUserTableName}"

            # Data payload
            payload = json.dumps({
                "data": {
                    "email": email,
                    "password_hash": md5_hash,
                    "mobile": mobile,
                    "username": email,
                    "member_id": member_id,
                    "institution_name": institution_id,

                }
            })
            headers = {'Content-Type': 'application/json'}

            try:
                # Make API request
                response = req.post(url, headers=headers, data=payload)
                if response.status_code == 200:
                    resdata = response.json()
                    psk_id = resdata['psk_id']
                    messages.success(request, "Registration successful.")
                    return redirect('applicant_verification', id=psk_id)
                else:
                    resdata = response.json()
                    messages.error(request, resdata['detail'])
            except req.RequestException as e:
                messages.error(request, f"An error occurred: {e}")

    context = {"institution_data": institution_data}
    return render(request, 'applicant_user_master/new_register_page.html', context)


def contact_details(request):
    if request.method == "POST":
        contact_name = request.POST['contact_name']
        contact_type = request.POST['contact_type']
        contact_no = request.POST['contact_no']
        contact_email = request.POST['contact_email']
        print(contact_name, contact_type, contact_no, contact_email)

    # return render(request, 'applicant_user_master/contact_details.html')


def applicant_user(request):
    print("ajax working")
    if request.method == "GET":
        userName = request.GET.get('userName')

        url = f"{API_STUDIO_URL}getapi/{ApplicantUserTableName}"

        payload = json.dumps({
            "queries": [
                {
                    "field": "username",
                    "value": userName,
                    "operation": "equal"
                }
            ],
            "search_type": "first"
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = req.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            res_data = response.json()
            applicant_photo = fetch_applicant_user_photo(request)
            res_data['applicant_photo'] = applicant_photo

            return JsonResponse(res_data)
    else:
        return JsonResponse({'error': 'Failed to fetch data'}, status=500)


def applicant_profile_pic_update(request):
    saved_username = request.COOKIES.get('saved_username', None)

    if not saved_username:
        redirect('loginpage')

    obj = get_applicant_user_data(request, username=saved_username)
    psk_id = obj.get('psk_id')

    _id_url = f"{API_STUDIO_URL}crudapp/get/media/{ApplicantUserTableName}_media/parent/{psk_id}"

    payload = {}
    headers = {
        'Content-Type': 'application/json'
    }

    response = req.request("GET", _id_url, headers=headers, data=payload)

    if response.text == "[]":
        # print("first time picture update")
        if request.method == 'POST':
            profile_photo = request.FILES.get('upload_photo')
            url = f"{API_STUDIO_URL}crudapp/upload/media/{ApplicantUserTableName}_media"

            payload = {'parent_psk_id': psk_id}
            files = [
                ('media',
                 (profile_photo.name, profile_photo.read(), 'image/png'))
            ]
            # print(files)
            headers = {}

            response = req.request("POST", url, headers=headers, data=payload, files=files)
            if response.status_code == 200:
                messages.success(request, message=f"profile photo was updated successfully.")
                return redirect('profile')
            else:
                error_res = response.json()
                messages.error(request, message=f"{error_res['detail']}")
                return redirect('profile')

    else:
        # print("update")
        user_data = response.json()[0]

        if request.method == 'POST':
            profile_photo = request.FILES.get('upload_photo')
            url = f"{API_STUDIO_URL}crudapp/upload/media/{ApplicantUserTableName}_media/{user_data['psk_id']}"

            payload = {'parent_psk_id': psk_id}
            files = [
                ('media',
                 (profile_photo.name, profile_photo.read(), 'image/png'))
            ]
            headers = {}

            response = req.request("PUT", url, headers=headers, data=payload, files=files)
            if response.status_code == 200:
                messages.success(request, message=f"profile photo was updated successfully.")
                return redirect('profile')
            else:
                error_res = response.json()
                messages.error(request, message=f"{error_res['detail']}")
                return redirect('profile')


def fetch_applicant_user_photo(request):
    saved_username = request.COOKIES.get('saved_username', None)
    if not saved_username:
        photo_url = None
        return photo_url

    obj = get_applicant_user_data(request, username=saved_username)
    psk_id = obj.get('psk_id')

    photo_tbl_url = f"{API_STUDIO_URL}crudapp/get/media/{ApplicantUserTableName}_media/parent/{psk_id}"
    photo_response = req.request("GET", photo_tbl_url, headers={})

    photo_response_data = photo_response.json()
    if photo_response_data:
        photo_response_value = photo_response_data[0]
        photo_url = f"{API_STUDIO_URL}crudapp/view/media/{ApplicantUserTableName}_media/{photo_response_value['psk_id']}"
    else:
        photo_url = None

    return photo_url


def profile(request):
    saved_username = request.COOKIES.get('saved_username', None)
    obj = get_applicant_user_data(request, username=saved_username)
    psk_id = obj.get('psk_id')
    print(psk_id)
    applicant_photo = fetch_applicant_user_photo(request)
    if request.method == "POST":
        print("form working")
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        username = request.POST.get('username')
        # year_of_established = request.POST.get('year_of_established')
        email = request.POST.get('email_address')
        # institution_name = request.POST.get('institution_name')
        # application_type = request.POST.get('application_type')
        # mobile = request.POST.get('contact_no')
        # user_address = request.POST.get('address')
        # state = request.POST.get('state')
        # district = request.POST.get('district')
        # pincode = request.POST.get('pincode')
        # institute_website = request.POST.get('website')

        url = f"{API_STUDIO_URL}updateapi/update/{ApplicantUserTableName}/{psk_id}"
        payload = json.dumps({
            "data": {
                "firstname": firstname,
                "lastname": lastname,
                "username": username,
                "email": email,
                # "year_of_established": year_of_established,
                # "institution_name": institution_name,
                # "application_type": application_type,
                # "mobile": mobile,
                # "user_address": user_address,
                # # "state": state,
                # "district": district,
                # "pincode": pincode,
                # "institute_website": institute_website,

            }
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = req.put(url, headers=headers, data=payload)

        if response.status_code == 200:

            messages.success(request, message="Profile updated successfully.")
            return redirect('help')
        else:
            messages.error(request,
                           message="Failed")

    context = {"applicant_photo": applicant_photo, "obj": obj}
    return render(request, "applicant_user_master/profile.html", context)


def resetpassword(request):
    saved_username = request.COOKIES.get('saved_username', None)

    if saved_username:
        obj = get_applicant_user_data(request, username=saved_username)
        current_password_hash = obj.get('password_hash')
        psk_id = obj.get('psk_id')
    else:
        current_password_hash = None
        return redirect('help')

    if request.method == "POST":
        current_password = request.POST.get("currentpassword")
        new_password = request.POST.get("newpassword")
        confirm_password = request.POST.get("confirmpassword")

        md5_hash = hashlib.md5(current_password.encode()).hexdigest()
        new_md5_hash = hashlib.md5(new_password.encode()).hexdigest()

        if current_password_hash != md5_hash:
            messages.error(request, message="Current password is incorrect.")
            # return redirect('help')

        elif new_password != confirm_password:
            messages.error(request, message="New password and confirm password do not match.")
            # return redirect('help')

        else:
            url = f"{API_STUDIO_URL}updateapi/update/{ApplicantUserTableName}/{psk_id}"
            payload = json.dumps({
                "data": {
                    "password_hash": new_md5_hash
                }
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = req.put(url, headers=headers, data=payload)

            if response.status_code == 200:
                messages.success(request, message="Password updated successfully.")
                return redirect('loginpage')
            else:
                messages.error(request,
                               message="Failed to update password: {response_data.get('message', 'Unknown error')}")

    return render(request, "applicant_user_master/resetpassword.html")


def applicant_verification(request, id):
    if request.method == "GET":
        otp_expiry = "1 minutes"

        # Get user data from API
        user_api_url = f"{API_STUDIO_URL}getapi/phpm02_user_master_01/{id}"
        response = req.get(user_api_url)
        if response.status_code == 200:
            user_data = response.json()
            username = user_data.get("username")
            email = user_data.get("email")
            member_id = user_data.get("member_id")
            psk_id = user_data.get("psk_id")

            # Get access token
            token_url = f"{API_STUDIO_URL}auth/token?secret_key=6n6A5dp7dLECGD3wAEs5W1Uq7vCrrUko"
            token_response = req.post(token_url)
            if token_response.status_code == 200:
                token_data = token_response.json()
                access_token = token_data.get('access_token')
                token_type = token_data.get('token_type')

                # Send OTP request to email
                otp_url = f"{API_STUDIO_URL}coreapi/api/phpm0212"
                payload = json.dumps({"data": {"email": email, "username": username}})
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'{token_type} {access_token}'
                }
                otp_response = req.post(otp_url, headers=headers, data=payload)

                if otp_response.status_code == 200:
                    otp_data = otp_response.json()
                    otp = otp_data.get('otp')

                    # Store OTP and expiry in session
                    request.session['device_otp'] = otp
                    request.session['otp_expiry'] = otp_expiry
                    request.session['psk_id'] = psk_id
                    messages.success(request, "OTP sent successfully to your email.")

                    # Send OTP data to the API
                    url = f"{API_STUDIO_URL}postapi/create/phpm02_user_device_02"
                    payload = json.dumps({
                        "data": {
                            "device_otp": otp,
                            "device_otp_duration": otp_expiry,
                            "member_id": member_id,
                            "user_id": psk_id
                        }
                    })
                    headers = {'Content-Type': 'application/json'}
                    response = req.post(url, headers=headers, data=payload)

                    if response.status_code == 200:
                        # Fetch new token for another API call
                        url = f"{API_STUDIO_URL}auth/token?secret_key=XGGtGlZWmRJR522VfO3RRhXHfdLtHJK3"
                        response = req.post(url)
                        ress_data = response.json()
                        access_token = ress_data.get('access_token')
                        token_type = ress_data.get('token_type')

                        print("A:", access_token)
                        print("B:", token_type)

                        # Call another API with the fetched token
                        url = f"{API_STUDIO_URL}coreapi/api/phpm0213"
                        payload = json.dumps({"data": {"user_id": psk_id}})
                        headers = {
                            'Content-Type': 'application/json',
                            'Authorization': f'{token_type} {access_token}'
                        }
                        response = req.post(url, headers=headers, data=payload)
                        user_data = response.json()
                        print(user_data)

                        if response.status_code == 200:
                            device_otp = user_data.get('data', {}).get('device_otp')
                            print("Device OTP:", device_otp)
                else:
                    messages.error(request, "Failed to send OTP. Please try again.")
            else:
                messages.error(request, "Failed to fetch access token.")
        else:
            messages.error(request, "Failed to fetch user data.")

        return render(request, "applicant_user_master/verification.html", {"id": id})

    elif request.method == "POST":
        # Retrieve stored OTP and validate
        device_otp = request.session.get('device_otp')
        otp1 = request.POST.get('otp1')
        otp2 = request.POST.get('otp2')
        otp3 = request.POST.get('otp3')
        otp4 = request.POST.get('otp4')
        user_otp = otp1 + otp2 + otp3 + otp4
        print(f"USER OTP: {user_otp}, Stored OTP: {device_otp}")

        if user_otp == device_otp:
            messages.success(request, "OTP verified successfully!")
            return redirect('loginpage')
        else:
            messages.error(request, "Incorrect OTP. Please try again.")

    return render(request, "applicant_user_master/verification.html", {"id": id})
