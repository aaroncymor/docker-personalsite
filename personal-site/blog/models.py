from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.urls import reverse

from tinymce import models as tinymce_models

from blog.managers import PublishedPostManager
from core.utils import (
    load_html_doc,
    get_html_content,
    get_tags
)
from core.models import PortfolioMixin

# Create your models here.

class Category(PortfolioMixin):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Post(PortfolioMixin):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=100)
    content = tinymce_models.HTMLField()
    published_date = models.DateTimeField(blank=True, null=True)

    objects = models.Manager()
    published_objects = PublishedPostManager()

    class Meta:
        db_table = 'post'
    
    @property
    def short_content_for_home(self):
        # Slice content to 200 characters
        soup = load_html_doc(self.content)
        deciphers = soup.select('span.decipher')
        for decipher in deciphers:
            decipher.decompose()
        
        return soup.get_text()[:200]

    @property
    def short_content_for_list(self):
        # Slice content to 500 characters
        soup = load_html_doc(self.content)
        deciphers = soup.select('span.decipher')
        for decipher in deciphers:
            decipher.decompose()

        return soup.get_text()[:200]
    
    @property
    def sanitized_content(self):
        soup = load_html_doc(self.content)
        
        # get all span.decipher elements
        # prepended with underscore as a marker that is is
        # an HTML element, not from database 
        _deciphers = soup.select('span.decipher')
        for _decipher in _deciphers:
            decipher_id = _decipher.get('id', '')
            decipher_classes = _decipher.get('class', [])

            if decipher_id:
                # get decipher from db
                decipher = self.deciphers.get(name=decipher_id)

                # create div element tag for tooltip
                div_tooltip_container = soup.new_tag('div')
                div_tooltip_container['id'] = "tooltip-" + decipher.name
                div_tooltip_container['class'] = decipher_classes + ['tooltip-container']
                div_tooltip_container['data-target'] = '#' + decipher.name

                # create form
                decipher_form = soup.new_tag('form')
                decipher_form['class'] = ['notify-form', 'decipher-form']
                decipher_form['data-checkcode-url'] = reverse('api:decipher-check-code', args=[str(decipher.id)])
                
                # create div element tag for notify / pop up message
                div_notify_container = soup.new_tag('div')
                div_notify_container['class'] = ['notify-container']

                # create icon element for notify close
                close_notify_container = soup.new_tag('i')
                close_notify_container['class'] = ['fas', 'fa-times', 'decipher-close']

                div_notify_container.append(close_notify_container)

                # create div row for clue
                decipher_form_row = soup.new_tag('div')
                decipher_form_row['class'] = ['notify-form-row']

                decipher_clue = soup.new_tag('p')
                decipher_clue_label = soup.new_tag('span')
                decipher_clue_label.string = "clue:"
                decipher_clue.append(decipher_clue_label)
                decipher_clue.append(decipher.clue) 

                # append row clue to form
                decipher_form_row.append(decipher_clue)
                decipher_form.append(decipher_form_row)

                if decipher.clue_photo_url:
                    # create new row for clue_photo
                    decipher_form_row = soup.new_tag('div')
                    decipher_form_row['class'] = ['notify-form-row']
                
                    # create img element tag
                    decipher_clue_photo = soup.new_tag('img')
                    decipher_clue_photo['class'] = ['decipher-clue-photo']
                    decipher_clue_photo['src'] = decipher.clue_photo_url
                    
                    # append to new div form row
                    decipher_form_row.append(decipher_clue_photo)
                    # append div form row to form
                    decipher_form.append(decipher_form_row)

                decipher_form_row = soup.new_tag('div')
                decipher_form_row['class'] = ['notify-form-row']
                
                decipher_code = soup.new_tag('input')
                decipher_code['type'] = "text"
                decipher_code['name'] = "code"

                decipher_form_row.append(decipher_code)
                decipher_form.append(decipher_form_row)

                decipher_form_submit = soup.new_tag('button')
                decipher_form_submit['type'] = "submit"
                decipher_form_submit.string = "Enter"

                # input[type="text"] and button on same row
                decipher_form_row.append(decipher_form_submit)

                # append form.notify-form to div.notify-container
                div_notify_container.append(decipher_form)

                # append the div.notify-container to div.tooltip-container
                div_tooltip_container.append(div_notify_container)

                # change span.decipher with div.tooltip-container.decipher
                _decipher.replace_with(div_tooltip_container)

        #print("SOUPPPP",soup)
        return soup.prettify(formatter="html5")

    @property
    def is_published(self):
        
        if self.published_date:
            return True
        return False

    def __str__(self):
        return self.title


class Tag(PortfolioMixin):
    tag = models.CharField(max_length=100)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='tags')

    class Meta:
        db_table = 'tag'
        unique_together = ('tag', 'post')
    
    @property
    def html_id(self):
        return self.tag.replace(" ", "-")
    
    def __str__(self):
        return self.tag


class Decipher(PortfolioMixin):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='deciphers')
    hidden_text = models.CharField(max_length=255)
    name = models.CharField(max_length=100, null=True, default='')
    clue_photo_filename = models.CharField(max_length=255, null=True, default='')
    clue_photo_fullpath = models.CharField(max_length=255, null=True, default='')
    clue_photo_url = models.CharField(max_length=255, null=True, default='')
    clue = models.CharField(max_length=50)
    code = models.CharField(max_length=20, null=True, blank=True, default='')
