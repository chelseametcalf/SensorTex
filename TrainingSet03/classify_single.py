import libsvm
import argparse
from cPickle import load
from learn import extractSiftSingle, computeHistograms, writeHistogramsToFile
import sys
import Image, ImageChops, ImageDraw, ImageFont, ImageFilter
import os
import glob
import re

HISTOGRAMS_FILE = 'testdata.svm'
CODEBOOK_FILE = 'codebook.file'
MODEL_FILE = 'trainingdata.svm.model'

def draw_text_with_halo(img, position, text, font, col, halo_col):
    halo = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(halo).text(position, text, font = font, fill = halo_col)
    blurred_halo = halo.filter(ImageFilter.BLUR)
    ImageDraw.Draw(blurred_halo).text(position, text, font = font, fill = col)
    return Image.composite(img, blurred_halo, ImageChops.invert(blurred_halo))

def parse_arguments():
    parser = argparse.ArgumentParser(description='classify images with a visual bag of words model')
    parser.add_argument('-c', help='path to the codebook file', required=False, default=CODEBOOK_FILE)
    parser.add_argument('-m', help='path to the model  file', required=False, default=MODEL_FILE)
    parser.add_argument('input_images', help='images to classify', nargs='+')
    args = parser.parse_args()
    return args

# Uncomment @profile if want to do a profile by adding in: -m memory_profiler
#@profile
def classifySingle(args):
	#print "---------------------"
	#print "## extract Sift features"
	all_files = []
	all_files_labels = {}
	all_features = {}

	args = parse_arguments()
	model_file = args.m
	codebook_file = args.c
	fnames = args.input_images
	all_features = extractSiftSingle(fnames)
	for i in fnames:
	    all_files_labels[i] = 0  # label is unknown

	#print "---------------------"
	#print "## loading codebook from " + codebook_file
	with open(codebook_file, 'rb') as f:
	    codebook = load(f)

	#print "---------------------"
	#print "## computing visual word histograms"
	all_word_histgrams = {}
	for imagefname in all_features:
	    word_histgram = computeHistograms(codebook, all_features[imagefname])
	    all_word_histgrams[imagefname] = word_histgram

	#print "---------------------"
	#print "## write the histograms to file to pass it to the svm"
	nclusters = codebook.shape[0]
	writeHistogramsToFile(nclusters,
		              all_files_labels,
		              fnames,
		              all_word_histgrams,
		              HISTOGRAMS_FILE)

	#print "---------------------"
	#print "## test data with svm"
	#print libsvm.test(HISTOGRAMS_FILE, model_file)

	f = open('material_IDs.dat', 'r')
	result = str(libsvm.test(HISTOGRAMS_FILE, model_file))
	result = result.rstrip("]")
	result = result.lstrip("[")
	result = int(result) + 1
	for x in range(0, result):
		l = f.readline()
	num, name = l.split("-")
	mID = int(num)
	resultText = name.rstrip("\n")
	print(resultText)

	im = Image.open(sys.argv[5])
	font = ImageFont.truetype("TrebuchetMSBold.ttf", 25)

	text_col = (0, 255, 0) # bright green
	halo_col = (0, 0, 0)   # black
	i2 = draw_text_with_halo(im, (5, 5), resultText, font, text_col, halo_col)
	#i2.show()
	
	for infile in sys.argv[5:]:
		fname1 = os.path.splitext(infile)[0] + "_mci"

	pixels = im.load() # create the pixel map

	for i in range(0, im.size[0]):    # for every pixel:
	    for j in range(0, im.size[1]):
		pixels[i,j] = (mID, mID, mID, 255) # set the color accordingly

	#im.show()
	im.save(fname1, "tiff")
	return sys.argv[5] + '   Classification: ' + resultText
