from django import forms
import datetime
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from catalog.models import BookInstance, Profile
from django.core.validators import FileExtensionValidator, RegexValidator


class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(help_text="Enter a date between now and 4 weeks")

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        # Check if a date is not in the past.
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        # Check if a date is in the allowed range (+4 weeks from today).
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        # Remember to always return the cleaned data.
        return data

    class Meta:
        model = BookInstance
        fields = ['due_back']
        labels = {'due_back': _('Renewal date')}
        help_texts = {'due_back': _('Enter a date between now and 4 weeks (default 3)')}


class EmailForm(forms.Form):
    email_id = forms.EmailField(help_text="Enter a valid email ID to get the book")


class SearchForm(forms.Form):
    text = forms.CharField(max_length=50, help_text="Type to Search")


class ProfileForm(forms.ModelForm):
    image = forms.ImageField(
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpeg', 'jpg'])],
        required=False
    )
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,10}$',
                                 message="Phone number must be entered in the format: '+919999999999'. Utpo 10 digits")
    number = forms.CharField(validators=[phone_regex], max_length=10, required=False)
    # fav_book = forms.MultipleChoiceField(choices=FAV_BOOK_CHOICES)

    class Meta:
        model = Profile
        fields = ['image', 'number']
        labels = {
                  'image': _('Profile Photo'),
                  'number': _('Mobile Number'),
                  # 'fav_book': _('Favourite Books'),
                  }
        help_texts = {
                      'image': _('Upload a jpeg or png Image'),
                      'number': _('Enter 10 digit number starting with 9'),
                      # 'fav_book': _('Select Multiple Books')
        }
