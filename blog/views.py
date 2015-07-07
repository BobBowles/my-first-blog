from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .models import Post
from .forms import PostForm

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
        
@login_required
def post_draft_list(request):
    posts = Post.objects.filter(
        date_published__isnull=True
        ).order_by('date_created')
    return render(
        request, 
        'blog/post_draft_list.html', 
        {'posts': posts,},
        )
        
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(
        request, 
        'blog/post_detail.html', 
        {'post': post},
        )
        
@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('blog.views.post_detail', pk=post.pk,)
        
@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.date_published = timezone.now()
            post.save()
            return redirect('blog.views.post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(
        request, 
        'blog/post_edit.html', 
        {'form': form},
        )
        
@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.date_published = timezone.now()
            post.save()
            return redirect('blog.views.post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(
        request, 
        'blog/post_edit.html', 
        {'form': form},
        )
        
@login_required
def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    return redirect('blog.views.post_list')

