from numpy import *
from PIL import Image
import time
import os

bins = 4
rv = 256

def signature(img, sec):
    im = img.convert('RGB')
    W,H = im.size
    colors = im.getcolors(W*H)

    d = {}
    for count, color in colors:
       k = [int(x / (256 / sec)) for x in color]
       k = str(k)
       if k not in d:
           d[k] = []
       d[k].append(count)

    hashes = []
    for r in range(0, sec):
        for g in range(0, sec):
            for b in range(0, sec):
                k = str([r, g, b])
                v = sum(d[k]) if k in d else 0
                hashes.append(v)
    return hashes

def sketch(M, k):
    w,h = M.shape

    rand = random.randn(k, h)

    sketches = zeros((k,w))

    for i in range(k):
        for j in range(w):
            v = dot(rand[i], M[j])
            if v > 0:
                sketch = 1
            else:
                sketch = 0
            sketches[i][j] = sketch
    return sketches

def cossim(s1, s2):
    result = dot(s1, s2) / dot(linalg.norm(s1), linalg.norm(s2))

    if allclose(result, 1):
        ac = 0
    else:
        ac = arccos(result)
    return 1 - ac

def loadImages(path):
    imagesList = os.listdir(path)
    loadedImages = []
    for image in imagesList:
        img = Image.open(path + image)
        loadedImages.append(img)
    return loadedImages

def findsim(filenames, query_filename = "data/anchor/image_0001.jpg"):
    imgs = []
    for filename in filenames:
        img = Image.open(filename)
        imgs.append(img)
    mat = zeros(int(math.pow(bins, 3)), dtype = int)

    for img in imgs:
        sigs = signature(img, bins)
        mat = vstack((sigs, mat))

    mat = mat[:-1]

    sketches = sketch(mat, rv)

    pic_sketch = sketch(array([signature(Image.open(query_filename).convert('RGB'), bins)]), rv)

    scores = dot(transpose(pic_sketch), sketches)
    print (scores)
    n = 10
    top_n = argsort(scores)[-n:][::-1]
    return top_n









