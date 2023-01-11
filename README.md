# User Study Annotator
A minimal, hackable annotator for user studies. Originally created for [_SAMoSA_ (IMWUT/Ubicomp 2022)](https://vimal-mollyn.com/research/samosa-sensing-activities-with-motion-and-sub-sampled-audio/).
![Main page of the tool](media/Page2.png)

## What's it good for?
Anytime you need to manually annotate user sensor data. For example, IMU data from smartwatches, smartphones, etc. This tool will log unix timestamps to a csv, which can later be synced to sensor data.

### How does it work?
Given a set of [contexts with corresponding activities](static/activity_list.json), the tool will first shuffle the contexts in a random order and will further shuffle all the activities within each context (for a total of 3 trials). Check `app.py` to modify the maximum number of trials per activity.

## How to use?
Tested with python3.8  

Run
```
python app.py 
```

## I want a different set of labels
Modify `static/activity_list.json`.

## Dependencies
```
flask
```
