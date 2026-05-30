from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Friendship

User = get_user_model()


def _get_friends(user):
    """Return a queryset of User objects who are accepted friends."""
    accepted = Friendship.objects.filter(
        Q(sender=user, status=Friendship.ACCEPTED) |
        Q(receiver=user, status=Friendship.ACCEPTED)
    ).values_list('sender_id', 'receiver_id')

    friend_ids = set()
    for s, r in accepted:
        friend_ids.add(s if s != user.pk else r)

    return User.objects.filter(pk__in=friend_ids)


@login_required
def friends_list(request):
    friends = _get_friends(request.user)
    incoming = Friendship.objects.filter(
        receiver=request.user, status=Friendship.PENDING,
    ).select_related('sender')
    outgoing = Friendship.objects.filter(
        sender=request.user, status=Friendship.PENDING,
    ).select_related('receiver')

    return render(request, 'friends/friends_list.html', {
        'friends': friends,
        'incoming': incoming,
        'outgoing': outgoing,
    })


@login_required
def search_users(request):
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        results = (
            User.objects
            .filter(username__icontains=query)
            .exclude(pk=request.user.pk)[:20]
        )

    # Build a lookup of relationship status for each result
    friend_ids = set(_get_friends(request.user).values_list('pk', flat=True))
    pending_sent = set(
        Friendship.objects.filter(sender=request.user, status=Friendship.PENDING)
        .values_list('receiver_id', flat=True)
    )
    pending_received = set(
        Friendship.objects.filter(receiver=request.user, status=Friendship.PENDING)
        .values_list('sender_id', flat=True)
    )

    user_statuses = {}
    for u in results:
        if u.pk in friend_ids:
            user_statuses[u.pk] = 'friends'
        elif u.pk in pending_sent:
            user_statuses[u.pk] = 'sent'
        elif u.pk in pending_received:
            user_statuses[u.pk] = 'received'
        else:
            user_statuses[u.pk] = 'none'

    return render(request, 'friends/search.html', {
        'query': query,
        'results': results,
        'user_statuses': user_statuses,
    })


@login_required
@require_POST
def send_request(request, user_id):
    target = get_object_or_404(User, pk=user_id)
    if target == request.user:
        messages.warning(request, "You cannot add yourself.")
        return redirect('search_users')

    # Check if any relationship already exists in either direction
    exists = Friendship.objects.filter(
        Q(sender=request.user, receiver=target) |
        Q(sender=target, receiver=request.user)
    ).exists()

    if exists:
        messages.info(request, f"A request with {target.username} already exists.")
    else:
        Friendship.objects.create(sender=request.user, receiver=target)
        messages.success(request, f"Friend request sent to {target.username}.")

    return redirect('search_users')


@login_required
@require_POST
def accept_request(request, pk):
    friendship = get_object_or_404(
        Friendship, pk=pk, receiver=request.user, status=Friendship.PENDING,
    )
    friendship.status = Friendship.ACCEPTED
    friendship.save()
    messages.success(request, f"You are now friends with {friendship.sender.username}.")
    return redirect('friends')


@login_required
@require_POST
def decline_request(request, pk):
    friendship = get_object_or_404(
        Friendship, pk=pk, receiver=request.user, status=Friendship.PENDING,
    )
    friendship.delete()
    messages.success(request, "Request declined.")
    return redirect('friends')


@login_required
@require_POST
def cancel_request(request, pk):
    friendship = get_object_or_404(
        Friendship, pk=pk, sender=request.user, status=Friendship.PENDING,
    )
    friendship.delete()
    messages.success(request, "Request cancelled.")
    return redirect('friends')


@login_required
@require_POST
def unfriend(request, user_id):
    target = get_object_or_404(User, pk=user_id)
    deleted = Friendship.objects.filter(
        Q(sender=request.user, receiver=target, status=Friendship.ACCEPTED) |
        Q(sender=target, receiver=request.user, status=Friendship.ACCEPTED)
    ).delete()[0]

    if deleted:
        messages.success(request, f"Removed {target.username} from friends.")
    return redirect('friends')
