from flask import Flask, render_template
import chess
import paho.mqtt.client as mqtt

app = Flask(__name__)

board = chess.Board()
x = 0
@app.route("/")
def index():
    return render_template("index.html", fen=board.fen())

def on_message(client, userdata, message):
    if(message.payload.decode("utf-8") != ""):
        global x
        global board
        global blancas
        global negras
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
    

client = mqtt.Client()
client.on_message = on_message
client.connect('broker.emqx.io', 1883, 60)
client.subscribe("salida")

if __name__ == "__main__":
    client.loop_start()
    app.run(host= '0.0.0.0', port=80)
