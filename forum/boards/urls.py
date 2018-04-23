from django.urls import path

from . import views

urlpatterns = \
    [
        path('', views.BoardListView.as_view(), name='home'),
        path('boards/<int:board_pk>/', views.TopicListView.as_view(), name='topic_list'),
        path('boards/<int:board_pk>/create/', views.TopicCreateView.as_view(), name='topic_create'),
        path('boards/<int:board_pk>/topics/<int:topic_pk>/delete/', views.TopicDeleteView.as_view(),
             name='topic_delete'),
        path('boards/<int:board_pk>/topics/<int:topic_pk>/', views.PostListView.as_view(), name='post_list'),
        path('boards/<int:board_pk>/topics/<int:topic_pk>/reply', views.PostCreateView.as_view(), name='reply_topic'),
        path('boards/<int:board_pk>/topics/<int:topic_pk>/posts/<int:post_pk>/update/', views.PostUpdateView.as_view(),
             name='post_update'),
        path('boards/<int:board_pk>/topics/<int:topic_pk>/posts/<int:post_pk>/delete/', views.PostCreateView.as_view(),
             name='post_delete'),
    ]
