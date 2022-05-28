from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Case, When
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import ListView, DetailView

from movies.models import Movie, Rating, WatchList
from movies.utils.recommendation import get_recommended_movies


class HomePageView(ListView):
    model = Movie
    template_name = 'list.html'
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return self.model.objects.filter(Q(title__icontains=query)).distinct()
        return self.model.objects.all()


class MovieDetailView(LoginRequiredMixin, DetailView):
    model = Movie
    movie_rating_model = Rating
    template_name = 'movies/detail.html'

    def get_current_user_movie_rating(self):
        try:
            return self.movie_rating_model.objects.get(
                user=self.request.user, movie=self.get_object()
            ).rating
        except self.movie_rating_model.DoesNotExist:
            return 0

    def get_user_watchlist(self):
        try:
            return WatchList.objects.get(user=self.request.user, movie=self.get_object())
        except WatchList.DoesNotExist:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movie_rating'] = self.get_current_user_movie_rating()
        context['watchlist'] = self.get_user_watchlist()

        return context

    def post(self, request, *args, **kwargs):
        if 'rating_btn' in request.POST:
            rating_value = request.POST.get('rating')
            rating_user, _ = self.movie_rating_model.objects.get_or_create(user=request.user, movie=self.get_object())

            rating_user.rating = float(rating_value)
            rating_user.save()
            messages.success(request, "Rating has been submitted!")

        if 'watch' in request.POST:
            watch_value = request.POST.get('watch')

            if watch_value == 'add':
                watchlist_user, _ = WatchList.objects.get_or_create(user=request.user, movie=self.get_object())
                watchlist_user.is_watched = True
                watchlist_user.save()
                messages.success(request, "Movie added to your list!")
            elif watch_value == 'remove':
                watchlist_user, _ = WatchList.objects.get_or_create(user=request.user, movie=self.get_object())
                watchlist_user.delete()
                messages.success(request, "Movie removed from your list!")

        return HttpResponseRedirect(self.get_object().get_absolute_url())


class WatchListView(ListView):
    model = WatchList
    template_name = 'movies/watch.html'

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user).select_related('movie')


class RecommendView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'movies/recommend.html'
    model = Movie
    rating_model = Rating

    def test_func(self):
        return self.rating_model.objects.filter(user=self.request.user).exists()

    def get_permission_denied_message(self):
        ERROR_STRING = "You haven't rated any movies"
        return ERROR_STRING

    def handle_no_permission(self):
        if self.raise_exception or self.request.user.is_authenticated:
            messages.error(self.request, message=self.get_permission_denied_message())
            return render(self.request, self.template_name)
        return super().handle_no_permission()

    def get_queryset(self):
        return get_recommended_movies(self.request.user.pk)
