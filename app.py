from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from urllib.request import urlopen as uReq
import pymongo
from bs4 import BeautifulSoup
import scrapetube
from pytube import YouTube
from pytube import Channel

application = Flask(__name__, static_folder='static') # initializing a flask app
app=application
CORS(app)

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            reviews = []
            video_url = request.form['content'].replace(" ","")
            x = YouTube(video_url)
            c_id = x.channel_id
            c_url = x.channel_url
            c = Channel(c_url)
            c_name = c.channel_name
            url = "https://www.youtube.com/watch?v="
            list = []
            videos = scrapetube.get_channel(c_id)
            for video in videos:
                url1 = url + str(video['videoId'])
                list.append(url1)
            for i in list[0:5]:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
                urlclient = requests.get(url, headers = headers)
                videoUrl = i
                getUrl = requests.get(videoUrl)
                soup = BeautifulSoup(getUrl.content , 'html.parser')
                try:
                    Thumbnail_link = soup.find('meta',property='og:image')['content']
                except:
                    Thumbnail_link = "No name"
                try:
                    Title = soup.find('meta',property='og:title')['content']
                except:
                    Title = "No title"
                try:
                    Date = soup.find('meta',itemprop='uploadDate')['content']
                except:
                    Date = "No Date"
                try:
                    views = soup.find("meta", itemprop="interactionCount")['content']
                except:
                    views = "No views"

                mydict = {"Video_url":i ,"Thumbnail_url":Thumbnail_link,"Title":Title,"Views":views,"Upload_date":Date}
                reviews.append(mydict)

            client = pymongo.MongoClient("mongodb+srv://Nishant_17j03:mansinr2211@nishant17j03.focohu4.mongodb.net/?retryWrites=true&w=majority")
            db = client['Video_Scrap']
            review_col = db['Scrap_Data']
            review_col.insert_many(reviews)
            return render_template('results.html', reviews=reviews)
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)