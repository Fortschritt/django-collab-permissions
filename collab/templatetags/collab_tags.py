from django import template
from django.template.base import TemplateSyntaxError
from spaces.models import Space, SpacePluginRegistry

register = template.Library()

class ActionNode(template.defaulttags.URLNode):
    def __init__(self,action, args, kwargs, asvar):
        self.action = template.Variable(action)
        return super(ActionNode,self).__init__(action, args, kwargs, asvar)

    def render(self,context):
        try:
            action = self.action.resolve(context)
            if isinstance(action, Space):
                retval =  '/%s/' % action.slug
            else:
                retval = ''
        except template.VariableDoesNotExist:
            retval =  ''
        if self.asvar:
            context[self.asvar] = retval
            return ''
        return retval

@register.tag
def action_url(parser, token):
    """
    Try to get a url for the given actstream actor, object or target.
    """
    bits = token.contents.split()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one arguments"
                                  " (action)" % bits[0])
    action = bits[1]
    #viewname = parser.compile_filter(bits[1])
    args = []
    kwargs = {}
    asvar = None
    bits = bits[2:]



    if len(bits) >= 2 and bits[-2] == 'as':
        asvar = bits[-1]
        bits = bits[:-2]

    if len(bits):
        for bit in bits:
            match = template.base.kwarg_re.match(bit)
            if not match:
                raise TemplateSyntaxError("Malformed arguments to action_url tag")
            name, value = match.groups()
            if name:
                kwargs[name] = parser.compile_filter(value)
            else:
                args.append(parser.compile_filter(value))

    return ActionNode(action, args, kwargs, asvar)


@register.filter(name="is_manager")
def is_manager(user):
    """
    returns True if user has is_manager permissions or more, else False.
    """
    return user.is_superuser or user.collab.is_manager

@register.filter(name="is_admin_or_manager")
def is_admin_or_manager(user, space):
    """
    Returns True if the given user has 'admin' privileges for the given space,
    else False.

    Usage example:

    {% if user|is_admin:space %}Space Admin{% endif %}

    Is True for a superuser who is not a member in the 'admin' group of this
    space.
    """
    if user and space:
        admins = space.get_admins().user_set.all()
    else:
        return False
    ret = False
    if user in admins or user.is_superuser or \
        hasattr(user, 'collab') and user.collab.is_manager:
        ret = True
    return ret


@register.filter(name="verbose_name")
def verbose_name(value):
    return value._meta.verbose_name

@register.filter(name="nice_name")
def nice_name(value):
    if not value.is_authenticated:
        return ""
    return value.first_name if value.first_name else value.username

@register.filter(name="full_nice_name")
def full_nice_name(value):
    if not value.is_authenticated:
        return ""
    return value.get_full_name() if value.first_name else value.username
