from django.views.generic import View, TemplateView
from django.forms.models import ModelForm
from django.shortcuts import HttpResponse, Http404
from django.http.response import HttpResponseRedirect
from editapp.models import Entry
from django.template import Template, RequestContext
from django.template.response import TemplateResponse
from django.views.generic import ListView
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

model = ContentType.objects.get_for_id(7)
print('model name:', model.model_class().get_full_name())
print('label:', Entry._meta.label)
print('app_label:', Entry._meta.app_label)
print('verbose_name:', Entry._meta.verbose_name)

class ConflictTemplateResponse(TemplateResponse):
  def __init__(self, *args, **kwargs):
    kwargs['status'] = 409
    super().__init__(*args, **kwargs)

class BadRequestTemplateResponse(TemplateResponse):
  def __init__(self, *args, **kwargs):
    kwargs['status'] = 409
    super().__init__(*args, **kwargs)


class EditForm(ModelForm):
  class Meta:
    model = Entry
    fields = ['title', 'text']

  def clean(self):
    return self.cleaned_data

class EditView(TemplateView):
  
  @staticmethod
  def get_url_name():
    return Entry.get_full_name()
  
  def get(self, request, *args, **kwargs):
    action = 'view'
    
    if 'action' in request.GET:
      action = request.GET['action']

    base = '://'.join((request.scheme, request.get_host()))
    url = base + reverse(self.get_url_name(), kwargs={'title': kwargs['title']})
    
    if action == 'create':
      if Entry.objects.filter(title__exact=kwargs['title']).exists():
        return HttpResponse(status=409)
      form = EditForm(initial={'title': kwargs['title']})
      self.template_name = "edit-page.html"
      self.extra_context = {
        'page': {
          'title': kwargs['title'],
          'form': form
        },
        'form': {
          'action': 'create',
          'url': url,
        }
      }
    elif action == 'edit':
      try:
        entry = Entry.objects.get(title__exact=kwargs['title'])
      except Entry.DoesNotExist:
        raise Http404
      form = EditForm(initial={'title': entry.title, 'text': entry.text})
      self.template_name = "edit-page.html"
      self.extra_context = {
        'page': {
          'title': entry.title,
          'form': form
        },
        'form': {
          'action': 'update',
          'url': url,
        }
      }
    else:
      self.template_name = "view-page.html"
      try:
        entry = Entry.objects.get(title__exact=kwargs['title'])
      except Entry.DoesNotExist:
        raise Http404
      template = Template(entry.text)
      context = RequestContext(request)
      self.extra_context = {
        'page': {
          'title': entry.title,
          'text': template.render(context)
        }
      }
      
    return super().get(request, *args, **kwargs)
  
  def post(self, request, *args, **kwargs):
    self.template_name = "edit-page.html"
    form = EditForm(request.POST)
    action = 'update'
    if 'action' in request.POST:
      action = request.POST['action']
    
    if form.is_valid():
      try:
        entry = Entry.objects.get(title__exact=kwargs['title'])
      except Entry.DoesNotExist:
        entry = None
      if action == 'create':
        if entry is not None:
          self.response_class = ConflictTemplateResponse
        entry = Entry()
      elif entry is None:
        raise Http404
      
      entry.title = form.cleaned_data['title']
      entry.text = form.cleaned_data['text']
      entry.save()
      base = '://'.join((request.scheme, request.get_host()))
      url = base + reverse(self.get_url_name(), kwargs={'title': entry.title})
      return HttpResponseRedirect(url)
    
    else:
      self.response_class = BadRequestTemplateResponse
    
    self.extra_context = {
      'page': {
        'title': kwargs['title'],
        'form': form
      },
      'form': {
        'action': action,
      }
    }
    
    return super().get(request, *args, **kwargs)

class EntriesListView(TemplateView):
  template_name = 'entries-list.html'
  
  def get(self, request, *args, **kwargs):
    queryset = Entry.objects.all()
    
    entires_list = []
    base  = '://'.join((request.scheme, request.get_host()))
    for entry in queryset:
      entires_list.append({
        'title': entry.title,
        'url': base + reverse(EditView.get_url_name(), kwargs={'title': entry.title})})
    self.extra_context = {
      'page': {
        'title': 'Existing entries list',
        'entires_list': entires_list,
      }
    }
    return super().get(request, *args, **kwargs)
  
  
class CreateEntryView(TemplateView):
  def get(self, request, *args, **kwargs):
    form = EditForm()
    self.template_name = "edit-page.html"
    base = '://'.join((request.scheme, request.get_host()))
    url = base + reverse(EditView.get_url_name(), kwargs={'title': kwargs['title']})

    self.extra_context = {
      'page': {
        'title': 'Create entry',
        'form': form
      },
      'form': {
        'action': 'create',
        'url': url,
      }
    }
    return super().get(request, *args, **kwargs)

class EntryDispatcher(View):
  def get(self, request, *args, **kwargs):
    action = 'view'
    if 'action' in request.GET:
      action = request.GET['action']
    if action == 'create':
      class_name = CreateEntryView
    else:
      class_name = EntriesListView
    return class_name.as_view()(request, *args, **kwargs)
