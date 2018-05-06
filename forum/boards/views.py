from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic

from . import models
from .forms import NewTopicForm, NewPostForm


# Create your views here.

class BoardListView(generic.ListView):
    model = models.Board
    template_name = 'boards/home.html'
    context_object_name = 'boards'


class TopicListView(generic.ListView):
    model = models.Topic
    template_name = 'boards/topic_list.html'
    context_object_name = 'topics'
    paginate_by = 20

    def get_queryset(self):
        self.board = get_object_or_404(models.Board, pk=self.kwargs.get('board_pk'))
        queryset = self.board.topics.order_by('-last_updated_at').annotate(replies=Count('posts') - 1)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        kwargs['board'] = self.board
        return super().get_context_data(**kwargs)


class TopicCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.Topic
    template_name = 'boards/topic_create.html'
    form_class = NewTopicForm
    pk_url_kwarg = 'board_pk'

    def get_context_data(self, **kwargs):
        kwargs['board'] = get_object_or_404(models.Board, pk=self.kwargs.get('board_pk'))
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        return reverse_lazy('topic_list', kwargs={'board_pk': self.kwargs.get('board_pk')})

    def form_valid(self, form):
        user = self.request.user
        board = get_object_or_404(models.Board, pk=self.kwargs.get('board_pk'))
        form.instance.created_by = user
        form.instance.last_updated_by = user
        form.instance.board = board
        topic = form.save()
        models.Post.objects.create(message=form.cleaned_data.get('message'),
                                   topic=topic,
                                   created_by=user,
                                   last_updated_by=user)
        return HttpResponseRedirect(self.get_success_url())


class TopicUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.Topic
    fields = ('subject',)
    pk_url_kwarg = 'topic_pk'
    template_name = 'boards/topic_update.html'

    def get_queryset(self):
        queryset = models.Topic.objects.filter(pk=self.kwargs.get('topic_pk'),
                                               board__pk=self.kwargs.get('board_pk'),
                                               created_by=self.request.user)
        return queryset

    def get_success_url(self):
        return reverse_lazy('topic_list', kwargs={'board_pk': self.kwargs.get('board_pk')})

    def form_valid(self, form):
        topic = form.instance
        topic.last_updated_by = self.request.user
        topic.last_updated_at = timezone.now()
        topic.save()
        return HttpResponseRedirect(self.get_success_url())


class TopicDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = models.Topic
    pk_url_kwarg = 'topic_pk'
    template_name = 'boards/topic_confirm_delete.html'

    def get_queryset(self):
        queryset = models.Topic.objects.filter(pk=self.kwargs.get('topic_pk'),
                                               board__pk=self.kwargs.get('board_pk'),
                                               created_by=self.request.user)
        return queryset

    def get_success_url(self):
        return reverse_lazy('topic_list', kwargs={'board_pk': self.kwargs.get('board_pk')})


class PostListView(generic.ListView):
    model = models.Post
    context_object_name = 'posts'
    template_name = 'boards/post_list.html'
    paginate_by = 2

    def get_queryset(self):
        self.topic = get_object_or_404(models.Topic,
                                       board__pk=self.kwargs.get('board_pk'),
                                       pk=self.kwargs.get('topic_pk'))
        queryset = self.topic.posts.order_by('created_at')
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        session_key = 'viewed_topic_{}'.format(self.topic.pk)
        if not self.request.session.get(session_key, False):
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key] = True

        kwargs['topic'] = self.topic
        return super().get_context_data(**kwargs)


class PostCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.Post
    # form_class = NewPostForm
    fields = ('message',)
    template_name = 'boards/reply_topic.html'

    def get_context_data(self, **kwargs):
        kwargs['topic'] = get_object_or_404(models.Topic,
                                            pk=self.kwargs.get('topic_pk'),
                                            board__pk=self.kwargs.get('board_pk'))
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        return reverse_lazy('post_list', kwargs={'board_pk': self.kwargs.get('board_pk'),
                                                 'topic_pk': self.kwargs.get('topic_pk')})

    def form_valid(self, form):
        user = self.request.user
        topic = get_object_or_404(models.Topic,
                                  pk=self.kwargs.get('topic_pk'),
                                  board__pk=self.kwargs.get('board_pk'))
        post = form.instance
        post.topic = topic
        post.created_by = user
        post.last_updated_by = user
        post.save()
        topic.last_updated_by = user
        topic.last_updated_at = timezone.now()
        return HttpResponseRedirect(self.get_success_url())


class PostUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.Post
    form_class = NewPostForm
    pk_url_kwarg = 'post_pk'
    template_name = 'boards/post_update.html'

    def get_queryset(self):
        queryset = models.Post.objects.filter(pk=self.kwargs.get('post_pk'),
                                              topic__pk=self.kwargs.get('topic_pk'),
                                              topic__board__pk=self.kwargs.get('board_pk'),
                                              created_by=self.request.user)
        return queryset

    def get_success_url(self):
        return reverse_lazy('post_list', kwargs={'board_pk': self.kwargs.get('board_pk'),
                                                 'topic_pk': self.kwargs.get('topic_pk')})

    def form_valid(self, form):
        user = self.request.user
        post = form.instance
        post.last_updated_by = user
        post.last_updated_at = timezone.now()
        post.save()
        topic = post.topic
        topic.last_updated_at = timezone.now()
        topic.last_updated_by = user
        topic.save()
        return HttpResponseRedirect(self.get_success_url())


class PostDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = models.Post
    pk_url_kwarg = 'post_pk'
    template_name = 'boards/post_confirm_delete.html'

    def get_queryset(self):
        queryset = models.Post.objects.filter(pk=self.kwargs.get('post_pk'),
                                              topic__pk=self.kwargs.get('topic_pk'),
                                              topic__board__pk=self.kwargs.get('board_pk'),
                                              created_by=self.request.user)
        return queryset

    def get_success_url(self):
        return reverse_lazy('post_list', kwargs={'board_pk': self.kwargs.get('board_pk'),
                                                 'topic_pk': self.kwargs.get('topic_pk')})


@login_required
def like_post(request, board_pk, topic_pk, post_pk):
    post = get_object_or_404(models.Post, pk=post_pk, topic__pk=topic_pk, topic__board__pk=board_pk)
    check_liked = models.Like.objects.filter(user=request.user, post=post)
    if check_liked:
        check_liked.delete()
    else:
        models.Like.objects.create(user=request.user, post=post)
    return redirect('post_list', board_pk=board_pk, topic_pk=topic_pk)
