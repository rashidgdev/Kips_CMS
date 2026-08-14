"""
Generic CRUD view bases for simple "setup/reference data" screens (Programs,
Fee Categories, Rooms, etc.) so each app doesn't hand-roll near-identical
list/create/update/delete views and templates. Business-logic-heavy screens
(marking attendance, entering marks, scheduling classes) still use plain
function views elsewhere - this is only for straightforward model CRUD.
"""
from django.contrib import messages
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .permissions import RoleRequiredMixin


class CrudListView(RoleRequiredMixin, ListView):
    template_name = 'common/generic_list.html'
    paginate_by = 50
    page_title = ''
    list_display = ()  # [(attribute_path, column_label), ...]
    add_url_name = None
    edit_url_name = None
    delete_url_name = None
    extra_actions = ()  # [{'url_name': ..., 'label': ..., 'icon': ...}, ...] - secondary buttons next to Add
    bulk_delete_url_name = None  # POST target for multi-select "Delete Selected"
    row_actions = ()  # [{'url_name': ..., 'label': ...}, ...] - extra per-row links beyond Edit/Delete
    filter_fields = ()  # [(field_name, label, choices_queryset_or_None), ...] - GET-param select filters

    def get_queryset(self):
        queryset = super().get_queryset()
        for field_name, _label, _choices in self.filter_fields:
            value = self.request.GET.get(field_name)
            if value:
                queryset = queryset.filter(**{field_name: value})
        return queryset

    def get_filter_options(self):
        options = []
        for field_name, label, choices in self.filter_fields:
            if choices is None:
                values = (
                    self.model._default_manager.order_by()
                    .values_list(field_name, flat=True).distinct()
                )
                choice_list = [(v, v) for v in sorted(v for v in values if v is not None)]
            else:
                # `choices` is a QuerySet stored on the class at import time;
                # re-clone via `.all()` so each request re-queries instead of
                # reusing whatever got cached into `_result_cache` the first
                # time it was ever iterated.
                choice_list = [(obj.pk, str(obj)) for obj in choices.all()]
            options.append({
                'name': field_name,
                'label': label,
                'choices': choice_list,
                'selected': self.request.GET.get(field_name, ''),
            })
        return options

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            page_title=self.page_title,
            list_display=self.list_display,
            add_url_name=self.add_url_name,
            edit_url_name=self.edit_url_name,
            delete_url_name=self.delete_url_name,
            extra_actions=self.extra_actions,
            bulk_delete_url_name=self.bulk_delete_url_name,
            row_actions=self.row_actions,
            filter_options=self.get_filter_options() if self.filter_fields else None,
        )
        return context


class _CrudFormMixin:
    template_name = 'common/generic_form.html'
    page_title = ''
    success_message = 'Saved.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        # Use the raw `success_url` rather than `get_success_url()`: the
        # latter calls `self.object.__dict__` to support `.format()`
        # placeholders, but for CreateView `self.object` is still None at
        # GET-time (before the form has ever been saved), which crashes.
        context['cancel_url'] = str(self.success_url)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response


class CrudCreateView(_CrudFormMixin, RoleRequiredMixin, CreateView):
    pass


class CrudUpdateView(_CrudFormMixin, RoleRequiredMixin, UpdateView):
    pass


class CrudDeleteView(RoleRequiredMixin, DeleteView):
    template_name = 'common/generic_confirm_delete.html'
    success_message = 'Deleted.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = str(self.success_url)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response
