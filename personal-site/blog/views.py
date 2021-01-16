import datetime

from django.http import Http404, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic, View
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AnonymousUser
from django.db import IntegrityError

from blog.models import Post, Category, Tag, Decipher
from blog.forms import PostForm, PostSearchForm, DecipherForm

from personal_site_api.filters import PostFilter
from core.utils import (
    ModifiedSearchListView, load_html_doc,
    get_tags, assign_attr_to_tag,
    append_classes_to_tag, wrap_element,
    replace_element
)


# Function based views here.
def delete_post(request, pk):
    if Post.objects.filter(pk=pk).exists():
        post = Post.objects.get(pk=pk)
        post.delete()
        return redirect(reverse('post-list'))
    return Http404

def get_random_tags(request):
    # TODO: This view will showcase randomize tags and when you click,
    # it will show the corresponding post.

    context = {}
    if 'tag' in request.GET.keys():
        if isinstance(request.user, AnonymousUser):
            posts = Post.published_objects.filter(tags__tag=request.GET['tag'])
        else:
            posts = Post.objects.filter(tags__tag=request.GET['tag'])
        context['posts'] = posts
    
    # TODO: we can change how tags we want to appear
    # for now default value of 10.
    from random import choice
    tag_list = Tag.objects.values_list('tag', flat=True).distinct()
    tags = []
    while len(tags) < 10:
        try:
            random_tag = choice(tag_list)
            if random_tag not in tags:
                tags.append(random_tag)

            if len(tag_list) < 10 and len(tags) == len(tag_list):
                break
        except IndexError:
            break

    context['tags'] = tags

    if 'prev_page_session' in request.GET.keys():
        context['prev_page_session'] = request.GET['prev_page_session']

    context['post_list'] = request.GET.get('post_list', '0')

    return render(request, 'blog/post_random_tags.html', context)

def get_deciphers_by_post(request, pk):
    context = {}
    post = Post.objects.get(pk=pk)
    if not post:
        raise Http404

    if request.method == 'GET':
        decipher_qs = post.deciphers.all()
        paginator, page, queryset, is_paginated = paginate_queryset(request=request,
                                                                    queryset=decipher_qs,
                                                                    page_size=10)
        context.update({
                'post': post,
                'paginator': paginator,
                'page_obj': page,
                'is_paginated': is_paginated,
                'object_list': decipher_qs,
                'deciphers': queryset
            })

        if 'prev_page_session' in request.GET.keys():
            context['prev_page_session'] = request.GET['prev_page_session']

        context['post_list'] = request.GET.get('post_list', '0')

    return render(request, 'blog/post_decipher_list.html', context)


# Class based views here
class PostListView(ModifiedSearchListView):
    model = Post
    paginate_by = 10
    context_object_name = 'posts'
    template_name = 'blog/post_list.html'
    filter_class = PostFilter

    def get_queryset(self):
        """
        Return the list of items for this view.
        The return value must be an iterable and may be an instance of
        `QuerySet` in which case `QuerySet` specific behavior will be enabled.
        """
        # We will not allow queryset value
        self.queryset = None
        
        # We will require model 
        if not self.model:
            raise ImproperlyConfigured(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, or override "
                "%(cls)s.get_queryset()." % {
                    'cls': self.__class__.__name__
                }
            )

        if isinstance(self.request.user, AnonymousUser):
            queryset = self.model.published_objects.all()
        else:
            queryset = self.model._default_manager.all()
            
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)
        return queryset

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

        context = self.get_context_data()

        # add form here
        context['form'] = PostSearchForm

        return self.render_to_response(context)


class PostDetailView(generic.DetailView):
    model = Post
    template_name = 'blog/post_detail.html'

    def get(self, request, *args, **kwargs):

        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        deciphers = Decipher.objects.filter(post=self.object)
        context['deciphers'] = deciphers

        #print(self.object.tags.values_list('tag', flat=True))
        more_blogs = Tag.objects.filter(tag__in=self.object.tags  \
                    .values_list('tag', flat=True))               \
                    .order_by('-post__published_date')             \
                    .values('post__id', 'post__title')            \
                    .exclude(post__id=self.object.id)[:3]
        #print("MORE BLOGS", more_blogs)
        context['more_blogs'] = more_blogs

        if 'prev_page_session' in request.GET.keys():
            context['prev_page_session'] = request.GET['prev_page_session']

        # assign value to post_list which will be passed to template
        context['post_list'] = request.GET.get('post_list', '0')

        return self.render_to_response(context)


class PostFormView(LoginRequiredMixin, generic.FormView):
    login_url = '/login'

    form_class = PostForm
    template_name = 'blog/post_form.html'
    success_url = '/blog/'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        request_get_keys = request.GET.keys()

        post = None
        if form.is_valid():
            post_data = request.POST.dict()
            # tags from form
            tags = request.POST.getlist('tags')
            
            try:
                # TODO: Make DateFormat UTC
                post_data['publish']
                published_date = datetime.datetime.now()
            except KeyError:
                published_date = None

            if 'id' in request_get_keys:
                try:
                    post = get_object_or_404(Post, pk=request.GET['id'])
                    
                    if not post:
                        raise Http404

                    # TODO: figure out getting string of html content of returned soup object
                    processed_content = process_decipher_in_post(post, post_data['content'])
                    post.category = Category.objects.get(id=post_data['category_id'])
                    post.title = post_data['title']
                    post.content = processed_content
                    post.published_date = published_date
                    post.save()
                    # tags recorded in database
                    post_tags = post.tags.all().values_list('tag', flat=True)
                    
                    # delete tag in database if tag was removed from form
                    for post_tag in post_tags:
                        if post_tag not in tags:
                            Tag.objects.get(post=post, tag=post_tag).delete()

                    # insert tag if not existing in tags of post
                    for tag in tags:
                        if tag not in post_tags:
                            Tag.objects.create(post=post, tag=tag)
                except ValueError:
                    pass
            else:
                data = {
                    'category_id': post_data['category_id'],
                    'title': post_data['title'],
                    'content': post_data['content'],
                    'published_date': published_date
                }
                temp_content = post_data['content']

                post = Post.objects.create(**data)
                
                # process decipher span
                processed_content = process_decipher_in_post(post, temp_content)
                post.content = processed_content
                post.save()

                post_tags = []
                if tags:
                    for tag in tags:
                        post_tags.append(Tag(post=post, tag=tag))

                Tag.objects.bulk_create(post_tags)
        
        redirect_url = "{0}?id={1}".format(reverse('post-form'), post.id)
        if 'prev_page_session' in request_get_keys:
            redirect_url += '&prev_page_session=' + request.GET['prev_page_session']
        
        redirect_url += '&post_list=' + request.GET.get('post_list', '0')


        return redirect(redirect_url)

    def get(self, request, *args, **kwargs):
        form = self.form_class
        tags = []
        context = {}
        request_get_keys = request.GET.keys()

        tags_autocomplete = Tag.objects.distinct().values_list('tag', flat=True)

        tag_objects = []
        if 'id' in request_get_keys:
            try:
                post = get_object_or_404(Post, pk=request.GET['id'])
                tag_objects = Tag.objects.filter(post=post)
                tags = list(tag_objects.values('tag'))

                if not post:
                    raise Http404
                
                form = self.form_class({
                    'category_id': post.category.id,
                    'title': post.title,
                    'content': post.content,
                    'publish': True if post.published_date else False
                })

                context['post_id'] = post.id

            except ValueError:
                pass
        
        if 'prev_page_session' in request_get_keys:
            context['prev_page_session'] = request.GET['prev_page_session']

        # assign value to post_list which will be passed to template
        context['post_list'] = request.GET.get('post_list', '0')

        context['form'] = form
        context['tag_objects'] = tag_objects
        context['tags'] = tags
        context['tags_autocomplete'] = convert_list_for_chipauto(tags_autocomplete)

        return self.render_to_response(context)


class PostDecipherFormView(LoginRequiredMixin, generic.FormView):
    
    form_class = DecipherForm
    template_name = 'blog/post_decipher_form.html'

    def post(self, request, post_id, decipher_id, *args, **kwargs):
        form = self.form_class(request.POST)
        decipher = Decipher.objects.get(id=decipher_id, post__id=post_id)
        if not decipher:
            raise Http404

        if form.is_valid():
            data = request.POST.copy()

            clue = data.get('clue', None)
            code = data.get('code', None)
            clue_photo_base64 = data.get('clue_photo', None)
            clue_photo_name = data.get('clue_photo_name', None)

            import base64
            import os
            from django.conf import settings

            # if clues does not exists in media directory, create one
            clues_media_dir = "{}/{}".format(settings.MEDIA_ROOT, 'clues')
            if not os.path.isdir(clues_media_dir):
                os.mkdir(clues_media_dir)

            _, imgstring = clue_photo_base64.split(",")
            imgfilename = "{}.jpg".format(clue_photo_name) if not clue_photo_name.endswith(".jpg") else clue_photo_name
            imgdata = base64.b64decode(imgstring)
            # e.g., /home/user/../personal-site/media/clues/filename.jpg
            img_fullpath = "{}/{}".format(clues_media_dir, imgfilename)
            # e.g., /media/clues/filename.jpg
            img_url = "{}clues/{}".format(settings.MEDIA_URL, imgfilename)

            # check if file exists already, then delete
            if os.path.isfile(img_fullpath):
                os.remove(img_fullpath)

            with open(img_fullpath, "wb") as imagefile:
                imagefile.write(imgdata)

            decipher.clue = clue
            decipher.clue_photo_filename = imgfilename
            decipher.clue_photo_fullpath = img_fullpath
            decipher.clue_photo_url = img_url
            decipher.code = code
            decipher.save()

        return redirect(reverse('post-decipher-form', kwargs={'post_id': post_id, 'decipher_id': decipher_id}))

    def get(self, request, post_id, decipher_id, *args, **kwargs):
        form = self.form_class
        decipher = Decipher.objects.get(id=decipher_id, post__id=post_id)
        if not decipher:
            raise Http404

        form = self.form_class({
            'clue': decipher.clue,
            'clue_photo_name': decipher.clue_photo_filename,
            'code': decipher.code
        })

        context = {'form': form}

        context['decipher'] = decipher

        # post list page session
        if 'prev_page_session' in request.GET.keys():
            context['prev_page_session'] = request.GET['prev_page_session']
        
        # decipher page session
        if 'prev_decipher_page_session' in request.GET.keys():
            context['prev_decipher_page_session'] = request.GET['prev_decipher_page_session']
        context['post_list'] = request.GET.get('post_list', '0')
        return self.render_to_response(context)


# None view functions
def paginate_queryset(request, queryset, page_size, orphans=0, allow_empty=True, page_kwarg='page'):
    """
    Code coming from the following attributes and methods under ListView CBV.

    attributes: allow_empty, paginate_orphans, paginator_class

    Reference:
    https://ccbv.co.uk/projects/Django/2.1/django.views.generic.list/ListView/
    
    Arguments:
        queryset {[type]} -- [description]
        page_size {[type]} -- [description]
    """
    from django.core.paginator import Paginator

    paginator = Paginator(queryset, page_size, orphans=orphans, allow_empty_first_page=allow_empty)
    page = request.GET.get(page_kwarg) or 1

    try:
        page_number = int(page)
    except ValueError:
        if page == 'last':
            page_number = paginator.num_pages
        else:
            raise Http404(_("Page is not 'last', nor can it be converted to an int."))
    try:
        page = paginator.page(page_number)
        return (paginator, page, page.object_list, page.has_other_pages)
    except InvalidPage as e:
        raise Http404(_('Invalid page (%(page_number)s): %(message)s') %{
            'page_number': page_number,
            'message': str(e)
        })

def convert_list_for_chipauto(item_list):
    # converts list for autocomplete initialization
    # for materialize in this format
    # { 'Microsoft': null, 'Google': null, 'Apple': null}
    autocomplete = {}
    for item in item_list:
        autocomplete[item] = ''
    
    return autocomplete

def process_decipher_in_post(post, post_content):
    # load html doc in to readable python objects 
    soup = load_html_doc(post_content)

    # will only process div element with class 'decipher'
    deciphers = get_tags(soup, 'span.decipher')

    # decipher ids from content
    content_decipher_ids = []

    # create or update
    if deciphers:
        for decipher in deciphers:
            # To avoid IntegrityError (null value)
            if decipher.string:
                try:
                    # if key 'id' doesn't exist, maybe add to database
                    decipher_id = int(decipher['id'][11:])

                    instance = Decipher.objects.get(id=decipher_id)
                    # update decipher
                    instance.hidden_text = decipher.string
                    instance.save()

                    # if id was successfully parsed to int and is
                    # existing append to content_decipher_ids list
                    # so they would not be deleted later
                    content_decipher_ids.append(decipher_id)
                except (KeyError, ValueError, Decipher.DoesNotExist):
                    # save decipher to db
                    instance = Decipher.objects \
                                            .create(post=post, hidden_text=decipher.string)

                    decipher_name = 'decipherme-' + str(instance.id)
                    assign_attr_to_tag(
                        tag=decipher,
                        target_attr='id',
                        attr_val= decipher_name
                    )

                    # update decipher name once saved
                    instance.name = decipher_name
                    instance.save()

                    # also append newly saved decipher's id so
                    # it would not be deleted later
                    content_decipher_ids.append(instance.id)
            else:
                decipher.decompose()

    # get existing id of deciphers from given post
    post_decipher_ids = Decipher.objects.filter(post=post).values_list('id', flat=True)

    # delete all deciphers from db that are no longer found
    # on content (from content_decipher_ids)
    for post_decipher_id in post_decipher_ids:
        if post_decipher_id not in content_decipher_ids:
            instance = Decipher.objects.get(id=post_decipher_id)
            instance.delete()

    return soup.prettify(formatter="html5")

