from django.shortcuts import render
from django.utils import timezone

from .models import Post

# Create your views here.

def post_list(request):
    posts = Post.objects.filter(
        date_published__lte=timezone.now()
        ).order_by('date_published')
    return render(
        request, 
        'blog/post_list.html', 
        {'posts': posts,},
        )
