from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),  
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", views.signup_view, name="signup"),
path("delete-box/<int:box_id>/", views.delete_box_view, name="delete-box"),

    path("set-warehouse/", views.set_warehouse_view, name="set-warehouse"),
    path("warehouse/current/", views.current_warehouse_view, name="current-warehouse"),
    path("add-box/", views.add_box_view, name="add-box"),
    path("upload-csv/", views.upload_csv_view, name="upload-csv"),
    path("organize/", views.organize_view, name="organize"),
]
