from django import forms
# from django.core.validators import FileExtensionValidator, RegexValidator
# from improve.models import Profile


# class ProfileForm(forms.ModelForm):
#     image = forms.ImageField(validators=[FileExtensionValidator(allowed_extensions=['png','jpeg','jpg'])])
#     number = forms.CharField(regex=r'^\+?1?\d{9,10}$',
#                              message="Phone number must be entered in the format: '+919999999999'. Utpo 10 digits")