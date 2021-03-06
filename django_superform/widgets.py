import django
from django import forms
from django.template import loader


class TemplateWidget(forms.Widget):
    """
    Template based widget. It renders the ``template_name`` set as attribute
    which can be overriden by the ``template_name`` argument to the
    ``__init__`` method.
    """

    field = None
    template_name = None
    value_context_name = None

    def __init__(self, *args, **kwargs):
        template_name = kwargs.pop('template_name', None)
        if template_name is not None:
            self.template_name = template_name
        super(TemplateWidget, self).__init__(*args, **kwargs)

    def get_context_data(self):
        return {}

    def get_context(self, name, value, attrs=None, **kwargs):
        attrs = {} if attrs is None else attrs
        context = {
            'name': name,
            'hidden': self.is_hidden,
            'required': self.is_required,
            # In our case ``value`` is the form or formset instance.
            'value': value,
        }
        if self.value_context_name:
            context[self.value_context_name] = value

        if self.is_hidden:
            context['hidden'] = True

        context.update(self.get_context_data())
        context['attrs'] = self.build_attrs(attrs)
        if django.VERSION >= (1, 11):
            # Once support for older versions is dropped, this class
            # should be replaced with template widgets now that django
            # supports this.
            # See https://docs.djangoproject.com/en/1.11/ref/forms/renderers/
            context['widget'] = context

        return context

    def render(self, name, value, attrs=None, **kwargs):
        template_name = kwargs.pop('template_name', None)
        if template_name is None:
            template_name = self.template_name
        context = self.get_context(name, value, attrs=attrs or {}, **kwargs)
        return loader.render_to_string(template_name, context=context)


class FormWidget(TemplateWidget):
    template_name = 'superform/formfield.html'
    value_context_name = 'form'

    def value_from_datadict(self, data, files, name):
        return self.form


class FormSetWidget(TemplateWidget):
    template_name = 'superform/formsetfield.html'
    value_context_name = 'formset'

    def value_from_datadict(self, data, files, name):
        return self.formset
