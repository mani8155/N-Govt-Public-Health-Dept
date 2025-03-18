# views.py
from django.contrib.sites import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
import requests
import json
from datetime import datetime

# Read (List all districts)
def district_list(request):
    url = "https://api.apistudio.app/getapi/all_fields/phpm02_district_51/all"

    payload = ""
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code == 200:
        districts = response.json()
    else:
        districts = []


    return render(request, 'district_master/district_list.html', {'districts': districts})

def district_create(request):
    if request.method == 'POST':
        district_code = request.POST['district_code'].replace(" ", "")
        district_name = request.POST['district_name']
        district_address = request.POST['district_address']
        district_phone = request.POST['district_phone']
        district_fax = request.POST['district_fax']
        district_mobile = request.POST['district_mobile']
        district_contact_person = request.POST['district_contact_person']
        
        # Handle the 'active' field correctly: If 'active' is checked, set it to True
        active = request.POST.get('active') == 'on'  # 'on' if checked, otherwise False

        # Prepare the data to send in the API request
        url = "https://api.apistudio.app/postapi/create/phpm02_district_51"
        payload = json.dumps({"data": {
            "district_code": district_code,
            "district_name": district_name,
            "district_address": district_address,
            "district_phone": district_phone,
            "district_fax": district_fax,
            "district_mobile": district_mobile,
            "district_contact_person": district_contact_person,
            "active": active
        }})
        headers = {'Content-Type': 'application/json'}
        
        # Send the POST request
        response = requests.post(url, headers=headers, data=payload)
        
        # Handle response
        if response.status_code == 200:
            district_psk_id = response.json().get('psk_id')
            return redirect('district_list')  # Redirect on success
        else:
            # Handle error if the API request fails
            return render(request, 'district_master/district_create.html', {'error': 'Failed to create district.'})

    return render(request, 'district_master/district_create.html')



def district_update(request, district_id):
    # Fetch the current district details using GET request
    url = f"https://api.apistudio.app/getapi/phpm02_district_51/{district_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        district = response.json()  # Parse the JSON response
        print('success', district)
    else:
        return HttpResponse(f"Error fetching district details: {response.text}", status=500)

    # Handle form submission if method is POST
    if request.method == 'POST':
        # Prepare the URL for the PUT request (update)
        url = f"https://api.apistudio.app/updateapi/update/phpm02_district_51/{district_id}"

        # Handle 'active' correctly: check if it is checked or not
        active = request.POST.get('active') == 'on'  # If 'active' is checked, it will be 'on', else False

        # Prepare the payload with the POST data or the current district details if the form data is missing
        payload = json.dumps({
            "data": {
                "district_code": request.POST.get('district_code', district['district_code']).replace(" ", ""),
                "district_name": request.POST.get('district_name', district['district_name']),
                "district_address": request.POST.get('district_address', district['district_address']),
                "district_phone": request.POST.get('district_phone', district['district_phone']),
                "district_fax": request.POST.get('district_fax', district['district_fax']),
                "district_mobile": request.POST.get('district_mobile', district['district_mobile']),
                "district_contact_person": request.POST.get('district_contact_person', district['district_contact_person']),
                "active": active  # Use the active value from the form
            }
        })

        headers = {'Content-Type': 'application/json'}

        # Make the PUT request to update the district
        response = requests.request("PUT", url, headers=headers, data=payload)

        # Check for a successful response and redirect to the district list
        if response.status_code == 200:
            return redirect('district_list')  # Redirect to the district list page
        else:
            return HttpResponse(f"Error updating district: {response.text}", status=500)
    
    return render(request, 'district_master/district_update.html', {'district': district})



# Delete (Delete a district)
def district_delete(request, district_id):
    # if request.method == 'POST':
        url = f"https://api.apistudio.app/deleteapi/delete/phpm02_district_51/{district_id}"

        payload = ""
        headers = {}

        response = requests.request("DELETE", url, headers=headers, data=payload)
        return redirect('district_list')
    # return render(request, 'district_master/district_delete.html')

def hud_list_Master(request):
    # URL to fetch HUD data
    url = "https://api.apistudio.app/getapi/all_fields/phpm02_hud_52/all"

    payload = ""
    headers = {}

    # Sending GET request to fetch HUD data
    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code == 200:
        huds = response.json()
    else:
        huds = []  # Default empty list in case the request fails

    # URL to fetch district data
    district_url = "https://api.apistudio.app/getapi/all_fields/phpm02_district_51/all"
    district_response = requests.get(district_url, headers=headers, data=payload)

    if district_response.status_code == 200:
        district_data = district_response.json()
        # Create a dictionary mapping psk_id to district_name
        
        

    # Render the HUD list template with the district names and HUD data
    return render(request, 'hud_master/hud_list_Master.html', {'huds': huds, 'district_data': district_data})


def hud_create(request):
    
    # URL to fetch district data
    url = "https://api.apistudio.app/getapi/all_fields/phpm02_district_51/all"

    payload = ""
    headers = {}

    # Sending GET request to fetch district data
    response = requests.get(url, headers=headers, data=payload)


    # Process the district data from the API
    if response.status_code == 200:
        district_data = response.json()  # Get the list of districts
        
    # Handling the POST request when form is submitted
    if request.method == 'POST':
        # Get the selected district code from the form (not district_name)
        district_psk_id = request.POST['district_psk_id']  # Here, district_psk_id is the district code, not the name
        hud_code = request.POST['hud_code'].replace(" ", "")
        hud_name = request.POST['hud_name']
        hud_address = request.POST['hud_address']
        hud_phone = request.POST['hud_phone']
        hud_mobile = request.POST['hud_mobile']
        hud_contact_person = request.POST['hud_contact_person']
        
        # Handle the 'active' checkbox correctly
        active = request.POST.get('active') == 'on'  # 'on' if checked, otherwise False
        
        # Prepare the data to send in the API request
        url = "https://api.apistudio.app/postapi/create/phpm02_hud_52"
        payload = json.dumps({
            "data": {
                "district_psk_id": district_psk_id,  # The district_psk_id will be the code here
                "hud_code": hud_code,
                "hud_name": hud_name,
                "hud_address": hud_address,
                "hud_phone": hud_phone,
                "hud_mobile": hud_mobile,
                "hud_contact_person": hud_contact_person,
                "active": active
            }
        })
        
        headers = {'Content-Type': 'application/json'}
        
        # Send the POST request to create the new HUD
        response = requests.post(url, headers=headers, data=payload)
        
        # Handle the response from the API
        if response.status_code == 200:
            hud_psk_id = response.json().get('psk_id')
            return redirect('hud_list_Master')  # Redirect on success
        else:
            # If the request fails, render the form with an error message
            return render(request, 'hud_master/hud_create.html', {'error': 'Failed to create HUD.'})

    # Render the HUD create form with the district names as options
    return render(request, 'hud_master/hud_create.html', {'district_data': district_data})


def hud_update(request, hud_psk_id):
    # URL to fetch district data
    district_url = "https://api.apistudio.app/getapi/all_fields/phpm02_district_51/all"
    headers = {}

    # Sending GET request to fetch district data
    district_response = requests.get(district_url, headers=headers)

    if district_response.status_code == 200:
        district_data = district_response.json()  # Get the list of districts
    else:
        return HttpResponse(f"Error fetching district data: {district_response.text}", status=500)

    # URL to fetch the specific HUD data
    hud_url = f"https://api.apistudio.app/getapi/phpm02_hud_52/{hud_psk_id}"
    hud_response = requests.get(hud_url)

    if hud_response.status_code == 200:
        hud = hud_response.json()  # Parse the JSON response for the HUD details
        print('HUD Data:', hud)
    else:
        return HttpResponse(f"Error fetching HUD details: {hud_response.text}", status=500)

    # Handle form submission if method is POST
    if request.method == 'POST':
        # Prepare the URL for the PUT request (update HUD)
        url = f"https://api.apistudio.app/updateapi/update/phpm02_hud_52/{hud_psk_id}"

        # Handle 'active' correctly: check if it is checked or not
        active = request.POST.get('active') == 'on'  # If 'active' is checked, it will be 'on', else False

        # Prepare the payload with the POST data or the current hud details if the form data is missing
        payload = json.dumps({
            "data": {
                "district_psk_id": request.POST.get('district_psk_id', hud['district_psk_id']).replace(" ", ""),
                "hud_code": request.POST.get('hud_code', hud['hud_code']).replace(" ", ""),
                "hud_name": request.POST.get('hud_name', hud['hud_name']),
                "hud_address": request.POST.get('hud_address', hud['hud_address']),
                "hud_phone": request.POST.get('hud_phone', hud['hud_phone']),
                "hud_mobile": request.POST.get('hud_mobile', hud['hud_mobile']),
                "hud_contact_person": request.POST.get('hud_contact_person', hud['hud_contact_person']),
                "active": active  # Use the active value from the form
            }
        })

        headers = {'Content-Type': 'application/json'}

        # Make the PUT request to update the HUD
        response = requests.request("PUT", url, headers=headers, data=payload)

        # Check for a successful response and redirect to the HUD list
        if response.status_code == 200:
            return redirect('hud_list_Master')  # Redirect to the HUD list page
        else:
            return HttpResponse(f"Error updating HUD: {response.text}", status=500)

    # Render the HUD update page with district data and current HUD data
    return render(request, 'hud_master/hud_update.html', {'district_data': district_data, 'hud': hud})



# Delete (Delete a hud)
def hud_delete(request, hud_psk_id):
    
    # if request.method == 'POST':
        url = f"https://api.apistudio.app/deleteapi/delete/phpm02_hud_52/{hud_psk_id}"

        payload = ""
        headers = {}

        response = requests.request("DELETE", url, headers=headers, data=payload)
        return redirect('hud_list_Master')
    # return render(request, 'hud_delete.html')


# def user_menu(request):
#     return render(request, 'user_menus.html')


def block_list(request):
        
    url = "https://api.apistudio.app/getapi/all_fields/phpm02_hud_52/all"

    payload = ""
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    
    if response.status_code == 200:
        hud_data = response.json()
        print("hud_data:", hud_data)
    else:
        hud_data = []
        
    url = "https://api.apistudio.app/getapi/all_fields/phpm02_block_53/all"

    payload = ""
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    
    if response.status_code == 200:
        blocks = response.json()
    
    return render(request, 'block_master/block_list.html', {"blocks":blocks, "hud_data":hud_data})


def block_create(request):
    url = "https://api.apistudio.app/getapi/all_fields/phpm02_hud_52/all"

    payload = ""
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code == 200:
        huds_data = response.json()
    else:
        huds_data = []  # Default empty list in case the request fails
    if request.method =="POST":
        hud_psk_id = request.POST['hud_psk_id']
        block_code = request.POST['block_code'].replace(" ", "")
        block_name = request.POST['block_name']
        block_address = request.POST['block_address']
        block_phone = request.POST['block_phone']
        block_mobile = request.POST['block_mobile']
        block_contact_person = request.POST['block_contact_person']
        active = request.POST.get('active') == 'on'
        
        url = "https://api.apistudio.app/postapi/create/phpm02_block_53"

        payload = json.dumps({"data": {"hud_psk_id": hud_psk_id,"block_code": block_code,"block_name": block_name,"block_address": block_address,"block_phone": block_phone,"block_mobile": block_mobile,"block_contact_person": block_contact_person,"active": active}})
        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        
        if response.status_code == 200:
            bolck_psk_id = response.json().get('psk_id')
            return redirect('block_list')  # Redirect on success
        else:
            # If the request fails, render the form with an error message
            return render(request, 'block_master/block_create.html', {'error': 'Failed to create Block.'})        
    return render(request, 'block_master/block_create.html', {"huds_data": huds_data})


# Update (Edit an existing block)
def block_update(request, block_psk_id):
    url = "https://api.apistudio.app/getapi/all_fields/phpm02_hud_52/all"

    payload = ""
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    
    if response.status_code == 200:
        hud = response.json()
    else:
        return HttpResponse(f"Error fetching district data: {response.text}", status=500)
    
    url = f"https://api.apistudio.app/getapi/phpm02_block_53/{block_psk_id}"

    payload = ""
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    
    if response.status_code == 200:
        block_data = response.json()
        print("block", block_data)
    else:
        return HttpResponse(f"Error fetching Block details: {response.text}", status=500)
    
    if request.method == "POST":    
        url = f"https://api.apistudio.app/updateapi/update/phpm02_block_53/{block_psk_id}"
        
        active = request.POST.get('active') == 'on'  # If 'active' is checked, it will be 'on', else False

        # Prepare the payload with the POST data or the current hud details if the form data is missing
        payload = json.dumps({"data": {"hud_psk_id": request.POST.get('hud_psk_id', block_data['hud_psk_id']),"block_code": request.POST.get('block_code', block_data['block_code']).replace(" ", ""),"block_name": request.POST.get('block_name', block_data['block_name']),"block_address": request.POST.get('block_address', block_data['block_address']),"block_contact_person": request.POST.get('block_contact_person', block_data['block_contact_person']),"block_phone": request.POST.get('block_phone', block_data['block_phone']),"block_mobile": request.POST.get('block_mobile', block_data['block_mobile']),"active": active}})
        headers = {'Content-Type': 'application/json'}

        response = requests.request("PUT", url, headers=headers, data=payload)
        
        if response.status_code == 200:
            return redirect('block_list')  # Redirect to the HUD list page
        else:
            return HttpResponse(f"Error updating Block: {response.text}", status=500) 
    
    return render(request, 'block_master/block_update.html', {"huds":hud, "block_data": block_data})


# Delete (Delete a block)
def block_delete(request, block_psk_id):
    # if request.method == "POST":
        url = f"https://api.apistudio.app/deleteapi/delete/phpm02_block_53/{block_psk_id}"

        payload = ""
        headers = {}

        response = requests.request("DELETE", url, headers=headers, data=payload)
        return redirect('block_list')
    # return render(request, 'block_master/block_delete.html')


def phc_list_Master(request):
        
    url = "https://api.apistudio.app/getapi/all_fields/phpm02_block_53/all"

    payload = ""
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    
    if response.status_code == 200:
        block_data = response.json()
        print("block_data:", block_data)
    else:
        block_data = []
        
    url = "https://api.apistudio.app/getapi/all_fields/phpm02_phc_54/all"

    payload = ""
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    
    if response.status_code == 200:
        phc_list_Master = response.json()
        
    return render(request, 'phc_master/phc_list_Master.html', {"phc_list_Master":phc_list_Master, "block_data":block_data})


def phc_create(request):
    url = "https://api.apistudio.app/getapi/all_fields/phpm02_block_53/all"

    payload = ""
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    
    if response.status_code == 200:
        block_data = response.json()
        print("block_data:", block_data)
    else:
        block_data = []
        
    if request.method =="POST":
        block_psk_id = request.POST['block_psk_id']
        phc_code = request.POST['phc_code'].replace(" ", "")
        phc_name = request.POST['phc_name']
        phc_address = request.POST['phc_address']
        phc_phone = request.POST['phc_phone']
        phc_mobile = request.POST['phc_mobile']
        phc_contact_person = request.POST['phc_contact_person']
        active = request.POST.get('active') == 'on'
        
        url = "https://api.apistudio.app/postapi/create/phpm02_phc_54"

        payload = json.dumps({"data": {
                "block_psk_id": block_psk_id,
                "phc_code": phc_code,
                "phc_name": phc_name,
                "phc_address": phc_address,
                "phc_phone": phc_phone,
                "phc_mobile": phc_mobile,
                "phc_contact_person": phc_contact_person,
                "active": active}})
        headers = {'Content-Type': 'application/json'}
        response = requests.request("POST", url, headers=headers, data=payload)
        
        if response.status_code == 200:
            phc_psk_id = response.json().get('psk_id')
            return redirect('phc_list_Master')
        else:
            return render(request, 'phc_master/phc_create.html', {'error': 'Failed to create PHC.'})        
    return render(request, 'phc_master/phc_create.html', {"block_data":block_data})


# Update (Edit an existing phc)
def phc_update(request, phc_psk_id):
    
    url = "https://api.apistudio.app/getapi/all_fields/phpm02_block_53/all"

    payload = ""
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    
    if response.status_code == 200:
        block_data = response.json()
        print("block_data:", block_data)
    else:
        return HttpResponse(f"Error fetching Block details: {response.text}", status=500)
    
    url = f"https://api.apistudio.app/getapi/phpm02_phc_54/{phc_psk_id}"

    payload = ""
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    
    if response.status_code == 200:
        phc_data = response.json()
        print("phc_data:", phc_data)
    else:
        return HttpResponse(f"Error fetching PHC details: {response.text}", status=500)
    
    if request.method == 'POST':
        
        url = f"https://api.apistudio.app/updateapi/update/phpm02_phc_54/{phc_psk_id}"
        
        active = request.POST.get('active') == 'on'

        payload = json.dumps({
        "data": {
        "block_psk_id": request.POST.get('block_psk_id', phc_data['block_psk_id']),
        "phc_code": request.POST.get('phc_code', phc_data['phc_code']).replace(" ", ""), 
        "phc_name": request.POST.get('phc_name', phc_data['phc_name']),
        "phc_address": request.POST.get('phc_address', phc_data['phc_address']),
        "phc_phone": request.POST.get('phc_phone', phc_data['phc_phone']),
        "phc_mobile": request.POST.get('phc_mobile', phc_data['phc_mobile']),
        "phc_contact_person": request.POST.get('phc_contact_person', phc_data['phc_contact_person']),
        "active": active
        }
        })

        headers = {'Content-Type': 'application/json'}

        response = requests.request("PUT", url, headers=headers, data=payload)
        
        if response.status_code == 200:
            return redirect('phc_list_Master')  # Redirect to the HUD list page
        else:
            return HttpResponse(f"Error updating PHC: {response.text}", status=500)
    return render(request, 'phc_master/phc_update.html', {"block_data": block_data, "phc_data":phc_data})


# Delete (Delete a phc)
def phc_delete(request, phc_psk_id):
    url = f"https://api.apistudio.app/deleteapi/delete/phpm02_phc_54/{phc_psk_id}"

    payload = ""
    headers = {}

    response = requests.request("DELETE", url, headers=headers, data=payload)
    return redirect('phc_list_Master')
    
    # return render(request, 'phc_delete.html')
    
    
def holiday_list(request):
    url = "https://api.apistudio.app/getapi/all_fields/phpm02_holiday_56/all"

    payload = ""
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code == 200:
        holiday = response.json()
    else:
        holiday = []
        
    
    return render(request, 'holiday_master/holiday_list.html', {"holidays":holiday})


def holiday_create(request):
    # Fetch the current year for default selection
    calendar_year = datetime.now().year
        
    if request.method == "POST":
        print(request.POST)  # Check the POST data for debugging
        holiday_name = request.POST.get('holiday_name')
        holiday_type = request.POST.get('holiday_type')
        holiday_date = request.POST.get('holiday_date')
        active = request.POST.get('active') == 'on'
        
        # selected_week_off = request.POST.getlist('week_off')
        # week_off = ', '.join(selected_week_off) if selected_week_off else ''
        
        # Ensure you re-use the same calendar_year and week_off on successful creation
        url = "https://api.apistudio.app/postapi/create/phpm02_holiday_56"
        
        # Create payload with form data
        payload = json.dumps({"data": {"holiday_name": holiday_name,"holiday_type": holiday_type,"holiday_date": holiday_date,"active": active}})
        headers = {'Content-Type': 'application/json'}
        response = requests.request("POST", url, headers=headers, data=payload)
        
        if response.status_code == 200:
            # Redirect to 'holiday_create' to refresh the page and show the newly created holiday
            return redirect('holiday_list')
        else:
            return render(request, 'holiday_master/holiday_create.html', {'error': 'Failed to create holiday.'})
    
    url = "https://api.apistudio.app/getapi/all_fields/phpm02_holiday_56/all"
    response = requests.get(url)
    if response.status_code == 200:
        holiday_data = response.json()
    else:
        holiday_data = []

    return render(request, 'holiday_master/holiday_create.html', {'holidays': holiday_data})



# Update (Edit an existing holiday)
def holiday_update(request, holiday_psk_id):
    url = f"https://api.apistudio.app/getapi/phpm02_holiday_56/{holiday_psk_id}"

    payload = ""
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        holiday_update = response.json()
        print("holiday_update:", holiday_update)
        # Ensure week_off is split correctly if present
        # selected_week_off = holiday_update.get('week_off', '').split(', ') if holiday_update.get('week_off') else []
    else:
        return HttpResponse(f"Error fetching Holiday details: {response.text}", status=500)
    
    if request.method == "POST":
        # Handle selected week_off values correctly from the form
        # selected_week_off = ', '.join(request.POST.getlist('week_off'))  # Join selected days into a string

        active = request.POST.get('active') == 'on'
        
        payload = json.dumps({
            "data": {
                # "calendar_year": request.POST.get('calendar_year', holiday_update['calendar_year']),
                # "week_off": selected_week_off,  # Pass selected week_off as comma-separated string
                "holiday_type": request.POST.get('holiday_type', holiday_update['holiday_type']),
                "holiday_name": request.POST.get('holiday_name', holiday_update['holiday_name']),
                "holiday_date": request.POST.get('holiday_date', holiday_update['holiday_date']),
                "active": active
            }
        })

        url = f"https://api.apistudio.app/updateapi/update/phpm02_holiday_56/{holiday_psk_id}"
        headers = {'Content-Type': 'application/json'}

        response = requests.request("PUT", url, headers=headers, data=payload)
        
        if response.status_code == 200:
            return redirect('holiday_list')  # Redirect to the holiday list page
        else:
            return HttpResponse(f"Error updating holiday: {response.text}", status=500)

    return render(request, 'holiday_master/holiday_update.html', {"holiday": holiday_update})



# Delete (Delete a holiday)
def holiday_delete(request, holiday_psk_id):
    url = f"https://api.apistudio.app/deleteapi/delete/phpm02_holiday_56/{holiday_psk_id}"

    payload = ""
    headers = {}

    response = requests.request("DELETE", url, headers=headers, data=payload)
    return redirect('holiday_list')
    
    
    # return render(request, 'holiday_delete.html')




def course_list(request):
    return render(request, 'course_list.html')


