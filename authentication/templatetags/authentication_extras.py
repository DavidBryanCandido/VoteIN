from django import template

register = template.Library()
 
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def check_pending_request(student_obj, position_obj, existing_requests_tuples):
    """
    Checks if a request for the given student and position exists
    in the list of existing_requests_tuples.
    """
    if not student_obj or not position_obj or not existing_requests_tuples:
        return False
    return (str(student_obj.id), str(position_obj.id)) in existing_requests_tuples 