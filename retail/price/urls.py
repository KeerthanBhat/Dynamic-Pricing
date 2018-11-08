from django.conf.urls import url
from price import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^signup/$', views.register, name='register'),
	url(r'^login/$', views.user_login, name='login'),
	url(r'^logout/$', views.user_logout, name='logout'),
	url(r'^bill/$', views.bill, name='bill'),
	url(r'^inventory/$', views.inventory, name='inventory'),
	url(r'^history/$', views.history, name='history'),
	url(r'^balance/$', views.balance, name='balance'),
]