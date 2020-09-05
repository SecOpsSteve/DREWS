# Domain Registration Early Warning System (DREWS)

*Attention: The domain list download fails, unfortunately WhoisDS no longer provide the source data used in this project.*

## Objective
Brand impersonation, fraud and phishing pose prolific threats, even the biggest brands can be susceptible. A malicious actor could purchase a lookalike domain with no identity checks and use this domain to conduct business email compromise type campaigns.

> *In 2018, business email compromise (BEC) accounted for 23% of cyber insurance claims received from Europe, the Middle East and Asia, according to statistics released by AIG.*

DREWS is a means to identify unauthorised domain registrations that could facilitate brand impersonation, fraud or shadow IT. DREWS uses regular expressions to match results in Newly Registered Domain (NRD) lists and posts results to services such as Mattermost or Slack.

Reducing detection time enables an overall faster response, allowing responders to raise complaints with registrars or hosting providers in a timely fashion. Therefore disrupting the threat actors operations and reducing the campaign lifespan. Ultimately frustrating and imposing costs on the actor.

*Many thanks to <a href="https://whoisds.com/newly-registered-domains" target="_blank">WhoisDS</a> for providing the data for free.*

## How it works

* DREWS will iterate over *n* previous days. For each day/iteration;
* It will read the *"runcheck"* file and skip the current iteration if previously completed, otherwise;
* The day's NRD list is downloaded from <a href="https://whoisds.com/newly-registered-domains" target="_blank">WhoisDS</a>, extracted on-the-fly and stored in the *"domlist"* variable.
* Custom regular expressions are read in from *"regex_patterns.txt"* and are run against *"domlist"*.
* Regular expression matches are stored in the *"search_results"* variable.
* *"search_results"* is then passed into any enabled alert/output function.
* The *"runcheck"* file is updated with the a successful marker for the day.
* Proceeds to the next day, stopping having completed yesterdays run (current day -1).

### Output Functions

|Output			|Description											|Status|
|:---			|:---													|:---|
|__File__		|Output to file, 'YYYY-MM-DD_Results.txt'				|Tested, Reliable|
|__Mattermost__	|Post to a Mattermost channel via an incoming webhook 	|Tested, Reliable|
|__Slack__		|Post to a Slack channel via an incoming webhook		|Tested, Reliable|
|__TheHive__	|Create an alert within TheHive							|Future Feature|

### Known Issues

1. __<a href="https://whoisds.com/newly-registered-domains" target="_blank">WhoisDS</a> data does not include all TLDs.__
1. Download error handling, a failed NRD list download will result in a __badzip error__, it will exit but will try again next time.
1. Posting to a webhook that is not available result in a hang/wait for timeout. File output will still function. 
1. TheHive output has yet to be added.
1. It isn't perfect but it works well.

## Dependencies
* python3
* Internet access
* <a href="https://mattermost.com/" target="_blank">Mattermost</a> configured to allow incoming webhooks, or;
* <a href="https://slack.com/" target="_blank">Slack</a> configured to allow incoming webhooks, or;
* Some other means of monitoring file creation, perhaps the Power Automate SFTP connector.

## Setup and Configuration

1. Clone the repository.
```
git clone https://github.com/SecOpsSteve/DREWS.git
```
2. Edit __regex_patterns.txt__ and configure appropriate regular expressions (one regex per line), for example;
```
g[o0]{2}gg?[li1]e
```
Regular expressions can be built and tested with this example <a href="https://gchq.github.io/CyberChef/#recipe=Regular_expression%28'User%20defined','g%5Bo0%5D%7B2%7Dgg?%5Bli1%5De',true,true,false,false,false,false,'Highlight%20matches'%29&input=ZXhhbXBsZWcwMGdsZS5jb20KZXhhbXBsZWZha2Vnb29nbGVkb21haW4uY29tCg" target="_blank">CyberChef Recipe.</a> __Caution:__ Loose regex patterns are likely to cause erroneous matches and subsequent noisy alerts.

3. Next, edit __DREWS.py__ and set the desired options.
```
lookback_days = 7                           # On first run, iterate over n previous days.
txt_alert_enabled = True                    # Write results to 'YYYY-MM-DD_Results.txt'
thehive_alert_enabled = False               # INOPOPERABLE - FUTURE FEATURE
thehive_url = 'https://thehive.blah.io'     # INOPOPERABLE - FUTURE FEATURE
webhook_alert_enabled = False               # Enable output to a configured webhook.
webhook_url = 'https://mattermost.blah.io'  # Mattermost or Slack incoming webhook URL.
```
4. Schedule __DREWS.py__ to run daily.
```
crontab -e
```
Add an entry to the crontab for __DREWS.py__. The following example is set to execute every day at 0800 hrs.
```
|> Minute
| |> Hour
| | |> Day (month)
| | | |> Month
| | | | |> Day (week)
m h d m d command
0 8 * * * /usr/bin/python3 /<path-to-directory>/DREWS/DREWS.py > /<path-to-directory>/DREWS/lastrun.txt
```
*Optional: Direct output to __lastrun.txt__.*

5. Test. It is recommended to test your regex patterns thoroughly, this <a href="https://gchq.github.io/CyberChef/#recipe=Regular_expression%28'User%20defined','g%5Bo0%5D%7B2%7Dgg?%5Bli1%5De',true,true,false,false,false,false,'Highlight%20matches'%29&input=ZXhhbXBsZWcwMGdsZS5jb20KZXhhbXBsZWZha2Vnb29nbGVkb21haW4uY29tCg" target="_blank">CyberChef Recipe</a> can help. Also use a test Slack/Mattermost channel to avoid flooding your ChatOps channel.

## Manual Operation
__DREWS.py__ can be run manually, output will appear similar to the following;
```
blah@blah:~/Projects/DREWS$ python3 DREWS.py
     ____  ____  _______       _______
    / __ \/ __ \/ ____/ |     / / ___/
   / / / / /_/ / __/  | | /| / /\__ \ 
  / /_/ / _, _/ /___  | |/ |/ /___/ / 
 /_____/_/ |_/_____/  |__/|__//____/  

Version 0.9 (MVP)

[!] Initialising runcheck
[!] Initialisation complete.

D-7 : 2020-05-14 	 Domains: 118951 	 Results: 0
D-6 : 2020-05-15 	 Domains: 147890 	 Results: 1
D-5 : 2020-05-16 	 Domains: 141381 	 Results: 1
D-4 : 2020-05-17 	 Domains: 130792 	 Results: 0
D-3 : 2020-05-18 	 Domains: 82749 	 Results: 0
D-2 : 2020-05-19 	 Domains: 125215 	 Results: 0
D-1 : 2020-05-20 	 Domains: 151783 	 Results: 0
blah@blah:~/Projects/DREWS$ 
```
Running __DREWS.py__ again will result in skipping previously run days. Progress is recorded in the __runcheck__ file.
```
blah@blah:~/Projects/DREWS$ python3 DREWS.py
     ____  ____  _______       _______
    / __ \/ __ \/ ____/ |     / / ___/
   / / / / /_/ / __/  | | /| / /\__ \ 
  / /_/ / _, _/ /___  | |/ |/ /___/ / 
 /_____/_/ |_/_____/  |__/|__//____/  

Version 0.9 (MVP)

Runcheck exists, continuing..
Runcheck found 7 previous runs.

D-7 : 2020-05-14 	 Skipped: MjAyMC0wNS0xNC56aXA=
D-6 : 2020-05-15 	 Skipped: MjAyMC0wNS0xNS56aXA=
D-5 : 2020-05-16 	 Skipped: MjAyMC0wNS0xNi56aXA=
D-4 : 2020-05-17 	 Skipped: MjAyMC0wNS0xNy56aXA=
D-3 : 2020-05-18 	 Skipped: MjAyMC0wNS0xOC56aXA=
D-2 : 2020-05-19 	 Skipped: MjAyMC0wNS0xOS56aXA=
D-1 : 2020-05-20 	 Skipped: MjAyMC0wNS0yMC56aXA=
blah@blah:~/Projects/DREWS$ 
```
