from django.urls import path
from .views import *

urlpatterns = [
    
        # path('',home, name="home"),
        path('inspection_officer/',inspection_officer, name="inspection_officer"),
        path('inspection_create',inspection_create, name="inspection_create"),
        path('nursing_inspection',nursing_inspection, name="nursing_inspection"),
        path('nursing_inspection_add',nursing_inspection_add, name="nursing_inspection_add"),
        path('anm_inspection',anm_inspection, name="anm_inspection"),
        path('anm_inspection_add',anm_inspection_add, name="anm_inspection_add"),
        path('mphw_inspection',mphw_inspection, name="mphw_inspection"),
        path('mphw_inspection_add',mphw_inspection_add, name="mphw_inspection_add"),
        path('dgnm_inspection_add',dgnm_inspection_add, name="dgnm_inspection_add"),
        path('mbbs_inspection_add',mbbs_inspection_add, name="mbbs_inspection_add"),
        path('final_report',final_report, name="final_report"),
        #dashboard for users 
        path('',admin_dashboard, name="admin_dashboard"),
         path('admin_dashboard',admin_dashboard, name="admin_dashboard"),
        path('hud_dashboard',hud_dashboard, name="hud_dashboard"),
        path('officer_dashboard',officer_dashboard, name="officer_dashboard"),
        path('statelevel_dashboard',statelevel_dashboard, name="statelevel_dashboard"),
        #state level status
        path('total_applicants',total_applicants, name="total_applicants"),
        path('approved_applicants',approved_applicants, name="approved_applicants"),
        path('pending_applicants',pending_applicants, name="pending_applicants"),
        path('waiting_inspections',waiting_inspections, name="waiting_inspections"),
        path('rejected_applicants',rejected_applicants, name="rejected_applicants"),
         path('waiting_approvals',waiting_approvals, name="waiting_approvals"),
        #hud level status
        path('hud_anm_status',hud_anm_status, name="hud_anm_status"),
        path('hud_dgnm_status',hud_dgnm_status, name="hud_dgnm_status"),
        path('hud_mbbs_status',hud_mbbs_status, name="hud_mbbs_status"),
        path('hud_nursing_status',hud_nursing_status, name="hud_nursing_status"),
        path('hud_mphw_status',hud_mphw_status, name="hud_mphw_status"),
        #officer level status
        path('officer_pending_list',officer_pending_list, name="officer_pending_list"),
        path('officer_progress_list',officer_progress_list, name="officer_progress_list"),
        path('officer_completed_list',officer_completed_list, name="officer_completed_list"),
        path('officer_rejected_list',officer_rejected_list, name="officer_rejected_list"),
        
        #admin dashboard 

          path('pending_application',pending_application, name="pending_application"),
          path('overall_application',overall_application, name="overall_application"),
          path('phc_list',phc_list, name="phc_list"),
          path('gh_list',gh_list, name="gh_list"),
          path('inspection_officer_list',inspection_officer_list, name="inspection_officer_list"),
          path('hud_list',hud_list, name="hud_list"),

        #application process 
          
      path('dho_app_progress',dho_app_progress, name="dho_app_progress"),
      path('hud_app_progress',hud_app_progress, name="hud_app_progress"),
      path('io_app_progress',io_app_progress, name="io_app_progress"),




]