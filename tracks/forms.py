from django import forms
from .models import Group, Track

GROUP_COLORS = [
    ('#2D6A4F', 'Forest Green'),
    ('#1B4332', 'Dark Pine'),
    ('#40916C', 'Sage'),
    ('#D62828', 'Crimson'),
    ('#023E8A', 'Deep Blue'),
    ('#7B2D8B', 'Purple'),
    ('#E76F51', 'Terracotta'),
    ('#264653', 'Dark Teal'),
    ('#6D4C41', 'Brown'),
    ('#37474F', 'Slate'),
]

BS = {'class': 'form-control'}
BS_SELECT = {'class': 'form-select'}


class GroupForm(forms.ModelForm):
    cover_color = forms.ChoiceField(
        choices=GROUP_COLORS,
        initial='#2D6A4F',
        widget=forms.RadioSelect(attrs={'class': 'color-radio d-none'}),
    )

    class Meta:
        model = Group
        fields = ['name', 'description', 'is_private', 'cover_color']
        widgets = {
            'name': forms.TextInput(attrs={**BS, 'placeholder': 'e.g. Alps Trekkers 2024'}),
            'description': forms.Textarea(attrs={**BS, 'rows': 3,
                                                  'placeholder': 'What is this group about?'}),
            'is_private': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
        }


class TrackUploadForm(forms.ModelForm):
    class Meta:
        model = Track
        fields = ['title', 'description', 'gpx_file', 'activity_type']
        widgets = {
            'title': forms.TextInput(attrs={**BS, 'placeholder': 'e.g. Mont Blanc Summit Trail'}),
            'description': forms.Textarea(attrs={**BS, 'rows': 3,
                                                   'placeholder': 'Describe your adventure...'}),
            'gpx_file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.gpx'}),
            'activity_type': forms.Select(attrs=BS_SELECT),
        }
