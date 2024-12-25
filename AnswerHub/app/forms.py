from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile, Question, Tag, TagQuestion, Answer

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    next = forms.CharField(widget=forms.HiddenInput(), required=False)  

    def clean_username(self):
        return self.cleaned_data['username'].rstrip()


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirmation = forms.CharField(widget=forms.PasswordInput)
    avatar = forms.ImageField(required=False)  

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirmation') 

    def clean(self):
        data = super().clean()

        if data.get('password') != data.get('password_confirmation'):
            raise ValidationError('Passwords do not match')

        return data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()


            avatar = self.cleaned_data.get('avatar')
            print("DEBUG: avatar from cleaned_data ->", avatar)
            
            if avatar:
                Profile.objects.create(user=user, avatar=avatar)
            else:
                Profile.objects.create(user=user)  

        return user


class UserProfileEditForm(forms.ModelForm):
    avatar = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email')

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        
        if commit:
            user.save()

            profile, created = Profile.objects.get_or_create(user=user)

            avatar = self.cleaned_data.get('avatar')
            if avatar:
                profile.avatar = avatar
                profile.save()

        return user


class QuestionForm(forms.ModelForm):
    tags = forms.CharField(
        help_text="Введите от 1 до 3 тегов через запятую.",
        widget=forms.TextInput(attrs={"placeholder": "тег1, тег2, тег3"})
    )
    
    class Meta:
        model = Question
        fields = ['title', 'text', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Введите заголовок'}),
            'text': forms.Textarea(attrs={'placeholder': 'Введите текст вопроса'}),
        }

    def clean_tags(self):
        tags_str = self.cleaned_data['tags']
        tags_list = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        
        if not (1 <= len(tags_list) <= 3):
            raise ValidationError("Должно быть от 1 до 3 тегов.")
        
        for tag in tags_list: 
            if len(tag) > 20:
                raise ValidationError("Тег должен быть до 20 символов")
        return tags_list

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('title'):
            raise ValidationError("Поле заголовок не может быть пустым.")
        if not cleaned_data.get('text'):
            raise ValidationError("Поле текст не может быть пустым.")
        
        return cleaned_data

    def save(self, user=None, commit=True):
        question = super().save(commit=False)

        if user:
            question.author_id = user.id

        if commit:
            question.save()
            tags_list = self.cleaned_data['tags']
            for tag_name in tags_list:
                tag, created = Tag.get_or_create(tag_name)
                TagQuestion.objects.get_or_create(tag=tag, question=question)
        return question

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'placeholder': 'Введите текст ответа'})
        }
        labels = {
            'text': 'Answer'
        }
