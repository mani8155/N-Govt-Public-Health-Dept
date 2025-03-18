from django.urls import path
from .views import *

urlpatterns = [
    
        # path('',home, name="home"),
        path('role_add/',role_add, name="role_add"),
        path('role_list/',role_list, name="role_list"),
        path('role_edit/',role_edit, name="role_edit"),
        path('inspection_officer/',inspection_officer, name="inspection_officer"),
        path('inspection_create',inspection_create, name="inspection_create"),
        path('nursing_inspection',nursing_inspection, name="nursing_inspection"),
        path('nursing_inspection_add',nursing_inspection_add, name="nursing_inspection_add"),
        path('anm_inspection',anm_inspection, name="anm_inspection"),
        path('anm_inspection_add',anm_inspection_add, name="anm_inspection_add"),
        path('mphw_inspection',mphw_inspection, name="mphw_inspection"),
        path('mphw_inspection_add',mphw_inspection_add, name="mphw_inspection_add"),
        path('final_report',final_report, name="final_report"),
        #dashboard for users 
        path('',admin_dashboard, name="admin_dashboard"),
        path('hud_dashboard',hud_dashboard, name="hud_dashboard"),
        path('officer_dashboard',officer_dashboard, name="officer_dashboard"),
        path('statelevel_dashboard',statelevel_dashboard, name="statelevel_dashboard"),
         path('dho_dashboard',dho_dashboard, name="dho_dashboard"),
        #state level status
        path('anm_status',anm_status, name="anm_status"),
        path('dgnm_status',dgnm_status, name="dgnm_status"),
        path('mbbs_status',mbbs_status, name="mbbs_status"),
        path('nursing_status',nursing_status, name="nursing_status"),
        path('mphw_status',mphw_status, name="mphw_status"),
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
        
        #viewapplication

        path('view_application',view_application, name="view_application"),

        #admin dashboard 

          path('view_application',view_application, name="view_application"),
          path('view_application',view_application, name="view_application"),
          path('view_application',view_application, name="view_application"),
          path('view_application',view_application, name="view_application"),
          path('view_application',view_application, name="view_application"),






]