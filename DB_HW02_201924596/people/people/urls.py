from django.urls import path, include
from peopleInfo import views

urlpatterns = [
    path('', views.displayMain, name='main'),
    path('peopleInfo/', include('peopleInfo.urls')),

]