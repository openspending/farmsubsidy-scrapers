import os
import base64
import glob
import time
import os
import io

import numpy as np

from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img
from keras.optimizers import Adam
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras.layers.normalization import BatchNormalization


from PIL import Image


NOISE_BACKGROUND = (255, 255, None)
BACKGROUND = (255, 255, 255)
TEXT_NOISE = (0, 5, 255)
TEXT = (0, 0, 0)
NOISE = (0, 0, 0)
THRESHOLD = 140

CLASSES = ['3', '4', '6', '7', '8', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'k', 'r', 's', 't', 'v', 'x', 'y']
IMG_SIZE = (22, 50)


def normalize_color(im, from_color, to_color, threshold):
    im = im.copy()
    w, h = im.size
    for i in range(w):
        for j in range(h):
            p = im.getpixel((i, j))
            if not isinstance(p, tuple):
                p = (p,)
            diff = [abs(x - from_color[k]) for k, x in enumerate(p) if from_color[k] is not None]
            if all(map(lambda x: x < threshold, diff)):
                im.putpixel((i, j), to_color)
    return im

def non_white(p_list):
    diff = [abs(x - BACKGROUND[i]) for p in p_list for i, x in enumerate(p)]
    return any(map(lambda x: x > 0, diff))

def all_white(p_list):
    diff = [abs(x - BACKGROUND[i]) for p in p_list for i, x in enumerate(p)]
    return all([x == 0 for x in diff])

def check_image(im, width_range, check_func=non_white):
    w, h = im.size
    for i in width_range:
        if check_func((im.getpixel((i, j))) for j in range(h)):
            return i

def find_start_end(im):
    w, h = im.size
    start = check_image(im, range(w))
    end = check_image(im, range(w - 1, -1, -1))
    return start, end

def crop_start_end(im):
    start, end = find_start_end(im)
    box = (start, 0, end, im.size[1])
    return im.crop(box)

def get_empty_spaces(im):
    w, h = im.size
    x = check_image(im, range(0, w), check_func=non_white)
    empty_spots = []
    last_spot = None
    while True:
        empty = check_image(im, range(x, w), check_func=all_white)
        if empty is None:
            break
        if empty >= w - 1:
            break
        if last_spot is None:
            empty_spots.append(empty)
        else:
            if abs(empty - last_spot) > 1:
                empty_spots.append(last_spot)
                empty_spots.append(empty)
        last_spot = empty
        x = empty + 1
    empty_spots.append(last_spot)
    return [(empty_spots[i], empty_spots[i + 1]) for i in range(0, len(empty_spots) - 1, 2)]

def crop_by_splits(image, splits):
    w, h = image.size
    x = 0
    for a, b in splits:
        yield image.crop((x, 0, a, h))
        x = b


class LetterSplitter():
    def __init__(self, image, letter_count=6):
        self.image = image
        self.w, self.h = image.size
        self.letter_count = letter_count
        self.current_letter = 0
        self.x = 0
        self.recalc()

    def recalc(self):
        remaining = self.w - self.x
        self.ideal_width = remaining / (self.letter_count - self.current_letter)
        self.threshold = self.ideal_width / 4
        self.ideal_x = self.x + self.ideal_width

    def make_letter(self, end_x, new_x=None):
        part = self.image.crop((self.x, 0, end_x, h))
        self.current_letter += 1
        if new_x is None:
            self.x = end_x + 1
        else:
            self.x = new_x + 1
        self.recalc()
        return part

    def get_images(self):
        empty_spaces = get_empty_spaces(self.image)
        for a, b in empty_spaces:
            if self.current_letter == self.letter_count:
                break
            if abs(self.ideal_x - a) < self.threshold:
                # split ideal
                yield self.make_letter(a, b)
                continue
            elif self.ideal_x > a:
                # split too early, let's wait for next
                continue
            yield from self.advance(a)
        yield from self.advance(self.w)

    def advance(self, until):
        while self.ideal_x < until - self.threshold and self.current_letter < self.letter_count:
            yield self.make_letter(self.ideal_x)

def alt_split_letters(image):
    splitter = LetterSplitter(image)
    yield from splitter.get_images()

def split_letters(image, letter_count=5):
    w, h = image.size
    part_width = w / letter_count
    parts = []
    for i in range(letter_count):
        yield image.crop((i * part_width, 0, i * part_width + part_width, h))


def normalize_crop(im):
    im = normalize_color(im, NOISE_BACKGROUND, BACKGROUND, THRESHOLD)
    im = normalize_color(im, NOISE, BACKGROUND, THRESHOLD)
    im = normalize_color(im, TEXT_NOISE, TEXT, THRESHOLD)
    im = crop_start_end(im)
    return im

def get_split_letters_from_image(im):
    yield from split_letters(normalize_crop(im))


def resize_images(images):
    for img in images:
        gray = img.convert('L')
        bw = gray.point(lambda x: 0 if x < 128 else 255, '1')
        yield bw.resize(IMG_SIZE)


def letters_from_image(image):
    yield from resize_images(get_split_letters_from_image(image))


def read_solution_images(filename):
    with open(filename) as f:
        count = 0
        for line in f:
            solution, image_data = line.split('|')
            _, image_data = image_data.split(',')
            im = Image.open(io.BytesIO(base64.b64decode(image_data)))
            yield solution, im


def generate_images(filename):
    for solution, image in read_solution_images(filename):
        letter_images = letters_from_image(image)
        yield from zip(solution, letter_images)


def get_letter_onehot(letter):
    index_offset = CLASSES.index(letter)
    num_classes = len(CLASSES)
    labels_one_hot = np.zeros(num_classes)
    labels_one_hot[index_offset] = 1
    return labels_one_hot


def convert_captchas(filename):
    images = []
    letters = []
    for letter, im in generate_images(filename):
        image = img_to_array(im, data_format='channels_last')
        images.append(image)
        letters.append(get_letter_onehot(letter))
    images = np.array(images, dtype='float32')
    labels = np.array(letters)
    perm = np.arange(len(images))
    np.random.shuffle(perm)
    images = images[perm]
    labels = labels[perm]
    return images, labels


def extract_data(filename, recreate=False):
    images_path = os.path.abspath('data/images.npy')
    if not os.path.exists(images_path) or recreate:
        images, labels = convert_captchas(filename)
        np.save(images_path, images)
        labels_path = os.path.abspath('data/labels.npy')
        np.save(labels_path, labels)


def make_model():
    nb_classes = len(CLASSES)
    nb_filters = 32
    # # size of pooling area for max pooling
    pool_size = (2, 2)
    # # convolution kernel size
    kernel_size = (4, 10)
    input_shape = (IMG_SIZE[1], IMG_SIZE[0], 1)

    model = Sequential()

    # model.add(Conv2D(nb_filters, (kernel_size[0], kernel_size[1]),
    #                         padding='valid',
    #                         input_shape=input_shape))
    # model.add(BatchNormalization(axis=-1))
    # model.add(Activation('relu'))
    # model.add(Conv2D(nb_filters, (kernel_size[0], kernel_size[1])))
    # model.add(BatchNormalization(axis=-1))
    # model.add(Activation('relu'))
    # model.add(MaxPooling2D(pool_size=pool_size))
    # model.add(Dropout(0.25))

    model.add(Conv2D(32, (3, 3), input_shape=input_shape))
    model.add(BatchNormalization(axis=-1))
    model.add(Activation('relu'))
    model.add(Conv2D(32, (3, 3)))
    model.add(BatchNormalization(axis=-1))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2,2)))

    model.add(Conv2D(64,(3, 3)))
    model.add(BatchNormalization(axis=-1))
    model.add(Activation('relu'))
    model.add(Conv2D(64, (3, 3)))
    model.add(BatchNormalization(axis=-1))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2,2)))

    model.add(Flatten())

    model.add(Dense(512))
    model.add(BatchNormalization())
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(nb_classes))
    model.add(Activation('softmax'))

#     model.compile(loss='categorical_crossentropy',
#                   optimizer='adadelta',
#                   metrics=['accuracy'])
    model.compile(loss='categorical_crossentropy', optimizer=Adam(), metrics=['accuracy'])


    return model


class CaptchaSolver(object):
    def __init__(self, model=None, model_path=None):
        if model is None:
            self.model = make_model()
            self.model.load_weights(model_path)
        else:
            self.model = model

    def predict_from_bytes(self, content):
        return self.predict(Image.open(io.BytesIO(content)))

    def predict(self, image_data):
        letters = np.array([img_to_array(im, data_format='channels_last')
                    for im in letters_from_image(image_data)])

        predicted = self.model.predict_classes(letters)
        return ''.join(CLASSES[i] for i in predicted)


def show_predicted(cs):
    response = requests.get('https://www.sian.it/pubbAimu/Captcha.jpg')
    img = Image.open(io.BytesIO(response.content))
    display(img)
    return cs.predict(img)