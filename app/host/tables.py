from .models import Transient
import django_tables2 as tables

class TransientTable(tables.Table):

    name = tables.TemplateColumn(
        "<a href=\"{% url 'results' record.name %}\">{{ record.name }}</a>",
        verbose_name='Name',orderable=True,order_by='name')

    
    prefix = tables.Column(accessor='tns_prefix',
                              verbose_name='Prefix',orderable=True,order_by='prefix')

    disc_date = tables.Column(accessor='public_timestamp',
                              verbose_name='Discovery Date',orderable=True,order_by='ra_deg')


    ra_string = tables.Column(accessor='ra',
                              verbose_name='Right Ascension',orderable=True,order_by='ra_deg')
    
    dec_string = tables.Column(accessor='dec',
                               verbose_name='Declination',orderable=True,order_by='dec_deg')
    
    progress = tables.TemplateColumn(
"""          {% if record.progress == 0 %}
              Waiting
          {% elif record.progress == 100 %}
            <div class="progress">
              <div class="progress-bar bg-success" role="progressbar" style="width: {{record.progress}}%;" aria-valuenow="{{transient.progress}}" aria-valuemin="0" aria-valuemax="100">{{record.progress}}%</div>
            </div>
          {% else %}
            <div class="progress">
              <div class="progress-bar" role="progressbar" style="width: {{record.progress}}%;" aria-valuenow="{{record.progress}}" aria-valuemin="0" aria-valuemax="100">{{record.progress}}%</div>
            </div>
          {% endif %}
""",
        verbose_name="Progress",orderable=False,order_by='progress')
    
    
    class Meta:
        model = Transient
        fields = ()

        template_name='django_tables2/bootstrap.html'
        attrs = {
            'th' : {
                '_ordering': {
                    'orderable': 'sortable', # Instead of `orderable`
                    'ascending': 'ascend',   # Instead of `asc`
                    'descending': 'descend'  # Instead of `desc`
                }
            },
            'class': 'table table-bordered table-hover',
            'id': 'k2_transient_tbl',
            "columnDefs": [
                {"type":"title-numeric","targets":1},
                {"type":"title-numeric","targets":2},
            ],
            "order": [[ 3, "desc" ]],
        }
