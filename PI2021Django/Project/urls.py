"""Project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path
from webapp import views

urlpatterns = [


    path('grafana/', views.datasource_test, name="datasource_test"),
    path('grafana/search', views.datasource_search, name="datasource_available_search"),
    path('grafana/query', views.datasource_query, name="datasource_query"),
    path('grafana/annotations', views.datasource_annotations, name="datasource_annotations"),

    path('sensors/', views.sensors_overview, name="sensors_overview"),
    path('sensors/list/', views.sensors_get, name="sensors_list"),
    path('sensors/detail/<str:key>/', views.sensors_get_one, name="sensors_detail"),
    path('sensors/create/', views.sensors_post, name="sensors_create"),
    # path('sensors/update/<str:key>/', views.sensors_update, name="sensors_update"),
    # path('sensors/delete/<str:key>/', views.sensors_delete, name="sensors_delete"),

    # path('products/', views.overview, name="overview"),
    # path('products/list/', views.get, name="list"),
    # path('products/detail/<str:key>/', views.get_one, name="detail"),
    # path('products/create/', views.post, name="create"),
    # path('products/create_list/', views.post_list, name="create"),
    # path('products/update/<str:key>/', views.update, name="update"),
    # path('products/delete/<str:key>/', views.delete, name="delete"),
]
