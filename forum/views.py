from .models import Post, Comment
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from .forms import PostForm, CommentForm
from django.views.generic import CreateView
from django.core.files.storage import FileSystemStorage
from django.urls import reverse_lazy

def post_list(request):
    posts = Post.objects.all().order_by('-created_date')
    context = {
        'posts': posts,
        'MEDIA_URL': settings.MEDIA_URL
    }
    return render(request, 'forum/post_list.html', context)

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = Comment(
                author = request.user,
                body = form.cleaned_data["body"],
                related_to = post
            )
            comment.save()

    comments = Comment.objects.filter(related_to=post)
    context = {
        'post': post,
        'comments': comments,
        'MEDIA_URL': settings.MEDIA_URL,
        'form': form,
    }
    return render(request, 'forum/post_detail.html', context)

def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            if request.FILES:
                file = request.FILES['image']
                dir = settings.MEDIA_ROOT+'/img/'
                fs = FileSystemStorage(dir)
                filename = fs.save(file.name, file)
                file_url = fs.url(filename)
            post = form.save(commit=False)
            post.author = request.user
            post.image = dir+file.name
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'forum/post_edit.html', {'form': form})

# class PostCreate(CreateView):
#     model = Post
#     form_class = PostForm
#     template_name = 'forum/post_edit.html'
#     success_url = reverse_lazy('post_list')