# -*- coding: utf-8 -*-
"""Horses_Humans_Convnet.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/166OjCE5m6k4ZAaJzRHEtHifoSWseuofu

# Horse or Human Convnet Model

Link to the datasets

https://storage.googleapis.com/laurencemoroney-blog.appspot.com/horse-or-human.zip

https://storage.googleapis.com/laurencemoroney-blog.appspot.com/validation-horse-or-human.zip

Unzipping the data
"""

import os
import zipfile

local_zip = '/tmp/horse-or-human.zip'
zip_ref = zipfile.ZipFile(local_zip, 'r')
zip_ref.extractall('/tmp/horse-or-human')
zip_ref.close()

local_zip = '/tmp/validation-horse-or-human.zip'
zip_ref = zipfile.ZipFile(local_zip)
zip_ref.extractall('/tmp/validation-horse-or-human')
zip_ref.close()

"""Defining the directories"""

train_horse_dir = os.path.join('/tmp/horse-or-human/horses')
train_human_dir = os.path.join('/tmp/horse-or-human/humans')

valid_horse_dir = os.path.join('/tmp/validation-horse-or-human/horses')
valid_human_dir = os.path.join('/tmp/validation-horse-or-human/humans')

train_horse_names = os.listdir(train_horse_dir)
print(train_horse_names[:10])

train_human_names = os.listdir(train_human_dir)
print(train_human_names[:10])

valid_horse_names = os.listdir(valid_horse_dir)
print(valid_horse_names[:10])
valid_human_names = os.listdir(valid_human_dir)
print(valid_human_names[:10])

print('The total number of horse images for training : ', len(os.listdir(train_horse_dir)))
print('The total number of human images for training : ', len(os.listdir(train_human_dir)))
print('The total number of horse images for validation : ', len(os.listdir(valid_horse_dir)))
print('The total number of human images for validation : ', len(os.listdir(valid_human_dir)))

categories = os.listdir('/tmp/horse-or-human')
categories

train_path = '/tmp/horse-or-human'
train_images = []
for category in categories:
  folder = train_path + '/' + category
  train_images.append(len(os.listdir(folder)))

import matplotlib.pyplot as plt
import seaborn as sns

sns.barplot(x=categories, y=train_images)
plt.show()

"""Plot some images"""

import matplotlib.image as mpimg

# plotting the images od shape 5x5
n_rows = 5
n_columns = 5

# idx for iterating over the images
pic_ind = 0

fig = plt.gcf() # get current figure (if no current figure exists then a new one is created using figure())
fig.set_size_inches(n_columns*5, n_rows*5)

# get the path for the figures
next_horse_pic = [os.path.join(train_horse_dir, fname) for fname in train_horse_names[pic_ind:pic_ind+10]]
next_human_pic = [os.path.join(train_human_dir, fname) for fname in train_human_names[pic_ind:pic_ind+10]]

for i, img_path in enumerate(next_horse_pic+next_human_pic):
  plt.subplot(n_rows, n_columns, i+1)
  plt.axis(False)
  img = mpimg.imread(img_path)
  plt.imshow(img)

plt.show()

"""## Building the model"""

import tensorflow as tf

model = tf.keras.Sequential([# First Convolution layer
                             tf.keras.layers.Conv2D(16, (3, 3), activation=tf.nn.relu, input_shape=(300, 300, 3)),
                             tf.keras.layers.MaxPool2D(2, 2),
                             # Second Convolution layer
                             tf.keras.layers.Conv2D(32, (3, 3), activation=tf.nn.relu),
                             tf.keras.layers.MaxPool2D(2, 2),
                             # Third Convolution layer
                             tf.keras.layers.Conv2D(64, (3, 3), activation=tf.nn.relu),
                             tf.keras.layers.MaxPool2D(2, 2),
                             # Fourth Convolution layer
                             tf.keras.layers.Conv2D(64, (3, 3), activation=tf.nn.relu),
                             tf.keras.layers.MaxPool2D(2, 2),
                             # Fifth Convolution layer
                             tf.keras.layers.Conv2D(64, (3, 3), activation=tf.nn.relu),
                             tf.keras.layers.MaxPool2D(2, 2),
                             # Flatten and feed into DNN
                             tf.keras.layers.Flatten(),
                             tf.keras.layers.Dense(512, activation=tf.nn.relu),
                             tf.keras.layers.Dense(1, activation=tf.nn.sigmoid)])

from tensorflow.keras.optimizers import RMSprop

model.compile(optimizer = RMSprop(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])

model.summary()

"""## Data Preprocessing"""

from tensorflow.keras.preprocessing.image import ImageDataGenerator

train_datagen = ImageDataGenerator(1/255)
validation_datagen = ImageDataGenerator(1/255)

train_generator = train_datagen.flow_from_directory('/tmp/horse-or-human',
                                                    target_size=(300, 300),
                                                    batch_size=128,
                                                    class_mode='binary')

validation_generator = validation_datagen.flow_from_directory('/tmp/validation-horse-or-human',
                                                              target_size=(300, 300),
                                                              batch_size=32,
                                                              class_mode='binary')

history = model.fit(
    train_generator,
    steps_per_epoch=8,
    epochs=15,
    verbose=1,
    validation_data=validation_generator,
    validation_steps=8
)

import matplotlib.pyplot as plt

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']

epochs = range(len(acc))

plt.figure(figsize=(16, 5))
plt.plot(epochs, acc, 'r', label='Training accuracy')
plt.plot(epochs, val_acc, 'b', label='Validation accuracy')
plt.title('Training and validation accuracy')
plt.legend()
plt.figure()

plt.figure(figsize=(16, 5))
plt.plot(epochs, loss, 'r', label='Training Loss')
plt.plot(epochs, val_loss, 'b', label='Validation Loss')
plt.title('Training and validation loss')
plt.legend()

plt.show()

"""## Visulaizing the intermideiate Representations"""

import numpy as np
import random
from tensorflow.keras.preprocessing import image

layers_outputs = [layer.output for layer in model.layers]
visulaization_model = tf.keras.models.Model(inputs=model.inputs, outputs=layers_outputs)

# Let's prepare a random input image from the training set.
horse_img_files = [os.path.join(train_horse_dir, f) for f in train_horse_names]
human_img_files = [os.path.join(train_human_dir, f) for f in train_human_names]
img_path = random.choice(horse_img_files+human_img_files)

img = image.load_img(img_path, target_size=(300, 300))
x = image.img_to_array(img) # Numpy array with shape (300, 300, 3)
x = x.reshape((1,) + x.shape) # Numpy array with shape (1, 300, 300, 3)

# Rescale
x = x/255

successive_feature_maps = visulaization_model.predict(x)

layer_names = [layer.name for layer in model.layers]

for layer_name, feature_map in zip(layer_names, successive_feature_maps):
  if len(feature_map.shape)==4:
    n_features = feature_map.shape[-1]
    size = feature_map.shape[1]
    display_grid = np.zeros((size, size*n_features))
    
    for i in range(n_features):
      x = feature_map[0, :, :, i]
      x = x -x.mean()
      x = x/x.std()
      x = x*64 + 128
      x = np.clip(x, 0, 255).astype('uint8')
      display_grid[:, i*size : (i+1)*size] = x

    scale = 20. / n_features 
    plt.figure(figsize=(scale*n_features, scale))
    plt.grid(False)
    plt.title(layer_name)
    plt.imshow(display_grid)

"""## Running the model"""

import numpy as np
from google.colab import files
from keras.preprocessing import image

uploaded = files.upload()

for fn in uploaded.keys():

  # predicting images
  path = '/content/' + fn 
  img = image.load_img(path, target_size=(300, 300))
  plt.figure(figsize=(5, 5))
  plt.imshow(img)
  plt.show()
  x = image.img_to_array(img)
  x = np.expand_dims(x, axis=0)

  images = np.vstack([x])
  classes = model.predict(images, batch_size=10)
  print(classes)
  if classes[0]>0.5:
    print(fn+' is a human')
  else:
    print(fn+' is a horse')

"""Saving the model"""

model.save('my_model.h5')  # creates a HDF5 file 'my_model.h5'

from keras.models import load_model 

mod = load_model('my_model.h5')

import numpy as np
from google.colab import files
from keras.preprocessing import image

#uploaded = files.upload()

for fn in uploaded.keys():

  # predicting images
  path = '/content/' + fn 
  img = image.load_img(path, target_size=(300, 300))
  plt.figure(figsize=(5, 5))
  plt.imshow(img)
  plt.show()
  x = image.img_to_array(img)
  x = np.expand_dims(x, axis=0)

  images = np.vstack([x])
  classes = mod.predict(images, batch_size=10)
  print(classes)
  if classes[0]>0.5:
    print(fn+' is a human')
  else:
    print(fn+' is a horse')