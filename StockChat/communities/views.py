from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CommentForm, PostForm
from .models import Comment, Post, Vote


@login_required
def post_list(request):
    sort = request.GET.get('sort', 'new')

    posts = Post.objects.annotate(
        up_count=Count('votes', filter=Q(votes__value=Vote.UP)),
        down_count=Count('votes', filter=Q(votes__value=Vote.DOWN)),
        net_score=Coalesce(
            Sum('votes__value'),
            Value(0),
        ),
        num_comments=Count('comments'),
    ).select_related('author')

    if sort == 'top':
        posts = posts.order_by('-net_score', '-created_at')
    else:
        posts = posts.order_by('-created_at')

    # Fetch the current user's votes for displayed posts
    user_votes = {}
    if request.user.is_authenticated:
        votes = Vote.objects.filter(user=request.user, post__in=posts).values_list('post_id', 'value')
        user_votes = dict(votes)

    return render(request, 'communities/post_list.html', {
        'posts': posts,
        'user_votes': user_votes,
        'current_sort': sort,
    })


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Post published.')
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'communities/post_create.html', {'form': form})


@login_required
def post_detail(request, pk):
    post = get_object_or_404(
        Post.objects.annotate(
            net_score=Coalesce(Sum('votes__value'), Value(0)),
        ).select_related('author'),
        pk=pk,
    )

    # Current user's vote on this post
    user_vote = None
    if request.user.is_authenticated:
        vote_obj = Vote.objects.filter(user=request.user, post=post).first()
        if vote_obj:
            user_vote = vote_obj.value

    # Top-level comments with their replies prefetched
    top_comments = (
        post.comments
        .filter(parent__isnull=True)
        .select_related('author')
        .prefetch_related('replies__author')
    )

    comment_form = CommentForm()

    return render(request, 'communities/post_detail.html', {
        'post': post,
        'user_vote': user_vote,
        'comments': top_comments,
        'comment_form': comment_form,
    })


@login_required
@require_POST
def post_vote(request, pk):
    post = get_object_or_404(Post, pk=pk)
    value_str = request.POST.get('value')

    if value_str not in ('1', '-1'):
        return JsonResponse({'error': 'Invalid vote'}, status=400)

    value = int(value_str)
    vote, created = Vote.objects.get_or_create(
        user=request.user,
        post=post,
        defaults={'value': value},
    )

    if not created:
        if vote.value == value:
            # Same vote again — toggle off
            vote.delete()
        else:
            # Switch vote
            vote.value = value
            vote.save()

    # Recompute score
    score = Vote.objects.filter(post=post).aggregate(
        total=Coalesce(Sum('value'), Value(0))
    )['total']

    # Check user's current vote
    current = Vote.objects.filter(user=request.user, post=post).values_list('value', flat=True).first()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'score': score, 'user_vote': current})

    return redirect('post_detail', pk=pk)


@login_required
@require_POST
def post_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        parent_id = request.POST.get('parent')
        if parent_id:
            comment.parent = get_object_or_404(Comment, pk=parent_id, post=post)
        comment.save()
    return redirect('post_detail', pk=pk)


@login_required
@require_POST
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    post.delete()
    messages.success(request, 'Post deleted.')
    return redirect('communities')
