from django import forms
from .models import Position

 
class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['position_name', 'description', 'program']
        widgets = {
            'position_name': forms.TextInput(attrs={'class': 'form-input t_d'}),
            'description': forms.Textarea(attrs={'class': 'form-input t_d', 'rows': 4}),
            'program': forms.TextInput(attrs={'class': 'form-input t_d'}),
        } 