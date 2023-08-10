from django.shortcuts import render
from django.views import generic


# Create your views here.


class Index(generic.View):
    def get(self, request):
        if request.method == 'GET':
            return render(request, 'index.html')
