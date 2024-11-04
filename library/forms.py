# forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    date_of_birth = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    phone = forms.CharField(max_length=15, required=False)
    address = forms.CharField(max_length=100, required=False)
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'date_of_birth', 
                  'phone', 'address', 'profile_picture', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
            profile = UserProfile.objects.create(
                user=user,
                phone=self.cleaned_data['phone'],
                address=self.cleaned_data['address'],
                date_of_birth=self.cleaned_data['date_of_birth'],
                profile_picture=self.cleaned_data['profile_picture'],
            )
            profile.save()
        return user

from django import forms
from datetime import datetime, timedelta
from django.utils import timezone

from django import forms
from .models import BookIssue

class BookIssueForm(forms.ModelForm):
    book_id = forms.CharField(max_length=10, label='Book ID')
    book_copy_no = forms.CharField(max_length=10, label='Copy Number')

    class Meta:
        model = BookIssue
        fields = ['book_id', 'book_copy_no']

    def clean(self):
        cleaned_data = super().clean()
        book_id = cleaned_data.get("book_id")
        book_copy_no = cleaned_data.get("book_copy_no")

        # Ensure both fields are filled
        if not book_id or not book_copy_no:
            raise forms.ValidationError("Both Book ID and Copy Number are required.")

        return cleaned_data


from django import forms
from .models import Goal, Book

class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['goal_name', 'books', 'target_completion_date']
        widgets = {
            'books': forms.CheckboxSelectMultiple,  # Users can select multiple books
            'target_completion_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }



from django import forms
from .models import CommunityPost

class CommunityPostForm(forms.ModelForm):
    class Meta:
        model = CommunityPost
        fields = ['title', 'description', 'video', 'image', 'document', 'research_link']

    def clean(self):
        cleaned_data = super().clean()
        if not any([cleaned_data.get('video'), cleaned_data.get('image'), cleaned_data.get('document'), cleaned_data.get('research_link')]):
            raise forms.ValidationError("Please upload or provide at least one type of content.")
        return cleaned_data
       