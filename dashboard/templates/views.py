from django.shortcuts import render, redirect
from django.http import HttpResponse



def home(request):
    return render(request,'test.html')

def inspection_officer(request):
    return render(request , 'inspection_officer/index.html')

def inspection_create(request):
    return render(request , 'inspection_officer/create.html')

def nursing_inspection(request):
    return render(request , 'nursing_inspection/index.html')

def nursing_inspection_add(request):
    return render(request , 'nursing_inspection/nursing_inspection_add.html')

def dgnm_inspection_add(request):
    return render(request , 'dgnm_inspection_add.html')

def mbbs_inspection_add(request):
    return render(request , 'mbbs_inspection_add.html')


def anm_inspection(request):
    return render(request , 'anm_inspection/index.html')

def anm_inspection_add(request):
    return render(request , 'anm_inspection/anm_inspection_add.html')

def mphw_inspection(request):
    return render(request , 'mphw_inspection/index.html')

def mphw_inspection_add(request):
    return render(request , 'mphw_inspection/mphw_inspection_add.html')

def final_report(request):
    return render(request , 'final_report.html')

def admin_dashboard(request):
    return render(request , 'dashboard/admin_dashboard.html')

def hud_dashboard(request):
    return render(request , 'dashboard/hud_dashboard.html')

def officer_dashboard(request):
    return render(request , 'dashboard/officer_dashboard.html')

def statelevel_dashboard(request):
    return render(request , 'dashboard/statelevel_dashboard.html')


#status for statelevel Dashboard 

def total_applicants(request):
    return render(request , 'statelevel_status/total_applicants.html')

def approved_applicants(request):
    return render(request , 'statelevel_status/approved_applicants.html')

def pending_applicants(request):
    return render(request , 'statelevel_status/pending_applicants.html')

def waiting_inspections(request):
    return render(request , 'statelevel_status/waiting_inspections.html')

def rejected_applicants(request):
    return render(request , 'statelevel_status/rejected_applicants.html')

def waiting_approvals(request):
    return render(request , 'statelevel_status/waiting_approvals.html')

#status for HUDlevel Dashboard

def hud_anm_status(request):
    return render(request , 'hudlevel_status/anm_status.html')

def hud_dgnm_status(request):
    return render(request , 'hudlevel_status/dgnm_status.html')

def hud_mbbs_status(request):
    return render(request , 'hudlevel_status/mbbs_status.html')

def hud_nursing_status(request):
    return render(request , 'hudlevel_status/nursing_status.html')

def hud_mphw_status(request):
    return render(request , 'hudlevel_status/mphw_status.html')

#status for Officerlevel Dashboard 

def officer_pending_list(request):

    return render(request , 'officer_status/officer_pending_list.html')

def officer_progress_list(request):
    return render(request , 'officer_status/officer_progress_list.html')

def officer_completed_list(request):
    return render(request , 'officer_status/officer_completed_list.html')

def officer_rejected_list(request):
    return render(request , 'officer_status/officer_rejected_list.html')


def pending_application(request):
    
    return render(request , 'admin_officer/pending_application.html')

def overall_application(request):
    
    return render(request , 'admin_officer/overall_application.html')

def phc_list(request):
    
    return render(request , 'admin_officer/phc_list.html')

def hud_list(request):

    return render(request , 'admin_officer/hud_list.html')

def gh_list(request):
    
    return render(request , 'admin_officer/gh_list.html')

def inspection_officer_list(request):
    
    return render(request , 'admin_officer/inspection_officer.html')

def dho_app_progress(request):
    
    return render(request , 'application_process/dho_app_progress.html')

def hud_app_progress(request):
    
    return render(request , 'application_process/hud_app_progress.html')

def io_app_progress(request):
    
    return render(request , 'application_process/io_app_progress.html')


