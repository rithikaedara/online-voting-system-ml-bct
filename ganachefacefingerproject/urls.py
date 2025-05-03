"""
URL configuration for ganachefacefingerproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from adminapp import views as admin_views
from userapp import views as user_views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path('',user_views.index,name="index"),
    path('contact',user_views.contact,name="contact"),
    path('voter/elections/',user_views.elections,name="elections"),
    path('voter/candidates/<int:id>/',user_views.candidates,name="candidates"),
    path('voter/results/',user_views.results,name="results"),
    path('voter/admin-login/',user_views.admin_login,name="admin_login"),
    path('voter/voting-page/<int:id>/',user_views.voting_page,name="voting_page"),
    path('vote-otp/<int:id>/<int:cand_id>',user_views.voter_otp,name='voter_otp'),
    path('finger-print-verification/<int:id>/<int:cand_id>/', user_views.fingerprint, name='fingerprint'),
    path('cast-vote/<int:id>/<int:cand_id>',user_views.cast_vote,name='cast_vote'),
    path('voter-results',user_views.voter_results,name='voter_results'),
    path('voter-view-result/<int:id>',user_views.voter_verify_results,name='voter_verify_results'),
    path('predict/', user_views.predict_election, name='predict_election'),






    ### admin views

    path('dashboard',admin_views.admin_dashboard, name='admin_dashboard'),
    path('add-election',admin_views.admin_add_election,name='admin_add_election'),
    path('add-candidate',admin_views.admin_add_candidates,name='admin_add_candidates'),
    path('results',admin_views.admin_results,name='admin_results'),
    path('view-elections',admin_views.admin_view_elections,name='admin_view_elections'),
    path('view-candidates/<int:id>',admin_views.admin_view_candidates,name='admin_view_candidates'),
    path('verify-results/<int:id>',admin_views.verify_results,name='verify_results'),
    path('add-voters/',admin_views.add_voters,name='add_voters'),
    path("upload/", admin_views.upload_csv, name="upload_csv"),

    path('manage-voters/',admin_views.manage_voters,name='manage_voters'),
    path('remove-voter/<int:voter_id>/', admin_views.remove_voter, name='remove_voter'),

]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)