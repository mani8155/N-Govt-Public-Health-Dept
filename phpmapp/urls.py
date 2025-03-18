from django.urls import path
from .tieup_bh import *
from .tieup_ram import *
from .inspection_master import *
from .admin_insitution import *

urlpatterns = [
    path('',user_menu, name="user_menu"),
    path('phpm_create/', phpm_create, name="phpm_create"),
    path('phpm_company_list/', phpm_company_list, name="phpm_company_list"),
    path('phpm_update_company/<int:psk_id>/', phpm_update_company, name="phpm_update_company"),
    path('phpm_delete_company/<int:psk_id>/', phpm_delete_company, name="phpm_delete_company"),

    path('phpm_course_list/', phpm_course_list, name="phpm_course_list"),
    path('phpm_company_create/', phpm_company_create, name="phpm_company_create"),
    path('phpm_update_course/<int:psk_id>/', phpm_update_course, name="phpm_update_course"),
    path('phpm_delete_course/<int:psk_id>/', phpm_delete_course, name="phpm_delete_course"),

    path('institution_list_view/', institution_list_view, name="institution_list_view"),
    path('admin_create_institution/', admin_create_institution, name="admin_create_institution"),
    path('admin_update_institution/<int:psk_id>/', admin_update_institution, name="admin_update_institution"),
    # path('phpm_instituion_update/<int:psk_id>/', phpm_instituion_update, name="phpm_instituion_update"),
    # path('phpm_instituion_delete/<int:psk_id>/', phpm_instituion_delete, name="phpm_instituion_delete"),


    # mani

    path('phpm_Inspection_create/', phpm_Inspection_create, name="phpm_Inspection_create"),
    path('phpm_Inspection_update/<int:psk_id>/', phpm_Inspection_update, name="phpm_Inspection_update"),
    path('ajax_hud_designation/', ajax_hud_designation, name="ajax_hud_designation"),
    path('phpm_Inspection_list/', phpm_Inspection_list, name="phpm_Inspection_list"),
    path('phpm_Inspection_delete/<int:psk_id>/', phpm_Inspection_delete, name="phpm_Inspection_delete"),


    # Ram

    path('district_list/', district_list, name='district_list'),
    path('district/create/', district_create, name='district_create'),
    path('district/update/<int:district_id>/', district_update, name='district_update'),
    path('district/delete/<int:district_id>/', district_delete, name='district_delete'),

    path('hud_list_Master/', hud_list_Master, name='hud_list_Master'),
    path('hud/create/', hud_create, name='hud_create'),
    path('hud/update/<int:hud_psk_id>/', hud_update, name='hud_update'),
    path('hud/delete/<int:hud_psk_id>/', hud_delete, name='hud_delete'),

    path('block_list/', block_list, name='block_list'),
    path('block/create/', block_create, name='block_create'),
    path('block/update/<int:block_psk_id>/', block_update, name='block_update'),
    path('block/delete/<int:block_psk_id>/', block_delete, name='block_delete'),

    path('phc_list_Master/', phc_list_Master, name='phc_list_Master'),
    path('phc/create/', phc_create, name='phc_create'),
    path('phc/update/<int:phc_psk_id>/', phc_update, name='phc_update'),
    path('phc/delete/<int:phc_psk_id>/', phc_delete, name='phc_delete'),

    path('holiday_list/', holiday_list, name='holiday_list'),
    path('holiday/create/', holiday_create, name='holiday_create'),
    path('holiday/update/<int:holiday_psk_id>/', holiday_update, name='holiday_update'),
    path('holiday/delete/<int:holiday_psk_id>/', holiday_delete, name='holiday_delete'),

]
