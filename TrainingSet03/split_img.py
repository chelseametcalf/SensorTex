from PIL import Image
import numpy as np
from scipy.stats import mode

from classify_subwindows import classify

def parse_arguments():
    parser = argparse.ArgumentParser(description='classify images with a visual bag of words model')
    parser.add_argument('-c', help='path to the codebook file', required=False, default=CODEBOOK_FILE)
    parser.add_argument('-m', help='path to the model  file', required=False, default=MODEL_FILE)
    parser.add_argument('input_images', help='images to classify', nargs='+')
    args = parser.parse_args()
    return args

def splitImage(args):
	print "---------------------"
	print "Spliting up the image..."

	# get test image
	im = Image.open(args.input_images[0])
	xsize, ysize = im.size
	
	subWindowSize = 32, 32
	overlapWindows = 4, 4
	halfWindowSize = (subWindowSize[0]/2, subWindowSize[1]/2)
	stepSize = (subWindowSize[0]/overlapWindows[0], subWindowSize[1]/overlapWindows[1])
	xcover = xsize-halfWindowSize[0]
	ycover = ysize-halfWindowSize[1]
	mciPixels = np.empty((overlapWindows[0], overlapWindows[1], xsize, ysize))
	mciPixels[:,:,:,:] = -1
	maxVote = 0
	hist = np.zeros(4)
	total = 0
	maxMaterials = 4
	mci = np.empty((xsize, ysize))
	maxProb = np.empty((xsize, ysize))

	# iterate through subwindows
	for xcenter in range(halfWindowSize[0], xsize-halfWindowSize[0], stepSize[0]):
		for ycenter in range(halfWindowSize[1], ysize-halfWindowSize[1], stepSize[1]):				
			box = (xcenter-halfWindowSize[0], ycenter-halfWindowSize[1], xcenter+halfWindowSize[0], ycenter+halfWindowSize[1])
			subwindow = subImage(box, im)
			#subwindow.show()
			subwindowfname = "subwindows/subwindow_" + str(xcenter) + "_" + str(ycenter) + ".png"
			subwindow.save(subwindowfname)
			print "Subwindow file name: " + subwindowfname
			print "---------------------"
			tempMID = classify(subwindowfname, args)
			print str(tempMID)
			x = xcenter/stepSize[0]
			y = ycenter/stepSize[1]
			mciPixels[x % overlapWindows[0], y % overlapWindows[1], (xcenter-halfWindowSize[0]):(xcenter+halfWindowSize[0]), (ycenter-halfWindowSize[1]):(ycenter+halfWindowSize[1])] = tempMID

	# find mode
	print "Determining max vote"
	print "---------------------"
	for x in range(1, xsize):
		for y in range(1, ysize):
			for i in range(1, overlapWindows[0]):
				for j in range(1, overlapWindows[1]):
					maxVote = mciPixels[i][j][x][y]
					if(maxVote == -1):		# not classified
						continue
					total = total + 1
					hist[maxVote/40] = hist[maxVote/40] + 1

			maxID = 0
			maxVote = hist[0]

			for k in range (1, maxMaterials):
				if(hist[k] > maxVote/40):
					maxID = k
					maxVote = hist[k]

			mci[x][y] = maxID * 40
			maxProb[x][y] = maxVote/total
			

def subImage(box, im):
	region = im.crop(box)
	return region
