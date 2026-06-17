from django.urls import path
from . import views

urlpatterns = [
    path('login/',  views.login_view,  name='login'),
    path('signup/', views.signup,      name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('study/add/', views.study_create, name='study_add'),
    path('study/<slug:study_id>/edit/', views.study_update, name='study_edit'),
    path('study/<slug:study_id>/delete/', views.study_delete, name='study_delete'),
    path('study/<slug:study_id>/pdf/', views.pdf_proxy, name='pdf_proxy'),
    path('accounts/',               views.user_list,   name='user_list'),
    path('accounts/add/',           views.user_add,    name='user_add'),
    path('accounts/<int:user_id>/edit/',   views.user_edit,   name='user_edit'),
    path('accounts/<int:user_id>/delete/', views.user_delete, name='user_delete'),

    path('profile/update/',          views.profile_update,          name='profile_update'),
    path('profile/change-password/', views.profile_password_change, name='profile_password_change'),

    path('',                    views.home,       name='home'),
    path('repository/',         views.repository, name='repository'),
    path('viewer/<slug:study_id>/', views.viewer, name='viewer'),
    path('about/',              views.about,      name='about'),
    path('application/',        views.research_application, name='research_application'),
    path('applications/',       views.application_list,  name='application_list'),
    path('applications/<int:application_id>/<str:action>/', views.application_review, name='application_review'),
    path('my-applications/',    views.my_applications,   name='my_applications'),
    path('contact/',            views.contact,    name='contact'),
]