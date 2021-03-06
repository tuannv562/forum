from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path('', views.UserListView.as_view(), name='list'),
    path('redirect/', views.UserRedirectView.as_view(), name='redirect'),
    path('search/', views.search_user, name='search'),
    path('update/<slug:username>/', views.UserUpdateView.as_view(), name='update'),
    path('<slug:username>/', views.UserDetailView.as_view(), name='detail'),

    # path('<slug:username>/update/', views.UserUpdateView.as_view(), name='update'),
]
