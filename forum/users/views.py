from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView

from .forms import SearchUserForm
from .models import User


class UserListView(LoginRequiredMixin, ListView):
    model = User
    context_object_name = 'users'
    template_name = 'users/list.html'
    paginate_by = 50

    def get_queryset(self):
        queryset = User.objects.all().order_by('date_joined')
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        kwargs['form'] = SearchUserForm
        return super().get_context_data(**kwargs)
    # These next two lines tell the view to index lookups by username
    # slug_field = "username"
    # slug_url_kwarg = "username"


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = "username"
    slug_url_kwarg = "username"
    template_name = 'users/detail.html'
    context_object_name = 'user'


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})


class UserUpdateView(LoginRequiredMixin, UpdateView):
    # we already imported User in the view code above, remember?
    model = User
    fields = ('avatar', 'first_name', 'last_name', 'gender', 'date_of_birth', 'local_timezone', 'bio')
    slug_url_kwarg = 'username'
    template_name = 'users/update.html'

    # send the user back to their own page after a successful update

    def get_success_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})

    def get_object(self):
        # Only get the User record for the user making the request
        return User.objects.get(username=self.request.user.username)


def search_user(request):
    if request.method == 'GET':
        users = User.objects.filter(username__icontains=request.GET.get('username'))
    else:
        users = User.objects.filter(username__icontains=request.POST.get('username'))
    return render(request, 'users/list.html', context={'users': users, 'form': SearchUserForm})
