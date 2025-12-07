from django import forms

class SupplierInwardEntryForm(forms.Form):
    """Form for supplier inward entry with 3 required documents"""
    invoice = forms.FileField(
        label='Invoice',
        help_text='Primary reference document (PDF, JPG, PNG - Max 10MB)',
        widget=forms.FileInput(attrs={
            'accept': '.pdf,.jpg,.jpeg,.png',
            'class': 'file-input'
        })
    )
    
    delivery_order = forms.FileField(
        label='Delivery Order (DO)',
        help_text='Required document (PDF, JPG, PNG - Max 10MB)',
        widget=forms.FileInput(attrs={
            'accept': '.pdf,.jpg,.jpeg,.png',
            'class': 'file-input'
        })
    )
    
    purchase_order = forms.FileField(
        label='Purchase Order (LPO)',
        help_text='Required document (PDF, JPG, PNG - Max 10MB)',
        widget=forms.FileInput(attrs={
            'accept': '.pdf,.jpg,.jpeg,.png',
            'class': 'file-input'
        })
    )
    
    remarks = forms.CharField(
        label='Remarks (Optional)',
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 4,
            'class': 'input-field textarea-field',
            'placeholder': 'Add any additional notes or comments...'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validate file sizes (10MB max)
        max_size = 10 * 1024 * 1024  # 10MB in bytes
        
        for field_name in ['invoice', 'delivery_order', 'purchase_order']:
            file = cleaned_data.get(field_name)
            if file and file.size > max_size:
                raise forms.ValidationError(
                    f'{field_name.replace("_", " ").title()} file size must be less than 10MB'
                )
        
        return cleaned_data


class DirectPurchaseEntryForm(forms.Form):
    """Form for direct purchase entry with invoice only"""
    invoice = forms.FileField(
        label='Invoice',
        help_text='Primary reference document (PDF, JPG, PNG, DOC, DOCX - Max 10MB)',
        widget=forms.FileInput(attrs={
            'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx',
            'class': 'file-input'
        })
    )
    
    remarks = forms.CharField(
        label='Remarks (Optional)',
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 4,
            'class': 'input-field textarea-field',
            'placeholder': 'Add any additional notes or comments...'
        })
    )
    
    def clean_invoice(self):
        file = self.cleaned_data.get('invoice')
        
        if file:
            # Validate file size (10MB max)
            max_size = 10 * 1024 * 1024
            if file.size > max_size:
                raise forms.ValidationError('File size must be less than 10MB')
        
        return file

class SupplierInwardEditForm(SupplierInwardEntryForm):
    """Form for editing supplier inward entry (files optional)"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['invoice', 'delivery_order', 'purchase_order']:
            self.fields[field].required = False
            self.fields[field].help_text = f"Upload new file to replace existing {field.replace('_', ' ')} (Optional)"

class DirectPurchaseEditForm(DirectPurchaseEntryForm):
    """Form for editing direct purchase entry (files optional)"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['invoice'].required = False
        self.fields['invoice'].help_text = "Upload new file to replace existing invoice (Optional)"
