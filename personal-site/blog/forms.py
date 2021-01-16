from itertools import chain

from django import forms
from django.db.utils import ProgrammingError

from tinymce.widgets import TinyMCE

from blog.models import Category

def generate_category_choices(category_fields):
    choices = ['None']
    try:
        choices = list(chain([('', 'None')], 
                Category.objects.all().values_list(*category_fields)))
    except ProgrammingError:
        choices = (('', 'None'))
    except Exception as e:
        pass

    return choices

class PostForm(forms.Form):
    category_id = forms.ChoiceField(
            label="Category", 
            widget=forms.Select(attrs={'class': 'input-field'}),
            choices=generate_category_choices(['id', 'name'])
        )
    title = forms.CharField(label="Title")
    content = forms.CharField(
            label="Content",
            widget=TinyMCE()
        )
    publish = forms.BooleanField(required=False, label="Publish")

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['category_id'] = forms.ChoiceField(
            label="Category", 
            widget=forms.Select(attrs={'class': 'input-field'}),
            choices=generate_category_choices(['id', 'name'])
        )


class PostSearchForm(forms.Form):
    category = forms.ChoiceField(
            required=False,
            label="Category", 
            widget=forms.Select(attrs={'class': 'input-field'}),
            choices=generate_category_choices(['name', 'name'])
        )
    title = forms.CharField(
            required=False,
            label="Title"
        )

    def __init__(self, *args, **kwargs):
        super(PostSearchForm, self).__init__(*args, **kwargs)
        self.fields['category'] = forms.ChoiceField(
            required=False,
            label="Category", 
            widget=forms.Select(attrs={'class': 'input-field'}),
            choices=generate_category_choices(['name', 'name'])
        )


class DecipherForm(forms.Form):
    clue = forms.CharField(
            required=False,
            label="Clue",
        )
    clue_photo = forms.CharField(widget=forms.HiddenInput(), required=False)
    clue_photo_name = forms.CharField(widget=forms.HiddenInput(), required=False)
    code = forms.CharField(required=False, label="Code")
