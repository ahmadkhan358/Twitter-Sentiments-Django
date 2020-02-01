from django import forms


class SearchFormUsername(forms.Form):
    username = forms.CharField(label='', required=True, widget=forms.TextInput(attrs={'class':'form-control row-style', 'placeholder':'Search for username here...'}))
    number_of_tweets = forms.IntegerField(label='', required=True, widget=forms.NumberInput(attrs={'class': 'form-control mt-3', 'placeholder': 'Number Of Tweets'}))

class SearchFormHashtag(forms.Form):
    search_hashtag = forms.CharField(label='', required=True, widget=forms.TextInput(attrs={'class':'form-control row-style', 'placeholder':'Search for hashtags here...'}))
    number_of_tweets = forms.IntegerField(label='', required=True, widget=forms.NumberInput(attrs={'class':'form-control mt-3', 'placeholder':'Number Of Tweets'}))
    date = forms.DateField(label='', required=False, widget=forms.DateInput(attrs={'type': 'date', 'class':'form-control mt-3'}))


class CSVFileForm(forms.Form):
    filename = forms.CharField(label='', required=True, widget=forms.TextInput(attrs={'class':'form-control row-style', 'placeholder':'Enter file name without file extension...'}))