from django.forms import forms


class VerBaseDeDadosForm(forms.Form):
    VARIAVEL_CATEGORICA = (
        (1, "CATEGORICA ORDINAL"),
        (2, "CATEGORICA NOMINAL"),
    )
    variavel_categorica = forms.ChoicerField(choices=VARIAVEL_CATEGORICA, max_length=1)
