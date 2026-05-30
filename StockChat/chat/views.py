from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max, Subquery, OuterRef, Case, When, F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from friends.models import Friendship
from .models import Message

User = get_user_model()


def _get_friend_ids(user):
    """Return set of user IDs who are accepted friends."""
    accepted = Friendship.objects.filter(
        Q(sender=user, status=Friendship.ACCEPTED) |
        Q(receiver=user, status=Friendship.ACCEPTED)
    ).values_list('sender_id', 'receiver_id')
    ids = set()
    for s, r in accepted:
        ids.add(s if s != user.pk else r)
    return ids


def _are_friends(user, other):
    return Friendship.objects.filter(
        Q(sender=user, receiver=other) | Q(sender=other, receiver=user),
        status=Friendship.ACCEPTED,
    ).exists()


@login_required
def inbox(request):
    """Show list of conversations (friends with latest message)."""
    friend_ids = _get_friend_ids(request.user)
    friends = User.objects.filter(pk__in=friend_ids)

    # Get latest message and unread count for each friend
    conversations = []
    for friend in friends:
        latest_msg = (
            Message.objects.filter(
                Q(sender=request.user, receiver=friend) |
                Q(sender=friend, receiver=request.user)
            )
            .order_by('-created_at')
            .first()
        )
        unread = Message.objects.filter(
            sender=friend, receiver=request.user, is_read=False,
        ).count()
        conversations.append({
            'friend': friend,
            'latest': latest_msg,
            'unread': unread,
        })

    # Sort: conversations with messages first (newest), then those without
    conversations.sort(
        key=lambda c: c['latest'].created_at if c['latest'] else c['friend'].date_joined,
        reverse=True,
    )

    return render(request, 'chat/inbox.html', {'conversations': conversations})


@login_required
def conversation(request, user_id):
    """Show chat window with a specific friend."""
    other = get_object_or_404(User, pk=user_id)

    if not _are_friends(request.user, other):
        return render(request, 'chat/not_friends.html', {'other': other})

    # Mark messages from other user as read
    Message.objects.filter(
        sender=other, receiver=request.user, is_read=False,
    ).update(is_read=True)

    messages_qs = Message.objects.filter(
        Q(sender=request.user, receiver=other) |
        Q(sender=other, receiver=request.user)
    ).order_by('created_at')[:200]

    return render(request, 'chat/conversation.html', {
        'other': other,
        'messages': messages_qs,
    })


@login_required
@require_POST
def send_message(request, user_id):
    """Send a message via AJAX."""
    other = get_object_or_404(User, pk=user_id)

    if not _are_friends(request.user, other):
        return JsonResponse({'error': 'Not friends'}, status=403)

    body = request.POST.get('body', '').strip()
    if not body:
        return JsonResponse({'error': 'Empty message'}, status=400)

    msg = Message.objects.create(
        sender=request.user,
        receiver=other,
        body=body,
    )

    return JsonResponse({
        'id': msg.pk,
        'body': msg.body,
        'sender': msg.sender.username,
        'created_at': msg.created_at.strftime('%H:%M'),
        'is_mine': True,
    })


@login_required
def poll_messages(request, user_id):
    """Poll for new messages since a given message ID."""
    other = get_object_or_404(User, pk=user_id)
    after_id = int(request.GET.get('after', 0))

    if not _are_friends(request.user, other):
        return JsonResponse({'error': 'Not friends'}, status=403)

    new_msgs = Message.objects.filter(
        sender=other,
        receiver=request.user,
        pk__gt=after_id,
    ).order_by('created_at')

    # Mark as read
    new_msgs.filter(is_read=False).update(is_read=True)

    data = [{
        'id': m.pk,
        'body': m.body,
        'sender': m.sender.username,
        'created_at': m.created_at.strftime('%H:%M'),
        'is_mine': False,
    } for m in new_msgs]

    return JsonResponse({'messages': data})


@login_required
def unread_count(request):
    """Return total unread message count (for sidebar badge)."""
    count = Message.objects.filter(
        receiver=request.user, is_read=False,
    ).count()
    return JsonResponse({'unread': count})
