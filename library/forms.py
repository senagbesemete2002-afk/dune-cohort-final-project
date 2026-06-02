from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from .models import Book, Category


class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('staff', 'Staff'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, label='Register as')

    class Meta(UserCreationForm.Meta):
        model = UserCreationForm.Meta.model
        fields = UserCreationForm.Meta.fields


class BookForm(forms.ModelForm):
    new_category = forms.CharField(
        max_length=100,
        required=False,
        label='New category',
        help_text='If the category does not exist yet, type it here.'
    )

    class Meta:
        model = Book
        fields = ['category', 'new_category', 'title', 'author', 'description', 'cover_image', 'available_copies']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].required = False
        self.fields['category'].empty_label = 'Select existing category (or enter a new one)'

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        new_category = cleaned_data.get('new_category')

        if not category and not new_category:
            raise ValidationError('Please select an existing category or enter a new category.')

        return cleaned_data

    def save(self, commit=True):
        book = super().save(commit=False)
        new_category = self.cleaned_data.get('new_category')
        category = self.cleaned_data.get('category')

        if new_category:
            category, _ = Category.objects.get_or_create(name=new_category.strip())
            book.category = category
        elif category:
            book.category = category

        if commit:
            book.save()

        return book