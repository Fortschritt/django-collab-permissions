from spaces.models import SpacePluginRegistry


def default(request):
    """
        Fill in commonly needed context for space-based theming etc.
    """
    context = {}
    # get_plugins() is a generator. Converting to list so we can use the output
    # multiple times.
    context["space_plugins"] = list(SpacePluginRegistry.get_plugins())
    context["space"] = request.SPACE if hasattr(request,'SPACE') else None
    return context
