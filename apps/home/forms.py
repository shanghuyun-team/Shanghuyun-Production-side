from django import forms
from .models import Profile, Product, ProductImage, Sensor

class ColorForm(forms.Form):
    color = forms.CharField(
        max_length=7,
        widget=forms.TextInput(attrs={'type': 'color'}),
        label='選擇顏色'
    )
    gradient = forms.BooleanField(required=False, label='是否使用漸層')
    gradient_color = forms.CharField(
        max_length=7,
        widget=forms.TextInput(attrs={'type': 'color'}),
        required=False,
        label='漸層顏色'
    )

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['real_name', 'contact_address', 'phone_number', 'description', 'photo']
        widgets = {
            'real_name': forms.TextInput(attrs={"placeholder": "真實姓名", "class": "form-control"}),
            'contact_address': forms.TextInput(attrs={"placeholder": "聯絡地址", "class": "form-control"}),
            'phone_number': forms.TextInput(attrs={"placeholder": "電話號碼", "class": "form-control"}),
            'description': forms.Textarea(attrs={"placeholder": "個人描述", "class": "form-control"}),
            'photo': forms.FileInput(attrs={"class": "form-control"}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'email', 'phone_number', 'address', 'product_name', 'price', 'description', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '賣家姓名'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@gmail.com'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '連絡電話'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '聯絡地址'}),
            'product_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '商品名稱'}),
            'price': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '商品價錢'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': '商品描述', 'rows': 4, 'cols': 80}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file multiImageInput', 'style' : 'display: none;', 'id': 'productImage'}),
        }

    def __init__(self, *args, **kwargs):
        profile_real_name = kwargs.pop('profile_real_name', None)
        super(ProductForm, self).__init__(*args, **kwargs)
        if profile_real_name:
            self.fields['name'].initial = profile_real_name
            self.fields['name'].widget.attrs['value'] = profile_real_name

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

class SensorForm(forms.ModelForm):
    class Meta:
        model = Sensor
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '感測器名稱'}),
        }