import django_tables2 as tables

from .models import Student


class StudentTable(tables.Table):
    id = tables.Column(linkify=True, attrs={"td": {"align": "left"}})
    name = tables.Column(linkify=True, attrs={"td": {"align": "left"}}, verbose_name='Name')
    twitter_account = tables.Column(linkify=dict(viewname='redirect-twitter',
                                                args=[tables.A('twitter_account')]), 
                                    attrs={"td": {"align": "left"}})
    updated_date = tables.Column(attrs={"td": {'class': 'date-column'}})
    delete = tables.TemplateColumn(
        verbose_name='',
        template_name='dashboard/delete_button.html',
        orderable=False,
        attrs={"td": {'class': 'delete-column'}}
        )
    
    bipolarity = tables.Column(linkify=False, attrs={"td": {"align": "middle"}}, verbose_name='Bipolarity')
    has_frequency_changed = tables.Column(linkify=False, attrs={"td": {"align": "middle"}}, verbose_name='Mood swings')
    consistent_negativity = tables.Column(linkify=False, attrs={"td": {"align": "middle"}}, verbose_name='Consistent negativity')
    timing = tables.Column(linkify=False, attrs={"td": {"align": "middle"}}, verbose_name='Night activity')
    suicidal = tables.Column(linkify=False, attrs={"td": {"align": "middle"}}, verbose_name='Suicidal')

    class Meta:
        model = Student
        exclude = ('uid', 'caregiver', 'mean_frequency_score', 'total_number_of_tweets', 
                  'twitter_account', 'updated_date', 'has_frequency_changed')
