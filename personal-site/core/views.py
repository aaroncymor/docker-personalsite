from django.shortcuts import redirect
from django.views import generic
from django.contrib.auth import logout, views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings

from blog.models import Post

# Create your views here.

class HomeView(generic.TemplateView):
    template_name = 'home.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        # Queryset for blogs - latest two (2) posts
        posts = Post.published_objects.all().order_by('-timestamp')[:3]

        # Assign to context
        context['posts'] = posts

        return self.render_to_response(context)


class DashboardView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'personal_site/dashboard.html'


class LoginView(auth_views.LoginView):
    template_name = 'personal_site/login.html'

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.get_form()
        if form.is_valid():
            request.session['authorized'] = True
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


def logout_view(request):
    logout(request)
    return redirect('login')