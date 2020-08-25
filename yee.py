def fwd():
    print("jess")


robo_actions = {
    "forward": fwd
}


app = Flask(__name__)


@app.route("/")                   
def hello():                      
    return render_template('main.html')

@app.route("/move", methods=['GET', 'POST'])                   
def move():
    movement = request.form['movement']
    robo_actions[movement]()
    return "Moving " + movement
    
if __name__ == "__main__":        
    app.run(host='0.0.0.0', debug=True, use_reloader=False)
