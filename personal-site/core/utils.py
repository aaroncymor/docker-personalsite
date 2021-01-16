import json
from math import ceil

from django.conf import settings
from django.views import generic
from django.core.exceptions import ImproperlyConfigured
from django.db.models.query import QuerySet
from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor, ReverseManyToOneDescriptor
from django.utils.translation import gettext as _

from bs4 import BeautifulSoup

LOGGER_TYPES = ['info', 'debug', 'warning']

API_CUSTOM_STATUS_CODES = {
    2000: 'List successfully retrieved.',
    2001: 'Data successfully retrieved.',
    2002: 'Data successfully saved.',
    2003: 'Data successfully updated.',
    2004: 'Data successfully deleted.',

    4000: 'Serializer related error. Check fields and parameters submitted.',
    4001: 'Invalid post parameters.',
    4002: 'Invalid parameters count.',
    4003: 'Data does not exist. Model affected: ',
    4004: 'Duplicate data error.',
    4999: 'Client error occured. Please investigate.',
    
    5000: 'Server error occured. Please investigate.',

    9999: 'Unknown error occured. Please investigate.',
}

CHATBOT_CUSTOM_STATUS_CODES = {
    2000: 'Message from user successfully received.',
    2001: 'Token verification successful.',
    2002: 'Page verification successful.',

    4000: 'Message unsuccessful.',
    4001: 'Token verification unsuccessful.',
    4002: 'User is forbidden.'
}


# BeautifulSoup related utils
def load_html_doc(html_doc):
    """
    """
    return BeautifulSoup(html_doc, features="html.parser")


def get_html_content(soup):
    """
    """
    try:
        text = soup.get_text()
    except AttributeError:
        return
    return soup.get_text()


def get_tags(soup, selector):
    """
    """
    try:
        tags = soup.select(selector)
    except AttributeError:
        return
    return tags


def assign_attr_to_tag(tag, target_attr, attr_val):
    """
    """
    try:
        tag[target_attr] = attr_val
    except (KeyError, AttributeError):
        return


def append_classes_to_tag(tag, addtl_class=[]):
    """
    """
    try:
        tag_classes = tag['class']
        if addtl_class in tag_classes:
            return
        # addtl_class should be list of strings
        tag['class'] += addtl_class
    except KeyError:
        return

def wrap_element(soup, wrapper, tag, tag_attr):
    """
    soup
    wrapper
    tag
    tag_attr: tag_attribute
    """
    try:
        attr = getattr(tag, tag_attr)
    except (TypeError):
        attr = tag
    wrap = getattr(attr, 'wrap')
    if callable(wrap):
        wrap(soup.new_tag(wrapper))

def replace_element(soup, replacement, tag, tag_attr):
    try:
        attr = getattr(tag, tag_attr)
    except (TypeError):
        attr = tag
    replace_with = getattr(attr, 'replace_with')
    if callable(replace_with):
        replace_with(soup.new_tag(replacement))

# end of BeautifulSoup related utils


def enum(sequence, start=0):
    for index, value in enumerate(sequence):
        yield index + start, value


class ModifiedSearchListView(generic.ListView):
    filter_class = None
    filter_fields = []
    filter_field_suffix = '_search'
    filter_refresh_key = 'refresh'

    def get_filter_class(self):
        return self.filter_class
    
    def get_filter_fields(self):
        return self.filter_fields

    def get_filter_field_suffix(self):
        return self.filter_field_suffix

    def get_filter_refresh_key(self):
        return self.filter_refresh_key

    def get_queryset(self):
        """
        Return the list of items for this view.
        The return value must be an iterable and may be an instance of
        `QuerySet` in which case `QuerySet` specific behavior will be enabled.
        
        -Aaron overriding get_queryset for pagination with filters
        https://github.com/django/django/blob/2.1/django/views/generic/list.py#L194
        """
        if self.queryset is not None:
            queryset = self.queryset
            if isinstance(queryset, QuerySet):
                queryset = queryset.all()
        elif self.model is not None:
            queryset = self.model._default_manager.all()
        else:
            raise ImproperlyConfigured(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, %(cls)s.queryset, or override "
                "%(cls)s.get_queryset()." % {
                    'cls': self.__class__.__name__
                }
            )

        # Adding filter to queryset
        filter_class = self.get_filter_class()
        search_filter = {}

        if self.request.session and self.filter_class:
            session_keys = self.request.session.keys()
            for base_filter in self.filter_class.base_filters.keys():
                search_filter_field = base_filter + self.get_filter_field_suffix()
                if search_filter_field in session_keys:
                    refresh_key = self.get_filter_refresh_key()
                    if refresh_key in self.request.GET.keys() \
                        and self.request.GET[refresh_key] in ['true', 'True']:
                        # remove session and don't use as filter for queryset
                        del self.request.session[search_filter_field]
                    else:
                        # add to search filter and use for filtering queryset                     
                        search_filter[base_filter] = self.request.session[search_filter_field]
            queryset = self.filter_class(search_filter, queryset=queryset).qs
        # End of adding filter queryset

        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)

        return queryset


## TODO: Reference personal_site.core.utils.group_pagination
## Check if we need to make partitions for pagination.

def group_pagination(num_pages, group_num):
    """
    Let's say in our queryset, we have 11 number of pages,
    and we wanted to group them by 3 like so below:

    1. 1 2 3 >
    2. < 4 5 6 >
    3. < 7 8 9 >
    4. < 10 11

    total number of pages / group_by (page range to show) = ceil(answer) # group
    num_of_groups = ceil(num_of_pages / group_by)
    
    We have 4 groups from 11 pages

    4 = ceil(11 / 3)

    Now all we need to do is determine the page range with the given group_number
    if  we were given group_number = 2, this would return list if [4, 5, 6]

    To get that, we multiply group_number * group_by, from there we can determine the
    page_range

    Returns:
        list -- list of pages based on the given group number
    """
    group_by = settings.GROUPBY_PAGINATION

    has_next, has_prev, next_num, prev_num = False, False, None, None
    group_page_next, group_page_prev = None, None

    # default would be group by 1 at group number 0
    num_groups = ceil(num_pages / group_by) if group_by > 0 else num_pages
    start, stop = 1, num_groups + 1

    # if given group_num is more than the
    # determined number of groups, set a default
    # value for it which is 1. This will give
    # default value of group number 1 to process
    # group pagination.
    if group_num > num_groups or group_num < 0:
        group_num = 1

    # check if given group_num is within num_groups
    # and calculate new start and stop value
    if group_num <= num_groups and group_num > 0:
        res = group_num * group_by
        # list(range((6 + 1) - 3, (6 + 1))) or list(range(4, 7))
        start = (res + 1) - group_by
        stop = res + 1

        if res > num_pages:
            stop = num_pages + 1

    page_list = list(range(start, stop))

    # check if has_next group
    if group_num < num_groups and group_num > 0:
        has_next = True
        next_num = group_num + 1
        group_page_next = page_list[len(page_list) - 1] + 1
    
    # check if has_prev group
    if group_num > 1 and group_num <= num_groups:
        has_prev = True
        prev_num = group_num - 1
        group_page_prev = page_list[0] - 1
    
    grouped_pagination = {
        'grouped_pagination': page_list,
        'group_has_next': has_next,
        'group_has_prev': has_prev,
        'group_next': next_num,
        'group_prev': prev_num,
        'group_page_next': group_page_next,
        'group_page_prev': group_page_prev,
        'group_curr': group_num,
    }

    return grouped_pagination

class ModifiedPaginateListView(generic.ListView):
    # TODO: Check if this is needed.
    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()
        
        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if self.get_paginate_by(self.object_list) is not None and hasattr(self.object_list, 'exists'):
                is_empty = not self.object_list.exists()
            else:
                is_empty = not self.object_list
                if is_empty:
                    raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.") % {
                        'class_name': self.__class__.__name__,
                        })
        # TODO: By given page_num, determine the current group_number

        context = self.get_context_data()
        if context['is_paginated']:
            page_obj = context['page_obj']
            num_pages = page_obj.paginator.num_pages

            # give default value of 1
            group_num = int(request.GET.get('group_num', 1))

            context.update(group_pagination(num_pages, group_num))

        return self.render_to_response(context)


class APITransactException(Exception):
    def __init__(self, *args, **kwargs):
        if 'code' in kwargs:
            self.code = kwargs.pop('code')
        
        if 'message' in kwargs:
            self.message = kwargs.pop('message')
        super(APITransactException, self).__init__(*args, **kwargs)


def log(view_name, action, data, 
    status, status_code, logger_type,
    success=False, message=''):

    if not isinstance(view_name, str):
        raise ValueError("View name should be string.")

    if not isinstance(data, dict):
        raise ValueError("Data should be dictionary type.")
    
    # TODO: determine all logger types   
    if logger_type not in LOGGER_TYPES:
        raise ValueError("logger_type not valid.")
    
    if logger_type == 'info':
        return _("{0},{1},{2},{3},{4},{5}")\
            .format(view_name, action, success, 
                status, status_code, json.dumps(data))
    elif logger_type == 'warning':
        return _("WARNING: ")

    # debug
    return _("view_name: {0}, action: {1}, status: {2}, "
            "status_code: {3} data: {4}, success: {5}"
            "message: {6}")\
            .format(view_name, action, status, status_code,
                    data, success, message)