from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class LoginForm(forms.Form):
    """
    普通登录表单类
    Regular login form class
    """
    username = forms.CharField(max_length=11, label='Please enter your mobile number',
                               widget=forms.widgets.TextInput(
                                   attrs={'class': 'layui-input', 'placeholder': 'Please enter your mobile number',
                                          'lay-verify': 'required|phone', 'id': 'username'}), )
    password = forms.CharField(max_length=20, label='Please enter your password',
                               widget=forms.widgets.PasswordInput(
                                   attrs={'class': 'layui-input', 'placeholder': 'Please enter your password',
                                          'lay-verify': 'required|password', 'id': 'password'}), )

    # 自定义表单字段username的数据清洗
    # Custom data cleaning for username field
    def clean_username(self):
        if len(self.cleaned_data['username']) == 11:
            return self.cleaned_data['username']
        else:
            raise ValidationError('Username must be a phone number')


class LoginModelForm(forms.ModelForm):
    """
    基于模型的登录表单类
    Model-based login form class
    """
    class Meta:
        model = User
        fields = ('username', 'password')
        labels = {
            'username': 'Please enter your mobile number',
            'password': 'Please enter your password',
        }
        error_messages = {
            '__all__': {'required': 'Please enter content',
                        'invalid': 'Please check your input'},
        }
        # 定义widgets，设置表单字段对应HTML元素控件的属性
        # Define widgets, set the HTML element attributes for form fields
        widgets = {
            'username': forms.widgets.TextInput(
                                   attrs={'class': 'layui-input', 'placeholder': 'Please enter your mobile number',
                                          'lay-verify': 'required|phone', 'id': 'username'}),
            'password': forms.widgets.PasswordInput(
                                   attrs={'class': 'layui-input', 'placeholder': 'Please enter your mobile number',
                                          'lay-verify': 'required|password', 'id': 'password'})
        }

    # 自定义表单字段username的数据清洗
    # Custom data cleaning for username field
    def clean_username(self):
        if len(self.cleaned_data['username']) == 11:
            return self.cleaned_data['username']
        else:
            raise ValidationError('Username must be a phone number')