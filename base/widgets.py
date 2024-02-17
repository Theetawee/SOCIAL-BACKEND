from django.forms.widgets import CheckboxSelectMultiple


class CheckboxSelectMultipleWidget(CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = []
        return super().render(name, value, attrs, renderer)
