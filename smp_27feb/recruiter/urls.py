from django.conf.urls import url
from recruiter import views
from django.contrib.auth.views import login, logout_then_login, LoginView, LogoutView
from django.urls import reverse
from portal import views as portal_views


app_name = 'recruiter'

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    # url(r'^login/$', LoginView.as_view(template_name='recruiter/login.html'), name='login'),
    # url(r'^logout/$', logout_then_login, {'login_url': '/recruiter/login/'}, name='logout'),
    url(r'^logout/$', LogoutView.as_view(template_name='portal/home.html'), name='logout'),
    url(r'^login/$', LoginView.as_view(template_name='recruiter/login.html'), name='login'),
    url(r'^register/$', views.register, name='register'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^update_profile/$', views.update_profile, name='update_profile'),
    url(r'^account_activation_sent/$', views.account_activation_sent, name='account_activation_sent'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),

    url(r'^job/post/$', views.job_post, name='job_post'),
    url(r'^job/list/$', views.JobListView.as_view(), name='job_list'),
    url(r'^job/details/(?P<pk>[0-9]+)/$', views.JobDetailView.as_view(), name='job_details'),
    url(r'^job/update/(?P<job_id>[0-9]+)/$', views.job_update, name='job_update'),
    url(r'^job/delete/(?P<job_id>[0-9]+)/$', views.job_delete, name='job_delete'),

    url(r'^proposal/list/$', views.ProposalListView.as_view(), name='proposal_list'),
    url(r'^proposal/details/(?P<pk>[0-9]+)/$', views.ProposalDetailView.as_view(), name='proposal_details'),

    url(r'^candidate/search/$', views.candidate_search, name='candidate_search'),
    url(r'^candidate/details/(?P<pk>[0-9]+)/$', views.CandidateDetailView.as_view(), name='candidate_details'),

    url(r'^candidate/like/(?P<candidate_id>[0-9]+)/$', views.candidate_like, name='candidate_like'),
    url(r'^candidate/unlike/(?P<candidate_id>[0-9]+)/$', views.candidate_unlike, name='candidate_unlike'),
    url(r'^candidate/like/list/$', views.CandidateLikeListView.as_view(), name='candidate_like_list'),

    url(r'^account/$', views.account, name='account'),
    url(r'^account/recharge/make/(?P<package_id>[0-9]+)/$', views.recharge_make, name='recharge_make'),

    # url(r'^password/change/$', views.change_password, name='password_change'),
    url(r'^password/change/$', portal_views.change_password, name='password_change'),

]
