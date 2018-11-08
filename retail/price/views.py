# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from price.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from price.models import UserProfile
from background_task import background

import boto3
import botocore
import paramiko
from paramiko.ssh_exception import BadHostKeyException, AuthenticationException, SSHException

import re

import pymysql
import MySQLdb
import pandas as pd

from operator import itemgetter
from itertools import groupby

host = ""
port=3306
dbname="bill"
user="administrator"
password=""

connectionObject = MySQLdb.connect(host, user=user,port=port,passwd=password, db=dbname)

@login_required
def index(request):
	return render(request, 'retail/index.html')

@login_required
def user_logout(request):
	logout(request)
	return HttpResponseRedirect('/retail/login/')

def register(request):
	registered = False
	if request.method == 'POST':
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)

		if user_form.is_valid() and profile_form.is_valid():

			if not bool(re.search("@",request.POST['email'])):
				return HttpResponse("Enter valid email-id.")

			user = user_form.save()
			user.set_password(user.password)
			user.save()

			profile = profile_form.save(commit=False)
			profile.user = user
			profile.save()

			name = user.username
			cID = profile.cardID

			registered = True
			

			try:

				cursorObject = connectionObject.cursor()
				cursorObject.execute("INSERT INTO customer (cardID,customerName) VALUES (%s,%s)", [cID, name])
				connectionObject.commit()

				cursorObject.execute("INSERT INTO customerinshop (cardID) VALUES (%s)", [cID])
				connectionObject.commit()
			 
			except Exception as e:

			    print("Exeception occured:{}".format(e))
			finally:
				pass

	else:
		user_form = UserForm()
		profile_form = UserProfileForm()

	return render(request,
		'retail/register.html',
		{'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
		)

def user_login(request):

	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']

		user = authenticate(username=username, password=password)

		if user is not None:

			if user.is_active:
				login(request, user)
				return HttpResponseRedirect('/retail/')
			else:
				return HttpResponse("Your Retail account is disabled.")

		else:
			return HttpResponse("Invalid login details supplied.")

	else:
		return render(request, 'retail/login.html', {})

@login_required
def bill(request):

	if request.user.is_authenticated:
		user = request.user
	cardID = UserProfile.objects.get(user=user)

	cID = cardID.cardID
	
	try:
		cursorObject = connectionObject.cursor()

		cursorObject.execute("SELECT i.prodName, t.price, count(*), ROUND(t.price*count(*),2) FROM transact as t, itemlist as i WHERE cardID = (%s) AND t.productID = i.productID GROUP BY t.productID", [cID])

		rows = cursorObject.fetchall()
		connectionObject.commit()

		total = 0
		for row in rows:
			total += row[3]

			 
	except Exception as e:

		print("Exeception occured:{}".format(e))

	finally:
		pass

	return render(request, 'retail/bill.html', {'rows':rows, 'total':total})

@login_required
def inventory(request):

	try:
		cursorObject = connectionObject.cursor()

		cursorObject.execute("SELECT productID, prodName, price FROM itemlist as i, pricelist as p WHERE i.productID = p.prodID")

		rows = cursorObject.fetchall()
		connectionObject.commit()

	except Exception as e:

		print("Exeception occured:{}".format(e))

	finally:
		pass

	return render(request, 'retail/inventory.html', {'rows':rows})

@login_required
def history(request):

	if request.user.is_authenticated:
		user = request.user
	cardID = UserProfile.objects.get(user=user)

	cID = cardID.cardID
	
	try:
		cursorObject = connectionObject.cursor()

		cursorObject.execute("SELECT i.prodName, t.price, count(*), ROUND(t.price*count(*),2), t.timeStamp FROM transhistory as t, itemlist as i WHERE cardID = (%s) AND t.productID = i.productID GROUP BY t.productID", [cID])

		rows = cursorObject.fetchall()
		connectionObject.commit()
		
		rows = tuple(tuple(grp) for _, grp in groupby(rows, key=itemgetter(-1)))

		total = []
		for row in rows:
			tot = 0
			for r in row:
				tot += r[3]
			total.append(tot)
		total = tuple(total)

		timestamp = []
		for row in rows:
			for r in row:
				time = r[4]
				break
			t = time	
			t = t.strftime('%m/%d/%Y %H:%M%p')
			timestamp.append(t)
		timestamp = tuple(timestamp)

		test = zip(rows,total,timestamp)

	except Exception as e:

		print("Exeception occured:{}".format(e))

	finally:
		pass

	return render(request, 'retail/history.html', {'rows':rows,'total':total,'timestamp':timestamp,'test':test})

@login_required
def balance(request):

	if request.user.is_authenticated:
		user = request.user
		cardID = UserProfile.objects.get(user=user)

		cID = cardID.cardID
		name = cardID

		try:
			cursorObject = connectionObject.cursor()

			cursorObject.execute("SELECT balance FROM customer WHERE cardID = (%s)", [cID])

			balance = cursorObject.fetchall()
			connectionObject.commit()

			balance = balance[0][0]
			balance = round(balance,2)


		except Exception as e:

			print("Exeception occured:{}".format(e))

		finally:
			pass

	if request.method == 'POST':
		amount = request.POST['amount']
		try:
			cursorObject = connectionObject.cursor()

			cursorObject.execute("UPDATE customer SET balance = balance + (%s) WHERE cardID = (%s)", [amount, cID])
			balance = cursorObject.fetchall()
			connectionObject.commit()

			cursorObject.execute("SELECT balance FROM customer WHERE cardID = (%s)", [cID])
			balance = cursorObject.fetchall()
			connectionObject.commit()

			balance = balance[0][0]
			balance = round(balance,2)


		except Exception as e:

			print("Exeception occured:{}".format(e))

		finally:
			pass

		return render(request, 'retail/balance.html',{'balance':balance,'name':name,})

	else:
		return render(request, 'retail/balance.html',{'balance':balance, 'name':name,})