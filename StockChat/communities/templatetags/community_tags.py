from django import template

register = template.Library()


@register.filter
def get_vote(user_votes, post_id):
    """Return the user's vote value for a given post_id, or None."""
    return user_votes.get(post_id)
