import urllib2
import sys

if len(sys.argv)==2:
    operation = sys.argv[1]
    if operation=='ON':
        response = urllib2.urlopen('http://192.168.1.150/camera_control.cgi?param=14&value=0&user=admin&pwd=123456')
    elif operation=='OFF':
        response = urllib2.urlopen('http://192.168.1.150/camera_control.cgi?param=14&value=1&user=admin&pwd=123456')
    else:
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
        key = 'ircut'
        if param[key]=='0':
            print('True')
        else:
            print('False')
