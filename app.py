from flask import Flask, render_template, request, make_response, jsonify, Response, send_file
import numpy as np
import json
from collections import defaultdict
from pathlib import Path

app = Flask(__name__)

# constants
num_trials = 2

def get_contexts_activities_lists(pid):
    # set a random seed
    np.random.seed(int(pid))

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

    return contexts, new_activity_dict

def get_context_activity(p_state, contexts, new_activity_dict):
    curr_context = contexts[p_state["context"]]
    curr_activity = new_activity_dict[curr_context][p_state["activity"]]
    curr_trialno = p_state["activity"]//(len(new_activity_dict[curr_context])//num_trials) + 1 

    return curr_context, curr_activity, curr_trialno

def get_curr_status(pid):
    contexts, new_activity_dict = get_contexts_activities_lists(pid)

    # read participant's state
    p = Path(f"study_data/p_{pid}/p_state.json")
    if p.exists():
        # participant exists, read p_state
        with open(p, "r") as f:
            p_state = json.load(f)
    else:
        # make the dir
        p.parents[0].mkdir(exist_ok=True, parents=True)

        # set the p_state
        p_state = {
                "context": 0,
                "activity": 0
                }

        # save the p_state
        with open(p, "w") as f:
            json.dump(p_state, f)

    # get curr context and activity
    curr_context, curr_activity, curr_trialno = get_context_activity(p_state, contexts, new_activity_dict)

    return curr_context, curr_activity, curr_trialno, p_state
    

@app.route("/next_trial", methods=["POST"])
def next_trial():
    if request.method == "POST":
        req = request.get_json()

        start_time = req["start_time"]
        end_time = req["end_time"]
        pid = req["pid"]
        
        # get contexts, activities list
        contexts, new_activity_dict = get_contexts_activities_lists(pid)

        # get current status
        curr_context, curr_activity, curr_trialno, p_state = get_curr_status(pid)

        # check if the statuses match, or else error out
        assert curr_context == req["context"]
        assert curr_activity == req["activity"]
        assert curr_trialno == int(req["trialno"])

        # TODO save timestamps with any notes
        row = map(lambda x: str(x), [pid, start_time, end_time, curr_context, curr_activity, curr_trialno])
        with open(f"study_data/p_{pid}/timestamps.csv", "a") as f:
            f.write(",".join(row) + "\n")

        # update the status
        
        # check if we're done with all activities in the context
        if p_state["activity"] == len(new_activity_dict[curr_context]) - 1:

            # check if  we're done with all contexts!
            if p_state["context"] == len(contexts) - 1:
                response = {
                    "message": "Finished, Finally!"
                    }
                return make_response(jsonify(response), 200)
            else:
                # set the activity state to 0
                p_state["activity"] = 0
                p_state["context"] += 1
        else:
            # only need to increment the activity
            p_state["activity"] += 1

        # save the p_state
        p = Path(f"study_data/p_{pid}/p_state.json")
        with open(p, "w") as f:
            json.dump(p_state, f)

        # get curr context and activity
        curr_context, curr_activity, curr_trialno = get_context_activity(p_state, contexts, new_activity_dict)

        response = {
                "message": "Here's the current stuff",
                "curr_context": curr_context,
                "curr_activity": curr_activity,
                "curr_trialno": curr_trialno
                }

        return make_response(jsonify(response), 200)


@app.route("/submit_pid", methods=["POST"])
def submit_pid():
    if request.method == "POST":
        pid = int(request.form.get("pid"))
        
        curr_context, curr_activity, curr_trialno, p_state = get_curr_status(pid)

        html_data = {
                "curr_context": curr_context,
                "curr_activity": curr_activity,
                "curr_trialno": curr_trialno,
                "curr_pid": pid
                }
        
        # serve the activity page
        return render_template("activity_page.html", html_data=html_data)


@app.route("/")
def root():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="localhost", port=4444, debug=True)
