from darkflow.net.build import TFNet
import cv2
import matplotlib.pyplot as plt
import numpy as np
import os

def predict(folder,filename):

	photo = os.path.join(folder,filename)
	#print(type(photo))

	options = {
		"model": "cfg/tiny-yolo-voc-12c.cfg", 
		"load": 4000, 
		"threshold": 0.1,
		"GPU":1
			}

	tfnet = TFNet(options)

	# images = load_images_from_folder("./sample_img/*.jpg")
	# photo = os.path.join(folder,filename)
	#print(photo)
	imgcv = cv2.imread(photo)
	# imgcv = cv2.cvtColor(imgcv,cv2.COLOR_BGR2RGB)
	result = tfnet.return_predict(imgcv)
	print(result)

	'''for i in range(len(result)):
		t1 = (result[i]['topleft']['x'],result[i]['topleft']['y'])
		b1 = (result[i]['bottomright']['x'],result[i]['bottomright']['y'])
		label = (result[i]['label'])
		confidence = int(result[i]['confidence']*100)
		name = label + ' ' +  str(confidence)+'%'
		col = np.random.rand(3)*255
		imgcv = cv2.rectangle(imgcv,t1,b1,(col),7)
		imgcv = cv2.putText(imgcv,name,t1,cv2.FONT_HERSHEY_DUPLEX,1.5,(col),2)'''
	
	#plt.imshow(imgcv)
	#plt.show()
	return (imgcv,result)

if __name__ == "__main__":
	predict(folder,filename)

