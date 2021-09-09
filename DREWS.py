##########################################################
# DREWS - Domain Registration Early Warning System
# https://github.com/SecOpsSteve/DREWS
# See README.md for further details
appversion = '1.1 (MVP) Public'
##########################################################

import os, base64, re, json, urllib.request, urllib.parse
from datetime import date, timedelta
from io import BytesIO
from urllib.request import Request, urlopen
from zipfile import ZipFile
from pathlib import Path
import smtplib
from email.message import EmailMessage

import config
lookback_days = config.lookback_days
txt_alert_enabled = config.txt_alert_enabled
thehive_alert_enabled = config.thehive_alert_enabled
thehive_url = config.thehive_url
webhook_alert_enabled = config.webhook_alert_enabled
webhook_url = config.webhook_url
email_alert_enabled = config.email_alert_enabled
email_srv = config.email_srv
email_from = config.email_from
email_to = config.email_to

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print('''
     ____  ____  _______       _______
    / __ \/ __ \/ ____/ |     / / ___/
   / / / / /_/ / __/  | | /| / /\__ \ 
  / /_/ / _, _/ /___  | |/ |/ /___/ / 
 /_____/_/ |_/_____/  |__/|__//____/  
''''\n''Version',appversion,'\n')

def runcheck_func(action,encodedname):
	#runcheck_func is used to init/read/update the runcheck file. runcheck keeps track of previous downloads.
	if action == 'init':
		try:
			with open('runcheck',mode='r') as runcheck:
				print('Runcheck exists, continuing..')
				runcheck_list = str(runcheck.read()).split()
				print('Runcheck found', len(runcheck_list),'previous runs.\n')
		except IOError:
			print('[!] Initialising runcheck')
			Path('runcheck').touch()
			print('[!] Initialisation complete.\n')
	#elif action == 'read':
	# 	TODO build 'read' action for pre dl check return t/f?
	elif action == 'update':
		with open('runcheck', mode='a') as runcheck:
			runcheck.write(encodedname+'\n')
	else:
		print('runcheck_func error')

def grabber_extractor_func(url):
	#Grabber Extractor, pass in url. Note the User-Agent, default python User-Agent is commonly blocked.
	req = Request(url, headers={'User-Agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"})
	with urlopen(req) as zipresp:
		with ZipFile(BytesIO(zipresp.read())) as domzip:
			with domzip.open('domain-names.txt') as domzipcontents:
				domlist = str(domzipcontents.read(), 'utf-8').split()
	return domlist

def search_func(regex_patterns,data_in):
	results = []
	for term in regex_patterns:
		r = re.compile(term)
		result = list(filter(r.search, data_in))
		results.append(result)
	search_results = []
	for result in results:
		for x in result:
			search_results.append(x)
	return search_results

def txt_alert_func(list_input,dl_date):
	#Results are written to 'YYYY-MM-DD_Results.txt'.
	with open(dl_date+'_Results.txt', mode='w', encoding='utf-8') as txt_file:
		for item in sorted(list_input):
			txt_file.write(item+'\n')

def thehive_alert_func(list_input,thehive_url):
	#TODO Create an alert via The Hive API.
	print('[!] INOPOPERABLE - Future Feature, only printing',thehive_url)

def webhook_alert_func(list_input,webhook_url):
	#Post to Mattermost or Slack via incoming webhook.
	for item in sorted(list_input):
		data = json.dumps(
			{ 
				"text": ":warning: @channel DREWS has detected a newly registered domain.",
				"attachments": [
				{ 
					"color": "#ff0000",
					"author_name": "DREWS Detection",
					"author_link": 'https://github.com/SecOpsSteve/DREWS',
					"title": "Lookup in DomainTools",
					"title_link": "https://whois.domaintools.com/"+item,
					"text": "Domain: "+item
				}
			]
		}
		).encode('utf-8')
		headers = {'Content-Type': 'application/json'}
		urllib.request.urlopen(urllib.request.Request(webhook_url, data, headers))

def email_alert_func(list_input,msg_srv,msg_from,msg_to,msg_sub):
	#Send results via SMTP
	msg = EmailMessage()
	msg.set_content(f'Please investigate the following;\n\n{list_input}\n\n[!] False positives happen, tune your patterns if required.')
	msg['Subject'] = msg_sub
	msg['From'] = msg_from
	msg['To'] = msg_to
	s = smtplib.SMTP(msg_srv)
	s.send_message(msg)
	s.quit()

# Read in regex_patterns.txt
with open('regex_patterns.txt',mode='r') as regex_patterns:
	regex_patterns = str(regex_patterns.read()).split()

# Check or initialise 'runcheck'
runcheck_func('init','')

# Loop over n lookback_days.
for daynum in range(lookback_days,0,-1):
	dl_date = (date.today() - timedelta(days=daynum)).strftime('%Y-%m-%d')
	dl_name = dl_date + '.zip'
	encodedname = str(base64.b64encode(dl_name.encode()), "utf-8")
	url = 'https://www.whoisdownload.com/download-panel/free-download-file/'+encodedname+'/nrd/home'
	# Read runcheck, do if not already done
	with open('runcheck', mode='r') as runcheck:
		if not encodedname in runcheck.read():
			# Download and extract the list
			domlist = grabber_extractor_func(url)
			# Search patterns
			search_results = search_func(regex_patterns,domlist)
			# Output functions
			if not search_results == []:
				if txt_alert_enabled:
					txt_alert_func(search_results,dl_date)
				if thehive_alert_enabled:
					thehive_alert_func(search_results,thehive_url)
				if webhook_alert_enabled:
					webhook_alert_func(search_results,webhook_url)
				if email_alert_enabled:
					email_sub = f'DREWS Alert {dl_date}'
					email_alert_func(search_results,email_srv,email_from,email_to,email_sub)
			print('D-' + str(daynum), ':', dl_date, '\t Domains:', len(domlist), '\t Results:', len(search_results))
			runcheck_func('update',encodedname)
		else:
			print('D-' + str(daynum), ':', dl_date, '\t Skipped:', encodedname)
exit(0)
