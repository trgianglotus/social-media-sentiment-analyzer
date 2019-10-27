"""stress_detecting_application URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path, include
from django.contrib.auth import views as auth_views
from dashboard.views import (
    FilteredStudentListView,
    student_detail,
    login,
    load_student,
    redirect_twitter,
    delete_student,
    add_student,
    ChartData,
    ChartDataDetail,
    LineChartJSONView,
    line_chart_json,
    line_chart,
    all_students,
    search_student,
    classboard_test,
    check_phone,
    enter_phone,
    enter_email,
    update_receive_m,
    update_receive_e,
    enter_days,
    incoming_message,
    alert_message,
    auto_report,
    start_server,
    # PollDetail,
    # call_response

)

urlpatterns = [
    path('_', classboard_test, name='testing'),
    path('', all_students, name='all-students'),
    path('search/', search_student, name='search-student'),
    path('save_phone/', enter_phone, name='enter-phone'),
    path('save_email/', enter_email, name='enter-email'),
    path('save_days/', enter_days, name='enter-days'),
    path('receive_email/', update_receive_e, name='receive-email'),
    path('receive_phone/', update_receive_m, name='receive-message'),
    path('api/chart/data/', ChartData.as_view()),
    path('api/chart/data/<int:pk>', ChartDataDetail.as_view()),
    path('incoming_message/', incoming_message, name='incoming-message'),
    # path('call_response/', call_response, name='call-response'),
    # path("polls/<int:pk>/", PollDetail.as_view(), name="polls_detail"),
    path('alert-message/', alert_message, name='alert-message'),
    path('start_server/', start_server, name='start-server'),


    path('phone_number/', check_phone, name='check-phone'),
    path('student/<int:pk>/', student_detail, name='student-detail'),
    path('student/delete/<int:pk>/', delete_student, name='delete-student'),
    path('student/add/', add_student, name='add-student'),
    path('redirect_twitter/<str:account>/', redirect_twitter, name='redirect-twitter'),
    path('load/', load_student, name='load-student'),
    path('login/', login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('api-auth/', ChartData.as_view()),
    path('admin/', admin.site.urls),
    path('linechart/', line_chart),
    path('line_chart_json/', line_chart_json, name='line_chart_json')
]
