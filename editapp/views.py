from django.shortcuts import render
from django.views.generic import TemplateView
from django.forms.models import ModelForm
from django.shortcuts import HttpResponse, Http404
from django.http.response import HttpResponseBadRequest, HttpResponseRedirect
from editapp.models import Entry
from django.template import Template, RequestContext

class HttpConflict(HttpResponse):
  status_code = 409

class EditForm(ModelForm):
  class Meta:
    model = Entry
    fields = ['title', 'text']


class EditView(TemplateView):
  
  def get(self, request, *args, **kwargs):
    action = 'view'
    if 'action' in request.GET:
      action = request.GET['action']
    
    if action == 'create':
      if Entry.objects.filter(title__exact=kwargs['title']).exists():
        return HttpConflict()
      form = EditForm(initial={'title': kwargs['title']})
      self.template_name = "edit-page.html"
      self.extra_context = {
        'page': {
          'title': kwargs['title'],
          'form': form
        },
        'form': {
          'action': 'create',
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
          self.response_class = HttpConflict
        entry = Entry()
      elif entry is None:
        raise Http404
      
      entry.title = form.cleaned_data['title']
      entry.text = form.cleaned_data['text']
      entry.save()
      base = '://'.join((request.get_host(), request.scheme))
      url = '/'.join((base, entry.title))
      return HttpResponseRedirect(url)
    
    else:
      self.response_class = HttpResponseBadRequest
    
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
