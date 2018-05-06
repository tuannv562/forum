from django import template

from ..models import Post, User, Like

register = template.Library()


@register.simple_tag
def is_post_liked_by_user(post: Post, user: User) -> bool:
    check = Like.objects.filter(user=user, post=post)
    if check:
        return True
    else:
        return False
