# -*- coding: utf-8 -*-
"""horsesapp.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1YXP9SZbXsWm5U6QGyRQwcP22edS4cmLC
"""

!pip install flask-ngrok

#from google.colab import files
#uploaded = files.upload()

from zipfile import ZipFile

file_name = '/content/templates.zip'

with ZipFile(file_name, 'r') as zip:
  zip.extractall()
  print('Done')

!mkdir static

cd /content/static

!mkdir images

cd ..

import flask
from flask import Flask, render_template, request
from flask_ngrok import run_with_ngrok
import os

from keras.models import load_model 
from keras.preprocessing import image
import numpy as np

app = Flask(__name__)
run_with_ngrok(app)

image_folder = os.path.join('static', 'images')
app.config["UPLOAD_FOLDER"] = image_folder

model = load_model('my_model.h5')

@app.route('/', methods=['GET'])
def home():
  return render_template('index.html')

@app.route('/', methods=['POST'])
def predict():
  # predicting images
  imagefile = request.files['imagefile']
  image_path = './static/images/' + imagefile.filename 
  imagefile.save(image_path)

  img = image.load_img(image_path, target_size=(300, 300))
  x = image.img_to_array(img)
  x = np.expand_dims(x, axis=0)

  images = np.vstack([x])
  classes = model.predict(images, batch_size=10)

  pic = os.path.join(app.config['UPLOAD_FOLDER'], imagefile.filename)
  
  if classes[0]>0.5:
    return render_template('index.html', user_image=pic, prediction_text='{} is the image of Human'.format(imagefile.filename))
  else:
    return render_template('index.html', user_image=pic, prediction_text='{} is the image of Horse'.format(imagefile.filename)) 

if __name__=='__main__':
  app.run()