from django.conf.urls import url
from django.shortcuts import resolve_url, reverse
from django.urls import path
from . import views
from django.contrib.auth.views import login, logout_then_login, LoginView, password_reset_done, LogoutView
from django.contrib.auth import views as auth_views


app_name = 'portal'


urlpatterns = [
    # url(r'^$', views.first_page, name='first_page'),
    url(r'^$', views.home, name='home'),
    url(r'^login/$', login, {'template_name': 'portal/login.html'},  name='login'),
    url(r'^register/$', views.register, name='register'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^update_profile/$', views.update_profile, name='update_profile'),
    # url(r'^logout/$', logout_then_login, name='logout'),
    url(r'^logout/$', LogoutView.as_view(template_name='portal/home.html'), name='logout'),
    url(r'^account_activation_sent/$', views.account_activation_sent, name='account_activation_sent'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),

    url(r'^job/details/(?P<pk>[0-9]+)/$', views.JobDetailView.as_view(), name='job_details'),
    url(r'^job/search/$', views.job_search, name='job_search'),
    # url(r'^job/search/$', FilterView.as_view(filterset_class=JobFilter, template_name='portal/job_search.html'), name='job_search'),

    url(r'^job/proposal/add/(?P<job_id>[0-9]+)/$', views.proposal_add, name='proposal_add'),
    url(r'^job/proposal/update/(?P<proposal_id>[0-9]+)/$', views.proposal_update, name='proposal_update'),
    url(r'^job/proposal/details/(?P<pk>[0-9]+)/$', views.ProposalDetailView.as_view(), name='proposal_details'),
    url(r'^job/proposal/delete/(?P<proposal_id>[0-9]+)/$', views.proposal_delete, name='proposal_delete'),
    url(r'^job/proposal/list/$', views.ProposalListView.as_view(), name='proposal_list'),

    url(r'^account/$', views.account, name='account'),
    url(r'^account/recharge/make/(?P<package_id>[0-9]+)/$', views.recharge_make, name='recharge_make'),

    url(r'^password/change/$', views.change_password, name='password_change'),

    url(r'^password/reset/$', auth_views.password_reset, {'post_reset_redirect': '/password/reset/done/'}, name='password_reset'),

    url(r'^password/reset/done/$', auth_views.password_reset_done, name='password_reset_done'),


    url(r'^password/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, {'post_reset_redirect': '/password/reset/complete/'}, name='password_reset_confirm'),
    url(r'^password/reset/complete/$', auth_views.password_reset_complete, name='password_reset_complete'),
]

