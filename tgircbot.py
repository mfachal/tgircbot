# coding: utf8
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# Along with this program.  If not, see <http://www.gnu.org/licenses/>.

import socket
import string
import time
import random
import telepot
from telepot.loop import MessageLoop
import codecs
#import datetime

#todo: hacer que tenga una base de datos posta
#todo: hacer que maneje casos como /link #canal@server, no solo freenode
#todo: hacer que tenga comandos y cosas copadas?
#todo: hacer que maneje imágenes (toggleable)
#todo: hacer que maneje audios (toggleable)
#todo: hacer que indique si editaron el mensaje (con un "E" al final?)
#todo: hacer que las respuestas las indique (toggleable) (algo como "RE: mensaje : mensaje_rta")
#todo: hacer que trunque colores

risk='#empanada'
name='tircbot'
irc=socket.socket()
irc_to_tg_ids = {}
tg_to_irc_chans = {}
datos_file = "db.dat"

#datos_archivo = file()
#la idea es: si A te da /start, se lo agrega al tg_to_irc como clave. Cada canal que le da /join o /link se le agrega a su valor.
#al mismo tiempo, se agrega el canal como clave a irc_to_tg, o si ya estaba se lo agrega a su valor
#TODO: hacer que lo que guarde en el tg_to_irc sea un set de elementos tipo "canal@server" (por ahora nos conformamos con freenode)
#posiblemente hacer que parsee por si necesita pw, o conectarse solo por SSL (minga que lo voy a hacer)

#nota: si el usuario manda por tg y tiene un solo canal asociado, mandarlo directo a ese
#si no, pedirle que mande con /send mensaje

def init_dicts():
    token = ""
    with open(datos_file, 'r') as datos:
        token = datos.readline().strip()
        print "usando: "+repr(token)
        for line in datos:
            if (line.find('_') != -1):
                pass
            a = line.split(' : ')
            b = int(a[0])
            c = a[1].strip()
            if b in tg_to_irc_chans:
                tg_to_irc_chans[b].add(c)
            else:
                tg_to_irc_chans[b] = set([c])
            if c in irc_to_tg_ids:
                irc_to_tg_ids[c].add(b)
            else:
                irc_to_tg_ids[c] = set([b])
    return token

def ircrecibe(irc):
	line = ''
	while 1:
		character = irc.recv(1)
		if character == '\n':
			break
		elif character != '\r':
			line += character
	return line

def code():
    #no estrictamente un quine pero así está siempre actualizado:
    with open("tgircbot.py", "r") as bot_py:
        a = []
        contador = 0
        encodeado = bot_py.read()
        i = 0
        while i <= len(encodeado):
            c = encodeado[i:i+4090]
            a.append(c)
            i = i + 4090
        return a

def tghandle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
#    print msg['from']['id']
#    print tg_to_irc_chans
#    print irc_to_tg_ids
#    print msg['text'][:6]
    if content_type == "text":
        if msg['text'][:6] == "/start":
            if not (msg['chat']['id'] in tg_to_irc_chans):
                tg_to_irc_chans[msg['chat']['id']] = set()

        elif msg['text'][:5] == "/code":
            mensajecodigo = code()
            print "ea amigo que onda?"
            for a in mensajecodigo:
                bot.sendMessage(msg['chat']['id'], "```"+a+"```")

        elif msg['text'][:5] == "/link":
            try:
                canal = msg['text'].split()[1]
                if (canal[0] != '#'):
                    canal = '#' + canal
                tg_to_irc_chans[msg['chat']['id']].add(canal)
                if canal in irc_to_tg_ids:
                    irc_to_tg_ids[canal].add(msg['chat']['id'])
                else:
                    irc_to_tg_ids[canal] = set([msg['chat']['id']])
                    irc.send('JOIN '+canal+'\r\n')

                with open(datos_file, 'a') as datos:
                    datos.write(str(msg['chat']['id']) + ' : ' + canal + '\n')
            except:
                return
            #eventualmente cambiar esto a "hacer pedido SQL, agarrar eso y ponerlo", etc
        else:
            mensaje = bytearray(msg['from']['first_name']+' -- '+msg['text']+'\r\n', "utf_8", "replace")

            if msg['chat']['type'] == 'group' or msg['chat']['type'] == 'supergroup':
                mensaje = bytearray(msg['chat']['title'] + ' -- ', "utf_8", "replace") + mensaje

            lista = mensaje.split('\n')

            #aca voy a poner algo como "if tg_to_irc_chans[msg].size() == 1 que mande directo, si no no mande nada
            for line in lista:
                print line
                for canal in tg_to_irc_chans[msg['chat']['id']]:
                    irc.send(bytearray('PRIVMSG '+canal+' :', "utf_8", "replace") + line + bytearray("\r\n", "utf_8", "replace"))
                #que mande a todos y se joda por boludo, qcyo

    #idea: si content_type != text, subirlo a algun servicio (posiblemente teknik, pomf o imgur) y mandar la URL. No hacer esto con stickers (mandar el emoticon que representa con [sticker] antes) (si no spamea mucho) (hacer que sea opcional, por si se paranoiquean) (settings por grupo)

def main():
    irc.connect(("irc.freenode.net", 6667))
    irc.send('NICK '+name+' \r\n')
    irc.send('USER blah blag bla :test\r\n')

    token = init_dicts()

#    datos_archivo = open(datos_file, 'a') #no, no se puede eliminar de una asociacion
    global bot
    bot = telepot.Bot(token)
    MessageLoop(bot, tghandle).run_as_thread()

    for canal in irc_to_tg_ids.keys():
        print "joineando "+repr(canal)
        irc.send('JOIN '+canal+'\r\n')

    while True:
        msg = ircrecibe(irc)
        print msg
        if msg.find(' PRIVMSG ') != -1:
	    try:
	        mensaje = msg[msg.find('PRIVMSG'):].split(":",1)[1] #desde la parte que te manda el canal en el que estas, quedate con solo el mensaje (parte segun : y se queda con lo de despues)
                mandador = msg[:msg.find('PRIVMSG')].strip()
                if mandador[0] == ':':
                    mandador = mandador[1:]
                mandador = mandador.split('!')[0]
                canal = msg[msg.find('PRIVMSG'):].split()[1]
	    except:
	        pass
#	    print "MENSAJE: "+mensaje #confirmacion de recibo por stdout
            #aca hace cosas con el mensaje
            mensajeaenviar = mandador + ' -- ' + canal +' -- ' + mensaje
            #hacer que asocie ids con grupos y esas cosas -- hacer mas cheto
            #idea: en un grupo le das /link #canal @ server:port y que entre a ese canal
            #cada usuario tiene unos canales asociados, etc.
            #usando SQL lite o esas yerbas?
            if canal != "tircbot":
                for id in irc_to_tg_ids[canal]:
                    bot.sendMessage(id, mensajeaenviar)
        if msg.find(':VERSION') != -1:
	    irc.send('VERSION pythonbot 2')
	elif msg.find('PING') == 0:
            print "ping ack"
	    irc.send('PONG ' + msg.split()[1] + '\r\n')

if __name__ == '__main__':
    main()

