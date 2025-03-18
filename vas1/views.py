from datetime import timedelta
import pytz


from . import institution
from .anm_institute import anm_update
from .applicant_user_master import *
from .dgmn_proforma import dgmn_update
from .institution import *
from .mbbs_proforma import ApplicationTableName, mbbspplication_update, get_file_psk_id
from .mphw_proforma import mphw_update
from .nursing_proforma import nursing_update

MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB in bytes


def application_navigation(request):
    return redirect('proforma_view')


def faqs(request):
    context = {"menu": "faqs"}
    return render(request, "help_faqs/faqs.html", context)


def help(request):
    context = {"menu": "helppage"}
    return render(request, "help_faqs/index.html", context)


def view_application(request, psk_id, course_type):

    if course_type == "MBBS":
        return mbbspplication_update(request, psk_id)
    elif course_type == "Nursing":
        return nursing_update(request, psk_id)
    elif course_type == "DGMN":
        return dgmn_update(request, psk_id)
    elif course_type == "ANM":
        return anm_update(request, psk_id)
    elif course_type == "MPHW(M)":
        return mphw_update(request, psk_id)

    # Default response if no condition matches
    return HttpResponse("Invalid course type", status=400)


def downloadapplication(request):
    saved_username = request.COOKIES.get('saved_username', None)
    applicant_data = get_applicant_user_data(request, username=saved_username)
    institution_id = applicant_data.get('institution_name')
    application_status_download = application_status_load_data(institution_id)

    course_master = institution.course_master_data_get()

    filtered_applications = [
        app for app in application_status_download
        if app.get('application_status') in ('Downloaded', 'Submitted', 'Draft')
    ]

    context = {"menu": "download", "application_status_download": filtered_applications, "course_master": course_master}
    return render(request, "applicant_menus/downloadpdf.html", context)


def view_uploaded_pdf(request, psk_id):
    media_existing_ids = institution.media_table_get_data(psk_id)
    media_psk_id = get_file_psk_id('application_upload_uid', media_existing_ids)
    uploaded_pdf_file = f"{API_STUDIO_URL}crudapp/view/media/phpm02_application_301_master_dc1_media/{media_psk_id}"
    return redirect(uploaded_pdf_file)


def uploaddocument(request):
    saved_username = request.COOKIES.get('saved_username', None)
    applicant_data = get_applicant_user_data(request, username=saved_username)
    institution_id = applicant_data.get('institution_name')
    application_status_upload_lists = application_status_load_data(institution_id)

    course_master = institution.course_master_data_get()

    filtered_applications = [
        app for app in application_status_upload_lists
        if app.get('application_status') in ('Downloaded', 'Uploaded')
    ]

    context = {"menu": "upload", "application_status_upload_lists": filtered_applications,
               "course_master": course_master}
    return render(request, "applicant_menus/uploaddocument.html", context)


def upload_pdf_save(request, psk_id):
    if request.method == "POST":
        upload_pdf_file = request.FILES.get('upload_pdf_file')

        if not upload_pdf_file:
            messages.error(request, "No file selected")
            return redirect('uploaddocument')

            # Check file size limit (2MB)
        if upload_pdf_file.size > MAX_FILE_SIZE:
            messages.error(request, "File size must be 2MB or less.")
            return redirect('uploaddocument')

        field = "application_upload_uid"

        url = f"{API_STUDIO_URL}crudapp/upload/media/{ApplicationTableName}_media"
        payload = {'parent_psk_id': str(psk_id)}

        files = {
            'media': (field, upload_pdf_file, upload_pdf_file.content_type)
        }

        headers = {}  # Include necessary headers like authentication tokens if required

        response = requests.post(url, headers=headers, data=payload, files=files)

        if response.status_code == 200:
            institution.work_flow_table_insert(request, psk_id, status="Uploaded")
            institution.application_status_update(psk_id, "Uploaded")

            messages.success(request, "Successfully Uploaded")
            return redirect('uploaddocument')
        else:
            messages.error(request, "Failed to upload document")
            return redirect('uploaddocument')


def statusapplication(request):
    saved_username = request.COOKIES.get('saved_username', None)
    applicant_data = get_applicant_user_data(request, username=saved_username)
    institution_id = applicant_data.get('institution_name')
    application_status_lists = application_status_load_data(institution_id)

    course_master = institution.course_master_data_get()

    filtered_applications = [
        app for app in application_status_lists
        if app.get('application_status') in 'Uploaded'
    ]

    context = {"menu": "status", "application_status_lists": filtered_applications,  "course_master": course_master}

    return render(request, "applicant_menus/statusapplication.html", context)


def tracking_application_status(request, psk_id):
    # Get the application and workflow data
    obj = application_id_data_get(psk_id)
    track_status_list = work_flow_table_id_pass_get_all_data(psk_id)

    date_cal = None
    upload_confirmed = None  # Initialize variable to hold the upload_confirmed value

    # Find the date when approval status is 'Uploaded'
    for track_obj in track_status_list:
        if track_obj['approval_status'] == 'Uploaded':
            date_cal = track_obj['due_on']
            upload_confirmed = track_obj['due_on']  # Get the upload_confirmed value
            break

    date_cal = datetime.strptime(date_cal, "%Y-%m-%d")

    # Get the current date in Kolkata timezone
    kolkata_tz = pytz.timezone('Asia/Kolkata')
    current_date = datetime.now(kolkata_tz)

    # Localize 'due_on' to Kolkata timezone
    date_cal = kolkata_tz.localize(date_cal)

    # Add 15 days to the due date
    expected_date = date_cal + timedelta(days=15)

    # Function to add ordinal suffix to the day
    def get_day_with_ordinal(day):
        if 10 <= day <= 20:  # Handle 11th to 19th
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
        return f"{day}{suffix}"

    # Format the expected date with the day suffix and month abbreviation
    expected_date_with_suffix = get_day_with_ordinal(expected_date.day)
    formatted_expected_date = expected_date.strftime(f"%a, {expected_date_with_suffix} %b %Y")

    # Format Chnage
    upload_confirmed_date = datetime.strptime(upload_confirmed, "%Y-%m-%d")
    expected_date_with_suffix = get_day_with_ordinal(upload_confirmed_date.day)
    upload_confirmed_format = expected_date.strftime(f"%a, {expected_date_with_suffix} %b %Y")

    date_difference = current_date - date_cal

    # Determine the 'days ago' message
    if date_difference.days == 0:
        days_ago = "Today"
    elif date_difference.days == 1:
        days_ago = "1 day ago"
    else:
        days_ago = f"{date_difference.days} days ago"

    check_final_order_status = check_work_flow_tbl_final_order(psk_id)

    context = {
        "final_order_status": check_final_order_status,
        "menu": "status",
        "obj": obj,
        "track_status_list": track_status_list,
        "days_ago": days_ago,
        "expected_date": formatted_expected_date,
        "upload_confirmed": upload_confirmed_format,  # Pass the upload_confirmed value to the context
    }

    # Return the rendered template with the context data
    return render(request, "applicant_menus/tracking_application_status.html", context)


def proforma_view(request):
    context = {"menu": "application"}
    return render(request, 'proforma/proforma.html', context)


def institution_profile(request):
    saved_username = request.COOKIES.get('saved_username', None)
    applicant_data = get_applicant_user_data(request, username=saved_username)
    institution_id = applicant_data.get('institution_name')
    institution_obj = institution_id_data_get(int(institution_id))

    institution_distirict_psk_id = institution_obj['institution_distirict_psk_id']
    institution_hud_psk_id = institution_obj['institution_hud_psk_id']
    institution_block_psk_id = institution_obj['institution_block_psk_id']

    contact_details_data = institution_obj['contact_details_text']
    convert_json = json.loads(contact_details_data)
    contact_data = convert_json['contact_details']

    district = district_id_data_get(institution_distirict_psk_id)
    hud = hud_id_data_get(institution_hud_psk_id)
    block = block_id_data_get(institution_block_psk_id)

    context = {"menu": "institution_profile", "obj": institution_obj, "district": district,
               "hud": hud,
               "block_obj": block,
               "contact_data": contact_data,
               }
    return render(request, "institution/institution_profile.html", context)
