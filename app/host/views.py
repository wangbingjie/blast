from django.shortcuts import render
from .forms import TransientSearchForm
from .models import Transient, ExternalResourceCall


def transient_list(request):
    transients = Transient.objects.all()

    if request.method == 'POST':
        form = TransientSearchForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data['name']
            if name != 'all':
                transients = Transient.objects.filter(tns_name__contains=name)
    else:
        form = TransientSearchForm()

    transients = transients.order_by('-public_timestamp')[:100]
    context = {'transients': transients, 'form': form}
    return render(request, 'transient_list.html', context)


def analytics(request):
    calls = ExternalResourceCall.objects.all()
    return render(request, 'analytics.html', {'resource_calls': calls})


def results(request, slug):
    transients = Transient.objects.all()
    transient = transients.get(tns_name__exact=slug)

    return render(request, 'results.html', {'transient': transient})
