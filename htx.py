#! /usr/bin/python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import json

lights = []

def gen_config():
    answer = dict()

    answer["name"] = "Philips hue"
    answer["zigbeechannel"] = 15
    answer["mac"] = "00:17:88:00:00:00"
    answer["dhcp"] = False
    #answer["ipaddress"] = "192.168.1.7"
    #answer["netmask"] = "255.255.255.0"
    #answer["gateway"] = "192.168.1.1"
    answer["proxyaddress"] = "none"
    answer["proxyport"] = 0
    answer["UTC"] = "2014-07-17T09:27:35"
    answer["localtime"] = "2014-07-17T11:27:35"
    answer["timezone"] = "Europe/Madrid"
    answer["swversion"] = "01012917"
    answer["apiversion"] = "1.3.0"
    answer["linkbutton"] = False
    answer["portalservices"] = False
    answer["portalconnection"] = "connected"

    ps = dict()
    ps["signedon"] = True
    ps["incoming"] = False
    ps["outgoing"] = True
    ps["communication"] = "disconnected"
    answer['portalstate'] = ps

    return answer

def gen_config_json():
    return json.dumps(get_config())

def set_light_state(nr, state):
    entry = json.loads(state)

    if entry['on'] == True:
            print 'switch %s on' % lights[nr]['name']

    else:
            print 'switch %s off' % lights[nr]['name']

    json_obj = []

    entry = dict()
    entry['success'] = 'Updated.'

    json_obj.append(entry)

    return json.dumps(json_obj)

def gen_ind_light_json(nr):
    entry = dict()

    entry['state'] = dict()
    entry['state']['on'] = False
    entry['state']['reachable'] = True

    entry['type'] = 'Switch'
    entry['name'] = lights[nr]['name']
    entry['modelid'] = '666'
    entry['swversion'] = '42'

    return entry

def gen_lights():
    global lights

    json_obj = dict()

    nr = 1
    for l in lights:
        json_obj['%d' % nr] = gen_ind_light_json(nr - 1)
        
        nr += 1

    return json_obj

def gen_groups():
    answer = dict()

    g = dict()
    g['name'] = 'Group 1'

    g['lights'] = []
    for i in xrange(0, len(lights)):
        g['lights'].append('%d' % (i + 1))

    g["type"] = 'LightGroup'

    action = dict()
    action['on'] = True
    action["bri"] = 254
    action["hue"] = 10000
    action["sat"] = 254
    action["effect"] = "none"
    action['xy'] = []
    action['xy'].append(0.5)
    action['xy'].append(0.5)
    action["ct"] = 250
    action["alert"] = "select"
    action["colormode"] = "ct"
    g['action'] = action

    answer['1'] = g

    return answer

def gen_groups_json():
    return json.dumps(gen_groups())

def gen_light_json():
    return json.dumps(gen_lights())

def gen_dump_json():
    answer = dict()

    answer['lights'] = gen_lights()

    answer['groups'] = gen_groups()

    answer['config'] = gen_config()

    answer['swupdate2'] = dict()

    answer['schedules'] = dict()

    return json.dumps(answer)

class server(BaseHTTPRequestHandler):
	def _set_headers(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()

	def do_GET(self):
		self._set_headers()

                parts = self.path.split('/')

                if len(parts) >= 3 and parts[1] == 'api':
                        print 'get all state'
                        self.wfile.write(gen_dump_json())

                elif len(parts) >= 4 and parts[1] == 'api' and parts[3] == 'lights':
                        print 'enumerate list of lights'
                        self.wfile.write(gen_light_json())

                elif len(parts) >= 4 and parts[1] == 'api' and parts[3] == 'groups':
                        print 'enumerate list of groups'
                        self.wfile.write(gen_groups_json())

                elif len(parts) >= 4 and parts[1] == 'api' and parts[3] == 'light':
                        print 'get individual light state'
                        self.wfile.write(gen_ind_light_json(int(parts[4]) - 1))

                elif len(parts) >= 4 and parts[1] == 'api' and parts[3] == 'config':
                        print 'get basic configuration'
                        self.wfile.write(gen_config_json())

                else:
                        print 'unknown get request', self.path
                        self.wfile.write('???')

	def do_HEAD(self):
		self._set_headers()
        
	def do_POST(self):
                parts = self.path.split('/')

                # simpler registration; always return the same key
                # should keep track in e.g. an sqlite3 database and then do whitelisting etc
                if len(parts) >= 2 and parts[1] == 'api':
			self._set_headers()
			self.wfile.write('[{"success":{"username": "83b7780291a6ceffbe0bd049104df"}}]')

                elif len(parts) >= 4 and parts[1] == 'api' and parts['3'] == 'groups':
			self._set_headers()
			self.wfile.write('[{"success":{"id": "1"}}]')

                else:
                        print 'unknown post request', self.path

        def do_PUT(self):
		self._set_headers()

                parts = self.path.split('/')

                if len(parts) >= 6 and parts[1] == 'api' and parts[3] == 'lights' and parts[5] == 'state':
                        print 'set individual light state'

                        data_len = int(self.headers['Content-Length'])
                        self.wfile.write(set_light_state(int(parts[4]) - 1, self.rfile.read(data_len)))

                else:
                        print 'unknown put request', self.path
                
        
def run(server_class=HTTPServer, handler_class=server, port=80):
	server_address = ('', port)
	httpd = server_class(server_address, handler_class)
	print 'Starting http listener...'
	httpd.serve_forever()

def add_light(name, command):
        global lights

        row = dict()
        row['name'] = name
        row['cmd'] = command

        lights.append(row)

add_light('command', 'echo')

run()
