## Django Collab
This app augments Djangos default user model with the permissions needed for the Django Collab platform.
Also provides a few mixins to make custom apps obey the permissions.

## Limitations
This module extends your `settings.AUTH_USER_MODEL` with additional fields. This should work
transparently unless you register this module once users have already been created. In this case
you have to create the extra objects manually, so that the users already existing also get the needed fields.
To do that, run `python manage.py shell` and do the following:

```
>>> from django.contrib.auth import get_user_model
>>> from collab.models import Collab
>>> users = get_user_model()
>>> for user in users.objects.all():
...     Collab.objects.get_or_create(user=user)
... 
(<Collab: Collab object>, True)
(<Collab: Collab object>, True)
[...]
>>> 
```
## writing plugins
see corresponding chapter in the django-spaces documentation


## Registering django-spaces plugins with dashboard news:
Collab uses actstream to show member activities on the Space Dashboard.

To enable this feature for your plugin, two steps are required. First, you have to enable your model.
Open your app's `apps.py` file and extend the `ready()` method like this:

```
def ready(self):
    from actstream import registry
	from .models import YourModel
    registry.register(YourModel)
```

At his point your model is known to the system. Now you can find good points for emitting new
messages into the activity stream. Find a place where the action of interest just happened, for
example directly after creating a new model instance.

```
from actstream.signals import action
action.send(
	sender=request.user, 
    verb="was created/changed", 
    target=request.SPACE, 
    action_object=your_model_instance
)
```

target is mandatory: it ensures that your new activity records shows up only in the Space your 
model instance got created in.

action_object is your new model instance. It should have a meaningful string representation 
(which is the case if you have provided a `__str__` method in your model) and ideally a 
`get_absolute_url()` method for linking directly to the point of interest.