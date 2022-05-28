from django.urls import path

from movies import views

app_name = 'movies'

urlpatterns = [
    path('', views.HomePageView.as_view(), name='index'),
    path('<int:pk>/', views.MovieDetailView.as_view(), name='movie_detail'),
    path('watchlist/', views.WatchListView.as_view(), name='movie_watchlist'),
    path('recommend/', views.RecommendView.as_view(), name='recommend_movies'),
]
