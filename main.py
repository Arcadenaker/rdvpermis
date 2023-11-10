import time, json
from multiprocessing import Process, Manager, Value
from flask import Flask, send_from_directory
import permis
app = Flask(__name__)


@app.route('/app')
def hello():
    with open("data", "r") as f:
        data = f.read()
        return json.loads(data)

@app.route("/")
def main():
    return send_from_directory('./', "index.html")

def run_flask():
    app.run("0.0.0.0", 3000)

def regular_poll():
    while True:
        time.sleep(60 * 10) #Every 10 minutes
        poll()
def poll():
    app = permis.get_appointments()
    with open("data", "w") as f:
        f.write(json.dumps(app))
        

if __name__ == "__main__":
    poll();
    p1 = Process(target=run_flask)
    p1.start()
    p2 = Process(target=regular_poll)
    p2.start()
    p1.join()
    p2.join()
