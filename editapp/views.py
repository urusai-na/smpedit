from django.shortcuts import render
from django.views.generic import TemplateView
from django.forms.models import ModelForm
from django.shortcuts import HttpResponse, Http404
from editapp.models import Entry
from django.template.backends.django import Template


class EditForm(ModelForm):
  class Meta:
    fields = ['title', 'text']

class EditView(TemplateView):
  
  template_name = "edit-page.html"
  
  def get(self, request, *args, **kwargs):
    action = 'view'
    if 'action' in request.GET:
      action = request.GET['action']
    
    if action == 'create':
      self.template_name = "edit-page.html"
      
      form = EditForm()
      if Entry.objects.filter(title__exact=kwargs['title']).exists():
        raise Http404
      template = Template(entry.text)
      self.extra_context = {
        'entry': {
          'form': EditForm()
        }
      }
    elif action == 'edit':
      entry = Entry.objects.get(title__exact=kwargs['title'])
    else:
      self.template_name = "view-page.html"
      try:
        entry = Entry.objects.get(title__exact=kwargs['title'])
      except Entry.DoesNotExist:
        raise Http404
      template = Template(entry.text)
      self.extra_context = {
        'entry': {
          'text': template.render(request=request)
        }
      }
      
    return super().get(request=request, *args, **kwargs)
  
  def post(self, request, *args, **kwargs):
    self.template_name = "edit-page.html"
    return HttpResponse('ok')
  
  def get_context_data(self, **kwargs):
    return {
      'page': {
        'title': "Edit page title"
      }
    }
