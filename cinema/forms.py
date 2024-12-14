from django import forms
from django.contrib.auth.forms import SetPasswordForm, PasswordResetForm, AuthenticationForm
from django.contrib.auth.models import User


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Имя пользователя', 'required': 'required'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Пароль', 'required': 'required'})
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        max_length=128,
        widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}),
    )
    password2 = forms.CharField(
        max_length=128,
        widget=forms.PasswordInput(attrs={'placeholder': 'Подтвердить пароль'}),
    )

    class Meta:
        model = User
        fields = ('username', 'email')
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Имя пользователя', 'autocomplete': 'off'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email', 'required': 'required', 'autocomplete': 'off'})
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Пользователь с таким именем уже существует')
        if len(username) < 3:
            raise forms.ValidationError('Имя должно содержать не менее 3 символов')

        allowed_chars = {'@', '.', '+', '-', '_'}
        if not all(char.isalnum() or char in allowed_chars for char in username):
            raise forms.ValidationError('Имя может содержать только буквы, цифры и символы @/./+/-/_')

        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже зарегистрирован')

        return email

    def clean_password2(self):
        password = self.cleaned_data['password']
        password2 = self.cleaned_data['password2']

        if password and password2 and password != password2:
            raise forms.ValidationError('Пароли не совпадают')

        if len(password) < 8:
            raise forms.ValidationError('Пароль должен содержать не менее 8 символов')

        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({
            'placeholder': 'Введите новый пароль',
            'required': 'required',
        })
        self.fields['new_password2'].widget.attrs.update({
            'placeholder': 'Подтвердите новый пароль',
            'required': 'required',
        })

        self.error_messages['password_mismatch'] = 'Пароли не совпадают'

    def clean_new_password2(self):
        new_password2 = self.cleaned_data.get('new_password2')
        if new_password2 and len(new_password2) < 8:
            raise forms.ValidationError('Пароль должен содержать не менее 8 символов')
        return new_password2

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 and new_password2:
            if new_password1 != new_password2:
                self.add_error('new_password2',  self.error_messages['password_mismatch'])

        return cleaned_data


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Введите ваш email',
        })
    )



