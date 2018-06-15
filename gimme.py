from flask import Flask, request, render_template, url_for, redirect
from pymongo import MongoClient, DESCENDING
from bson import ObjectId
import urllib.parse
import datetime
import json

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.gimmedb
posts = db.posts


@app.route('/')
def startpage():
    print(posts)
    posted = posts.find()
    # to do add variables for the posts
    templatepost = '''
    <div class="card">
        <div class="card-header">
            %s
            <button class="btn btn-danger">New Suggestion</button>
            <a class='btn btn-danger' href='{{ url_for("newanswer") }}?id=%s'>New Suggestion</a>
        </div>

        <div class="card-body">
            <h5 class="card-title">%s</h5>
            %s
        </div>

    </div>

    <div style="height: 5vh;">
    </div>

    '''

    retstr = ""

    for item in posted:
        tempstr = ""

        for temp in item['suggestions']:
            tempstr += "<a class='btn btn-danger' href='" + temp['url'] + "'>" + temp['suggestion'] + "</a>"



        #print(type(item))
        #print(item)
        #print()
        newstr = templatepost.format(item['category'], str(item['_id']), item['question'], tempstr)
        templatepost = '''
            <div class="card">
                <div class="card-header">
                    %s
                    <a class='btn btn-danger' href='%s?id=%s'>New Suggestion</a>
                </div>

                <div class="card-body">
                    <h5 class="card-title">%s</h5>
                    %s
                </div>

            </div>

            <div style="height: 5vh;">
            </div>

            ''' % (item['category'], url_for('newanswer'), str(item['_id']), item['question'], tempstr)
        #print(templatepost)
        #print(newstr)
        retstr += templatepost
        #print()

    return render_template("index.html", postvar=retstr)

@app.route('/newmessage', methods=["GET", "POST"])
def newmessage():
    return render_template("newquestion.html")

@app.route('/postmessage', methods=["GET", "POST"])
def postmessage():


    if request.method == 'POST':
        category = request.form['category']
        question = request.form['question']
        date = datetime.datetime.utcnow()

        post = {"category": category, "question": question, "date": date, "suggestions": []}
        posts.insert_one(post)
        return redirect(url_for('startpage'))

@app.route('/newanswer', methods=["GET", "POST"])
def newanswer():
    #if request.method == "GET":
    ids = request.args['id']
    posted = posts.find_one({"_id": ObjectId(ids)})


    return render_template("answerquestion.html", question=posted['question'], category=posted["category"], id=ids)


@app.route('/feed', methods=["GET", "POST"])
def getfeed():
    all = posts.find().limit(30).sort('date', DESCENDING)
    retstr = ""
    for item in all:

        tempstr = ""

        for temp in item['suggestions']:
            tempstr += "<a class='btn btn-danger' href='" + temp['url'] + "'>" + temp['suggestion'] + "</a>"

        templatepost = '''
                    <div class="card">
                        <div class="card-header">
                            %s
                            <a class='btn btn-danger' href='%s?id=%s'>New Suggestion</a>
                        </div>

                        <div class="card-body">
                            <h5 class="card-title">%s</h5>
                            %s
                        </div>

                    </div>

                    <div style="height: 5vh;">
                    </div>

                    ''' % (item['category'], url_for('newanswer'), str(item['_id']), item['question'], tempstr)
        retstr += templatepost
    return render_template('feed.html', postvar=retstr)


@app.route('/postanswer', methods=["GET", "POST"])
def postanswer():

    id = request.form['id']
    suggestion = request.form['suggestion']
    url = request.form['url']

    posted = posts.find_one({"_id": ObjectId(id)})
    temp = posted
    temp['suggestions'].append({"suggestion" : suggestion, "url" : url})
    x = posts.replace_one({"_id": ObjectId(id)}, temp)
    return redirect(url_for('startpage'))


if __name__ == '__main__':
    app.run(host='192.168.7.11', port=1999)
