import libsvm
import argparse
from cPickle import load
from learn import extractSift, computeHistograms, writeHistogramsToFile
from PIL import Image
import sys
import ImageChops, ImageDraw, ImageFont, ImageFilter
import os
import glob
import re

from split_img import splitImage
from classify_single import classifySingle

HISTOGRAMS_FILE = 'testdata.svm'
CODEBOOK_FILE = 'codebook.file'
MODEL_FILE = 'trainingdata.svm.model'

def parse_arguments():
    parser = argparse.ArgumentParser(description='classify images with a visual bag of words model')
    parser.add_argument('-c', help='path to the codebook file', required=False, default=CODEBOOK_FILE)
    parser.add_argument('-m', help='path to the model  file', required=False, default=MODEL_FILE)
    parser.add_argument('input_images', help='images to classify', nargs='+')
    args = parser.parse_args()
    return args


answer = raw_input("Is this image a mosaic? Please type 'y' or 'n' and then press enter. ")
if answer == 'y':
	splitImage(parse_arguments())	#mosaic
elif answer == 'n':
	classifySingle(parse_arguments())	#single image
else:
	print "Please type 'y' or 'n'. "