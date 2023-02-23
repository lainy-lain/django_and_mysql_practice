from django.urls import path, include
from peopleInfo import views

urlpatterns = [
    path('', views.displayMain),
    path('addStudRecords/', views.addStudents),
    path('addProfRecords/', views.addProfessors),
    path('addCountyRecords/', views.addCounties),
    path('addCovidRecords/', views.addCovids),

]