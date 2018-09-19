# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
import json
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.views.generic.base import TemplateView

# Create your views here.

def index(request):
    if not request.user.is_authenticated():
        context = { 'next':reverse("collab_user_views:dashboard")}
        return render(request, 'registration/login.html', context)
    return redirect("collab_user_views:dashboard")

class EmptyIframe(TemplateView):
    """
        Display a template that apart from a centered spinner is empty. Useful
        as defaut content of an iframe.
    """
    template_name = "collab/empty_iframe.html"