from django.shortcuts import render
from django.http import HttpResponse
from .forms import TransientForm

from bokeh.plotting import figure, output_file, show
from bokeh.embed import components

def submit_transient(request):

    if request.method == 'POST':
        form = TransientForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']

            x = [1, 3, 5, 7, 9, 11, 13]
            y = [1, 2, 3, 4, 5, 6, 7]
            title = 'y = f(x)'

            plot = figure(title=title,
                          x_axis_label='X-Axis',
                          y_axis_label='Y-Axis',
                          plot_width=400,
                          plot_height=400)

            plot.line(x, y, legend='f(x)', line_width=2)
            # Store components
            script, div = components(plot)


            return render(request, 'results.html', {'script': script, 'div': div})


    form = TransientForm()
    return render(request, 'form.html', {'form': form})


