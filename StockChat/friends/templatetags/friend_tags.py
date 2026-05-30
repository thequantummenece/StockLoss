from django import template

register = template.Library()


@register.filter
def get_status(user_statuses, user_id):
    """Return friendship status for a given user_id."""
    return user_statuses.get(user_id, 'none')
