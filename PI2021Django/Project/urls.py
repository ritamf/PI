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
from django.conf import settings

urlpatterns = [

    path('', views.home_page, name="home_page"),
    path('query/', views.db_query_page, name="db_query_page"),
    path('insert/', views.db_insert_page, name="db_insert_page"),
    path('token/<str:token>', views.db_token_page, name="db_token_page"),
    path('recover_password/', views.recover_password_page, name="recover_password_page"),
    path('logout/', views.logout_page, name="logout_page"),
    
    path('register_user', views.register_user_page, name="register_user_page"),
    path('authenticate_user', views.authenticate_user_page, name="authenticate_user_page"),
    path('logout_user/<str:user_token>', views.logout_user_page, name="logout_user_page"),
    path('password_reset_request', views.password_reset_request, name="password_reset_request"),
    
    path('insert_into_db/<str:user_token>/<str:sensorid>', views.insert_into_db, name="insert_into_db"),
    path('query_db/<str:user_token>/<str:sensorid>', views.query_db, name="query_db"),
    path('get_all_attributes/<str:user_token>', views.get_all_attributes, name="get_all_attributes"),

    path('<str:user_token>/grafana', views.datasource_test, name="datasource_test"),
    path('<str:user_token>/grafana/search', views.datasource_search, name="datasource_available_search"),
    path('<str:user_token>/grafana/query', views.datasource_query, name="datasource_query"),
    path('<str:user_token>/grafana/annotations', views.datasource_annotations, name="datasource_annotations"),
    path('<str:user_token>/grafana/tag-keys', views.datasource_tagkeys, name="datasource_tagkeys"),
    path('<str:user_token>/grafana/tag-values', views.datasource_tagvalues, name="datasource_tagvalues"),
]