import sys
import cv2
from ForgeryDetection import Detect
import re
from datetime import datetime

def PrintBoundary():
	for i in range(50):
		print('*',end='')
	print()

try:
	file_name=sys.argv[1]
except IndexError:
	print('Enter a path to the image.')
	sys.exit(0)

image=cv2.imread(file_name)
if image is None:
	print(file_name)
	print('Enter Valid File Name/Path.')
	sys.exit(0)

eps =60
min_samples=2

PrintBoundary()
print('Use \'q\' for exit and\n\'s/S\' for saving the Forgery Detected.')
PrintBoundary()
flag=True

try:
	value=sys.argv[2]

except IndexError:
	flag=False
if flag:
	try:
		value=int(value)
		if(value<0 or value> 500):
			print('Value not in range (0,500)........ using default value.')
		else:
			eps= value
	except ValueError:
		print('Value not integer........ using default value.')

flag2=True
try:
	value=sys.argv[3]
except IndexError:
	flag2=False

if flag2:
	try:
		value=int(value)
		if(value<0 or value> 50):
			print('Value not in range (0,50)........ using default value.')
		else:
			min_samples= value
	except ValueError:
		print('Value not integer........ using default value.')

PrintBoundary()
print('Detecting Forgery with parameter value as\neps:{}\nmin_samples:{}'.format(eps,min_samples))
PrintBoundary()

detect=Detect(image)

key_points,descriptors = detect.siftDetector()

forgery=detect.locateForgery(eps,min_samples)
if forgery is None:
	sys.exit(0)
cv2.imshow('Original image',image)
cv2.imshow('Forgery',forgery)
wait_time=1000
while(cv2.getWindowProperty('Forgery', 0) >= 0) or (cv2.getWindowProperty('Original image', 0) >= 0) :
	keyCode = cv2.waitKey(wait_time)
	if (keyCode) == ord('q') or keyCode==ord('Q'):
		cv2.destroyAllWindows()
		break
	elif keyCode == ord('s') or keyCode ==ord('S'):
		name=re.findall(r'(.+?)(\.[^.]*$|$)',file_name)
		date=datetime.today().strftime('%Y_%m_%d_%H_%M_%S')
		new_file_name=name[0][0]+'_'+str(eps)+'_'+str(min_samples)
		new_file_name=new_file_name+'_'+date+name[0][1]
		PrintBoundary()
		
		vaue=cv2.imwrite(new_file_name,forgery)
		print('Image Saved as....',new_file_name)

cv2.destroyAllWindows()


