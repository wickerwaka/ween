#! /usr/bin/env python

import bottle
from bottle import abort, Bottle, static_file

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

relay_state = [ 0 for x in range(8) ]
gpio_ports = [ 26, 19, 13, 6, 5, 22, 27, 17 ]

GPIO.setup( gpio_ports, GPIO.OUT, initial=GPIO.HIGH )


app = Bottle()

@app.route('/api/relay/<id>', method='GET')
def get_relay(id):
	try:
		id = long(id)
	except ValueError:
		abort( 400, 'Invalid relay ID' )

	try:
		state = relay_state[id]
	except IndexError:
		abort( 400, 'Out of range relay ID' )

	return { 'state': state }

@app.route('/api/relay/<id>/<action>', method='POST')
def set_relay(id, action):
	try:
		id = long(id)
	except ValueError:
		abort( 400, 'Invalid relay ID' )
	
	if action not in [ 'on', 'off', 'toggle' ]:
		abort( 400, 'Invalid action' )
	
	try:
		old_state = relay_state[id]
	except IndexError:
		abort( 400, 'Out of range relay ID' )

	if action == 'on':
		GPIO.output( gpio_ports[id], GPIO.LOW )
		relay_state[id] = 1
	elif action == 'off':
		GPIO.output( gpio_ports[id], GPIO.HIGH )
		relay_state[id] = 0
	elif action == 'toggle':
		if old_state == 0:
			GPIO.output( gpio_ports[id], GPIO.LOW )
			relay_state[id] = 1
		else:
			GPIO.output( gpio_ports[id], GPIO.HIGH )
			relay_state[id] = 0

	return { 'state': relay_state[id], 'old_state': old_state  }

@app.route('/')
def default_index():
	return static_file( 'html/index.html', root='./static' )

@app.route('/static/<filepath:path>')
def serve_static(filepath):
	return static_file( filepath, root='./static' )

if __name__ == '__main__':
	bottle.run(app, host='0.0.0.0', port=8080)

