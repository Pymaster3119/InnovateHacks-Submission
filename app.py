from flask import Flask, jsonify, render_template, send_from_directory, request
import os
import threading
import importlib
import logging

app = Flask(__name__)
app.logger.setLevel(logging.ERROR)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
STATIC_FOLDER = "static"

thread = None
module = None
try:
    os.unlink("static/result.png")
except:
    pass
def importfns():
    global module
    import conversational_gpt
    module = conversational_gpt
with open("static/action.txt", "w") as txt:
    txt.write("")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/conversation.txt', methods=['GET'])
def get_conversation():
    try:
        with open(os.path.join(STATIC_FOLDER, 'conversation.txt'), 'r') as f:
            data = f.read()
        return data, 200
    except FileNotFoundError:
        return "Conversation log not found", 404

@app.route('/result.png')
def get_web_portal_image():
    try:
        return send_from_directory(STATIC_FOLDER, 'result.png')
    except:
        return send_from_directory(STATIC_FOLDER, "bg_grid.jpg")

# Route for sending prompt to action.txt
@app.route('/action.txt', methods=['POST'])
def send_prompt():
    try:
        content = request.data.decode('utf-8')  # Decode the raw data from the request
        # Write the content to action.txt
        with open(os.path.join(STATIC_FOLDER, 'action.txt'), 'w') as f:
            f.write(content)
        with open(os.path.join(STATIC_FOLDER, 'update.txt'), 'w') as f:
            f.write("")  # Write the incoming content to action.txt
        return "Content written to action.txt", 200
    except Exception as e:
        return str(e), 500

@app.route('/bg_grid', methods=['GET'])
def bgload():
    return send_from_directory(STATIC_FOLDER, 'bg_grid.jpeg')
@app.route('/1155097.png', methods=['GET'])
def sendbg():
    return send_from_directory(STATIC_FOLDER, '1155097.png')

@app.route('/reset.txt', methods=['GET'])
def reset():
    try:
        global thread, module
        if module is not None:
            importlib.reload(module)
        startthread()
        return "Successfully Reset", 200
    except Exception as e:
        return str(e), 500

def startthread():
    global thread
    if thread is None or not thread.is_alive():
        thread = threading.Thread(target=importfns)
        thread.start()

if __name__ == '__main__':
    startthread()
    app.run(debug=False, port=8080)
    