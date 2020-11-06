from django import forms
from .models import Report


class ReportForm(forms.ModelForm):

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ReportForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Report
        fields = ['game', 'discription']
        widgets = {
            'discription': forms.Textarea(attrs={'rows': 4, 'cols': 15}),
        }

    def save(self):
        data = self.cleaned_data
        game = data['game']
        discription = data['discription']
        report = Report(game=game, discription=discription,
                        reported_by=self.user)
        report.save()
