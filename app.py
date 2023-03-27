from flask import Flask, render_template
import chess
import paho.mqtt.client as mqtt
import os
import logging
logging.basicConfig(filename='log.log', level=logging.DEBUG)
MQTT_BROKER = os.environ.get('MQTT_BROKER')
MQTT_TOPIC = os.environ.get('MQTT_TOPIC')

app = Flask(__name__)

board = chess.Board()
x = 0
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/jugar")
def jugar():
    return render_template("jugar.html", fen=board.fen())

def on_message(client, userdata, message):
    if(message.payload.decode("utf-8") != ""):
        global x
        global board
        global blancas
        global negras
        global casilla
        global casillas
        casillas = [55,54,53,52,51,50,49,48,8,9,10,11,12,13,14,15]
        for casilla in casillas:
            print(casilla)
        if(x==0):
            blancas = message.payload.decode("utf-8")[0]
            if(blancas == "1"):
                negras = "2"
                print("Tablero 1 blancas")
            else:
                print("Tablero 2 blancas")
                negras = "1"
            x = x+1
        else:
            find = board.fen().find("w ")
            if(find != -1 and message.payload.decode("utf-8")[0] == blancas or find == -1 and message.payload.decode("utf-8")[0] == negras):
                try:
                    move = chess.Move.from_uci(message.payload.decode("utf-8")[1:])
                    for casilla in casillas:
                        print(casilla)
                        if (board.piece_at(casilla).piece_type == chess.PAWN) and (message.payload.decode("utf-8")[4]=="8" or message.payload.decode("utf-8")[4]=="1"):
                            print("hola")
                            move = chess.Move.from_uci(message.payload.decode("utf-8")[1:]+"q")
                            break
                    noerror = move in board.legal_moves
                    jm = board.is_checkmate()
                    ahogado = board.is_stalemate()
                    mi = board.is_insufficient_material()
                    try:
                        if (mi == True):
                            board = chess.Board()
                            client.publish("interchess/movimiento","mi")
                            x=0
                        if (ahogado == True):
                            board = chess.Board()
                            client.publish("interchess/movimiento","ahogado")
                            x=0
                        if (jm == True):
                            board = chess.Board()
                            client.publish("interchess/movimiento","jm")
                            x=0
                        if(noerror == True):
                            board.push(move)
                            client.publish("interchess/movimiento","update")
                        else:
                            client.publish("interchess/movimiento","error")
                    except:
                        client.publish("interchess/movimiento","error")
                except:
                    pass
                
def on_connect(mqttc, userdata, rc):
    logging.info("Connected with result code "+str(rc))
    
client = mqtt.Client()
client.on_message = on_message
client.on_connect = on_connect
client.connect(MQTT_BROKER, 8084)
client.subscribe(MQTT_TOPIC)

if __name__ == '__main__':
    client.loop_start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)
