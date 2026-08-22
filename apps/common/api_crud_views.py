"""
Thin Django "shell" views for resources converted to the REST-API-driven
CRUD pattern (see apps/common/api_generic.py, static/js/core/crud.js).
These render page chrome only - the actual list/form data comes from the
matching DRF API at request time via JS - but keep the exact same
RoleRequiredMixin gate apps/common/crud.py's CrudListView/CreateView/
UpdateView/DeleteView already use, so an unauthenticated or wrong-role
visitor is blocked before any JS ever runs, identically to before.
"""
import json

from django.urls import reverse
from django.views.generic import TemplateView

from .api_metadata import id_template_url
from .permissions import RoleRequiredMixin


class ApiCrudListView(RoleRequiredMixin, TemplateView):
    template_name = 'common/api_generic_list.html'
    page_title = ''
    api_list_url_name = None
    columns = ()  # [(key, label), ...] - key may be a *_label field for FK columns
    add_url_name = None
    edit_url_name = None
    delete_url_name = None
    extra_actions = ()  # [{'url_name': ..., 'label': ..., 'icon': ...}, ...]
    created_message = 'Created.'
    updated_message = 'Updated.'
    deleted_message = 'Deleted.'
    enable_search = False  # requires the API viewset to have a SearchFilter backend wired up
    search_placeholder = 'Search...'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config = {
            'apiList': reverse(self.api_list_url_name),
            'columns': [list(c) for c in self.columns],
            'addUrl': reverse(self.add_url_name) if self.add_url_name else None,
            'editUrlTemplate': id_template_url(self.edit_url_name) if self.edit_url_name else None,
            'deleteUrlTemplate': id_template_url(self.delete_url_name) if self.delete_url_name else None,
            'extraActions': [
                {'url': reverse(a['url_name']), 'label': a['label'], 'icon': a.get('icon')}
                for a in self.extra_actions
            ],
            'createdMessage': self.created_message,
            'updatedMessage': self.updated_message,
            'deletedMessage': self.deleted_message,
            'enableSearch': self.enable_search,
            'searchPlaceholder': self.search_placeholder,
        }
        context['page_title'] = self.page_title
        context['crud_config'] = json.dumps(config)
        return context


class ApiCrudFormView(RoleRequiredMixin, TemplateView):
    """Serves both create (no pk in the URL) and edit (pk in the URL)."""
    template_name = 'common/api_generic_form.html'
    create_page_title = ''
    edit_page_title = ''
    api_list_url_name = None
    api_detail_url_name = None
    list_url_name = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        config = {
            'apiList': reverse(self.api_list_url_name),
            'apiDetail': reverse(self.api_detail_url_name, args=[pk]) if pk else None,
            'cancelUrl': reverse(self.list_url_name),
            'redirectUrl': reverse(self.list_url_name),
        }
        context['page_title'] = self.edit_page_title if pk else self.create_page_title
        context['crud_config'] = json.dumps(config)
        context['cancel_url'] = reverse(self.list_url_name)
        return context


class ApiCrudDeleteView(RoleRequiredMixin, TemplateView):
    template_name = 'common/api_generic_confirm_delete.html'
    api_detail_url_name = None
    list_url_name = None
    title_fields = ()  # e.g. ('code', 'name') - joined to reproduce the model's __str__
    title_separator = ' - '

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs['pk']
        config = {
            'apiDetail': reverse(self.api_detail_url_name, args=[pk]),
            'redirectUrl': reverse(self.list_url_name),
            'titleFields': list(self.title_fields),
            'titleSeparator': self.title_separator,
        }
        context['crud_config'] = json.dumps(config)
        context['cancel_url'] = reverse(self.list_url_name)
        return context
