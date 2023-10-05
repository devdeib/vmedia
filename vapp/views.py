from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files import File
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.db.models import Max
from django.core.files.storage import FileSystemStorage
from . forms import *
from . models import *
# Create your views here.



def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/login')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})



def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('/feed')
        else:
            return redirect('login')
    return render(request, 'login.html')



def profile_view(request):
    user_profile = UserProfile.objects.get(user=request.user)
    posts = Post.objects.filter(author=request.user)
    return render(request, 'profile.html', {'user_profile': user_profile, 'posts': posts})



def profile_edit(request):
    user_profile = request.user.userprofile
    form = EditProfileForm(instance=user_profile)

    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            user = user_profile.user
            if form.cleaned_data.get('password') or user.email != form.cleaned_data['email']:
                if form.cleaned_data.get('password'):
                    user.set_password(form.cleaned_data['password'])
                user.username = form.cleaned_data['username']
                user.email = form.cleaned_data['email']
                user.save()
                update_session_auth_hash(request, user)  # Update session with new password
            form.save()

    # Pre-fill username and email fields
    form.initial['email'] = request.user.email
    form.initial['username'] = request.user.username

    context = {'form': form}
    return render(request, 'edit_profile.html', context)



def change_password(request):
    user = request.user
    form = EditProfileForm(instance=user)

    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=user)
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            if user.check_password(old_password):
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed successfully.')
                return redirect('profile_edit')
            else:
                messages.error(request, 'Incorrect old password.')

    context = {'form': form}
    return render(request, 'change_password.html', context)



def delete_photo(request):
    user_profile = UserProfile.objects.get(user=request.user)
    user_profile.photo.delete()
    user_profile.save()
    return redirect('vapp:profile')



def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.status = Post.Status.PUBLISHED
            post.author = request.user

            # Retrieve the title and slug from the post body
            body = form.cleaned_data['body']
            words = body.split()
            post.title = ' '.join(words[:2])
            post.slug = '-'.join(words[:2])

            post.save()

            # Save the tags after the post has been saved
            form.save_m2m()  # Save the tags associated with the post

            return redirect('/feed')  # Redirect to the feed page

    form = PostForm()
    return render(request, 'create_post.html', {'form': form})



def post_list(request, tag_slug=None):
    posts = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = posts.filter(tags__in=[tag])

    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.status = Post.Status.PUBLISHED
            post.author = request.user

            # Retrieve the title and slug from the post body
            body = form.cleaned_data['body']
            words = body.split()
            post.title = ' '.join(words[:2])
            post.slug = '-'.join(words[:2])

            post.save()

            return redirect('/feed')  # Redirect to the feed page
    else:
        form = PostForm()

    # Retrieve the latest comment for each post
    for post in posts:
        latest_comment = Comment.objects.filter(post=post).order_by('-created').first()
        post.latest_comment = latest_comment

    return render(request, 'feed.html', {'posts': posts, 'tag': tag, 'form': form})


def search(request):
    query = request.GET.get('q')
    results = Post.published.filter(body__icontains=query)
    return render(request, 'search_results.html', {'results': results, 'query': query})


def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if user in post.likes.all():
        post.likes.remove(user)
    else:
        post.likes.add(user)

    post.updated = timezone.now()  # Set the updated time to the current time
    post.save()

    return redirect('vapp:post_list')

def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author == request.user:
        post.delete()
    return redirect('/profile')



def post_detail(request, year, month, day, post):
    
    post = get_object_or_404(Post, status=Post.Status.PUBLISHED, slug=post, publish__year=year, publish__month=month, publish__day=day)
    # List of active comments for this post
    comments = post.comments.filter(active=True)
    # Form for users to comment
    form = CommentForm()
    
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids)\
                                  .exclude(id=post.id) 
                                  
    similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
                                 .order_by('-same_tags','-publish')[:4]
                                 
    return render(request, 'post_detail.html', {'post': post, 'comments': comments, 'form': form, 'similar_posts': similar_posts})
    


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    
    # A comment was posted
    if request.method == 'POST':
        form = CommentForm(data=request.POST)
        if form.is_valid():
            # Create a Comment object without saving it to the database
            comment = form.save(commit=False)
        
            # Retrieve the currently logged-in user's email, name, and photo
            user_email = request.user.email
            user_name = request.user.username
            user_photo = request.user.userprofile.photo
            
            # Set the email, name, and post fields of the comment form
            comment.email = user_email
            comment.name = user_name
            comment.post = post
            
            # Save the user's photo to the comment model
            if user_photo:
                comment.photo.save(user_photo.name, File(user_photo))
            
            # Save the comment to the database
            comment.save()
        
            # Redirect the user back to the post list view
            return redirect(reverse('vapp:post_list'))
    else:
        form = CommentForm()

    
    
    return render(request, 'feed.html', {'post': post, 'form': form, 'comment': comment})
def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False
    
    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST, user=request.user)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n{cd['name']}'s comments: {cd['comments']}"
            send_mail(subject, message, cd['email'], [cd['to']])
            sent = True
    else:
        form = EmailPostForm(user=request.user)
    
    return render(request, 'post_share.html', {'post': post, 'form': form, 'sent': sent})