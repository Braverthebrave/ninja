# ninja
messaging app thingy based on pythnon blah nbalh blah
here be da commands

Admin Commands:
starts with double pipes then admin key

e.g.||12345 shutdown


MODERATION
lock 			- prevents messages being sent, commands can still be sent.

unlock 			- if the server is locked, unlocks the server allowing messages to be sent

kick (user) 		- removes user from chat, they can't see or receive messages and will need to reconnect to chat again

box (user) 		- restricts user receiving messages

unbox (user) 		- if boxed, the user regains the ability to receive messages

mute (user) 		- prevents user from sending messages

unmute (user) 		- allows the user to send messages if muted

blank 			- if command doesn't match list of commands it is sent as a serverbroadcast


SERVER MANAGEMENT
shutdown 		- stops the server running

restart 		- restarts the server (note that it uses program in ram so for changes shutdown then start)


EXTRA
roll 			- rolls a 6-sided dice

roll d(int) 		- rolls a dice with sides corresponding to entered number

cat 			- sends a cat ascii in chat

send 			- sends raw text without any processing


Commands:
starts with double pipes 

e.g.||list

INFO
list 			- lists the users connected and their corresponding ips and ports

list users 		- lists connected users

list addresses 		- list connected addresses 

server info 		- list info about the server

server ip 		- lists the ip and port of the server

help 			- brings up this menu


TOOLS
time 			- displays the server's time

ping 			- echos back pong

echo (text) 		- echos back entered text

testimg 		- displays a stock image of someone doing a thumbs up


INTERACTION
status (status) 	- sends a message saying you are now (status)

w _ (user) (message) 	- sends a message to a specific user that can't be seen by others

img (url)		- sends an image from the desired url, some may not work

BLOCKING
block (user) 		- prevents receiving whispers from user

unblock (user) 		- allows user to send whispers to you again

blocked 		- list users you have blocked


FUN
roll 			- rolls a 6-sided dice

roll d(int) 		- rolls a dice with the number of sides entered

hug (user) 		- sends a message in chat saying you hugged the selected user

cat 			- echo an ascii cat

uwu 			- uwu astolfo crashes ur client 

:3 			- my thighs.
