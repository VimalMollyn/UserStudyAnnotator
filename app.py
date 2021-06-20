from flask import Flask, render_template, request, make_response, jsonify, Response, send_file
import numpy as np
import json
from collections import defaultdict

app = Flask(__name__)

# constants
num_trials = 3

@app.route("/submit_pid", methods=["POST"])
def submit_pid():
    if request.method == "POST":
        pid = int(request.form.get("pid"))
        
        # set a random seed
        np.random.seed(pid)

        # create the list storing the order of contexts and activities 
        # read the activity list
        with open("static/activity_list.json") as f:
            activity_dict = json.load(f)

        # get a random order of permuations
        contexts = list(np.random.permutation(list(activity_dict.keys())))
        
        # get a random order of activities for each context
        new_activity_dict = defaultdict(list)

        for context in contexts:
            for trial in range(num_trials):
                # for each trial, get a random permuation of the activities per context
                new_activity_dict[context] += list(np.random.permutation(activity_dict[context]))
                
        # read participant's state TODO
        p_state = {
                "context": 0,
                "activity": 0
                }

        # get curr context and activity
        curr_context = contexts[p_state["context"]]
        curr_activity = new_activity_dict[curr_context][p_state["activity"]]
        curr_trialno = p_state["activity"]//len(new_activity_dict[curr_context]) + 1 

        html_data = {
                "curr_context": curr_context,
                "curr_activity": curr_activity,
                "curr_trialno": curr_trialno
                }
        
        # serve the activity page
        return render_template("activity_page.html", html_data=html_data)


@app.route("/")
def root():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="localhost", port=4444, debug=True)
