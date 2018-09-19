from django.db import connection

def is_manager(user):
    """
    Returns True if user has at least management rights, else False.
    """
    if user and user.is_authenticated():
        if user.collab.is_manager or user.is_superuser:
            return True
    return False

def is_owner_or_admin(user, owner, space):
    """
    Returns True if either the user is the owner, the user is a space admin
    or the user is a manager. returns False otherwise.
    """
    is_owner = user == owner
    is_admin = user in space.get_admins().user_set.all()
    is_manager = hasattr(user, 'collab') and user.collab.is_manager
    return is_owner or is_admin or is_manager

def is_space_admin_or_manager(user, space):
    """
    Returns True if either the user is the owner, the user is a space admin
    or the user is a manager. returns False otherwise.
    """
    is_admin = user in space.get_admins().user_set.all()
    is_manager = hasattr(user, 'collab') and user.collab.is_manager
    return is_admin or is_manager

def db_table_exists(table_name):
    """ check whether the given table already exists in the database """
    cursor = connection.cursor()
    table_list = connection.introspection.table_names(cursor)
    return table_name in table_list

