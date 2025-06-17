# from http.client import HTTPResponse
# from bootstrap_datepicker_plus.widgets import DateTimePickerInput
# from django.db.transaction import commit
# from django.forms import CheckboxSelectMultiple, SelectMultiple
# import django.utils.functional
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404
from django.views import generic
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import AnonymousUser
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache

from typing_extensions import Any


class HomeView(generic.TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
