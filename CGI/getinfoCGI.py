import urllib2
import sys

response = urllib2.urlopen('http://192.168.1.150/get_camera_params.cgi?user=admin&pwd=123456')
html = response.read()
html1 = html.replace('\r\n','')
html2 = html1.replace('var ','')
html3 = html2.split(';')
param = {}
for par in html3:
    if par!='':
        parval = par.split('=')
        param[parval[0]]=parval[1]

if len(sys.argv)==1:
    key = sys.argv[1]
else:
    key = 'ircut'

print(param[key])
