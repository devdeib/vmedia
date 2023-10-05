from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import views as auth_views
from . import views

app_name = 'vapp'

urlpatterns = [
    path('', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('feed/', views.post_list, name='post_list'),
    path('change_password/', views.change_password, name="change_password"),
    path('edit_profile/', views.profile_edit, name="edit_profile"),
    path('delete_photo/', views.delete_photo, name="delete_photo"),
    path('profile/', views.profile_view, name='profile'),  # Use profile_view instead of profile
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail, name='post_detail'),
    path('create_post/', views.create_post, name="create_post"),
    path('<int:post_id>/share/', views.post_share, name='post_share'),
    path('search/', views.search, name='search'),
    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('login/', views.login, name='login'),
    path('<int:post_id>/comment/', views.post_comment, name='post_comment'), 
    path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]   