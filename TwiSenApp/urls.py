from . import views
from django.urls import path

app_name = "TwiSenApp"

urlpatterns = [
    path('', views.index, name='index'),
    path("searchbyuname/", views.search_by_uname, name='searchbyuname'),
    path("searchbyhtag/", views.search_by_htag, name='searchbyhtag'),
    path("sentimentanalysis/", views.sentiment_analysis_of_tweets, name='sentimentanalysis'),
    path("savetocsv/", views.save_to_csv, name='savetocsv'),
]