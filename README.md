# Noisemaker
An open source link aggregation web app for Google App Engine, similar to [Hacker News](https://news.ycombinator.com/) or [Lobsters](https://lobste.rs/). Noisemaker is written in Python and runs on Google App Engine. A live version can be found at [http://noisemaker.co](http://noisemaker.co), a link aggregation site geared toward music and audio creation.

## Quick Start
Assuming you've already installed and familiarized yourself with the [Google App Engine SDK for Python](https://cloud.google.com/appengine/downloads), you can get your own version of Noisemaker running with just a few small edits to a few files.

* Clone Noisemaker from Github

  ```$ git clone https://github.com/erikcore/noisemaker.git```
  
* Edit app.yaml. Change line 1:

  ```application: noisemakerclub```
  
  to your own unique app name.
  
* Edit main.py.
  
  First, edit line 20:
  
  ```config['webapp2_extras.sessions'] = dict(secret_key='<ENTER A UNIQUE, SUPER SECRET STRING HERE>')```
  
  Change `<ENTER A UNIQUE, SUPER SECRET STRING HERE>` to a unique and secret string.
  
  Next, edit line 86:
  
  ```message = mail.EmailMessage(sender="Noisemaker <hello@noisemakerclub.appspotmail.com>", subject="Welcome to Noisemaker")```
  
  Change `<hello@noisemakerclub.appspotmail.com>` to a valid email for your app and customize the email subject line.
  
  Finally, edit line 90 to customize your email welcome message.

That's it! You should now be able to add your cloned directory to the Google App Engine launcher as an existing app and deploy it.
