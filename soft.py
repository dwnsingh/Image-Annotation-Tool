import matplotlib
matplotlib.use("TkAgg")
from tkinter import *
from tkinter import filedialog
import os
from PIL import Image
from PIL import ImageTk	
from tkinter import messagebox
import process_img
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import animation
from matplotlib.figure import Figure
import csv
import pandas as pd
import numpy as np
from functools import partial
from matplotlib.widgets import RectangleSelector
from lxml import etree
import xml.etree.cElementTree as ET
plt.rcParams['toolbar'] = 'None'
image2 =Image.open(os.getcwd()+'/ann_tool.png')
#image1 = ImageTk.PhotoImage(image2)
class supreme(Tk):
	
	def __init__(self,*args,**kwargs):
		Tk.__init__(self,*args,**kwargs)
		
		self.title("Floor Plan Annotation Tool")
		self.geometry("1200x1000")
		self.main_menu = Menu(self)
		self.config(menu = self.main_menu)
		self.fileMenu = Menu(self.main_menu,tearoff = False)
		self.main_menu.add_command(label="Open Image",command=self.open_Folder)
		self.folderName = None
		self.baseFolder = os.getcwd()
		self.folderContent = []
		
		self.csv_file_name = ''
		self.xml_file_name = ''

		self.f = Figure(figsize=(5,5),dpi=100)
		self.ax = self.f.add_axes([0,0,1,1])
		self.df = None
		self.s = StringVar()
		self.tl_list = []
		self.br_list = []
		self.t = StringVar()
		#plt.ion()
		self.canvas= Canvas(width=300,height=400)
		self.canvas.pack(pady = 100)
		self.img = ImageTk.PhotoImage(Image.open("ann_tool.gif"))
		self.canvas.create_image(0,0,image=self.img,anchor=NW)

		self.predicted_img = None

	
	def show_pred_image(self,filename):
		os.chdir(self.baseFolder)
		self.predicted_img,json_result = process_img.predict(self.folderName,filename)
		
		self.create_csvFile(json_result,filename)			

		def animate(i):
			self.df = pd.read_csv(self.csv_file_name)
			lt = []
			bt = []
			wl = []
			hl = []
			obj = []
			for j in range(self.df.shape[0]):
				lt.append(self.df.loc[j]['xleft'])
				bt.append(self.df.loc[j]['yleft'])
				wl.append(self.df.loc[j]['width'])
				hl.append(self.df.loc[j]['height'])
				obj.append(self.df.loc[j]['label'])

			self.ax.clear()
			self.ax.imshow(self.predicted_img)
			#print('inside')
			self.ax.axis('off')
			for left,bottom,w,h,ob in zip(lt,bt,wl,hl,obj):
				p = patches.Rectangle((left,bottom),w, h,linewidth=1,edgecolor='r',facecolor='none')
				self.ax.add_patch(p)
				self.ax.text(left+w, bottom, ob, horizontalalignment='right', verticalalignment='bottom')

			self.ax.plot()

		
		
		
		if self.canvas !=None:
			self.canvas.destroy()
			
		self.canvas = FigureCanvasTkAgg(self.f,self)
		self.canvas.draw()
		self.canvas.get_tk_widget().pack(side=TOP,fill=BOTH,expand=True)

		toolbar = NavigationToolbar2TkAgg(self.canvas,self)
		toolbar.update()
		self.canvas._tkcanvas.pack(side=TOP,fill=BOTH,expand=True)

		destr_button = Button(self, text="Discard",fg='red', command=self.discardFile)
		destr_button.pack(side=LEFT,padx=10,pady=5)

		conf_button = Button(self, text="Confirm",fg='green', command=self.confirmFile)
		conf_button.pack(side=LEFT,padx=10,pady=5)


		
		def onclick(event):
			xcord = event.xdata
			ycord = event.ydata
			for j in range(self.df.shape[0]):
				if (between(xcord,self.df.loc[j]['xleft'],self.df.loc[j]['xleft']+self.df.loc[j]['width']) and 
					between(ycord,self.df.loc[j]['yleft'],self.df.loc[j]['yleft']+ self.df.loc[j]['height'])):
		
					top = Toplevel()
					top.geometry('200x120+'+str(np.random.randint(low=100,high=200))+'+'+ str(np.random.randint(low=100,high=200)))
					top.title('Edit Object')
		
					button1 = Button(top,text="Delete",bg='red',command=partial(deleteObj,j))
					button1.pack()
		
					entry = Entry(top,textvariable=self.s)
					self.s.set(root.df.loc[j]['label'])
					entry.pack()
					button2 = Button(top,text="Save",bg='green',command=partial(saveObj,j))
					button2.pack()
				else:
					if event.dblclick:
						toggle_selector.RS = RectangleSelector(
		        			self.ax, line_select_callback,
		        			drawtype='box', useblit=True,
		        			button=[1], minspanx=5, minspany=5,
		        			spancoords='pixels', interactive=True
		    				)
		
		

		def between(x,l,r):
			if x >=l and x <= r:
				return True
			else:
				return False

		def deleteObj(obj_id):
			print(obj_id)
			self.df.drop([obj_id],axis=0,inplace=True)
			df2 = self.df
			df2.to_csv(self.csv_file_name, index=False) 

		def saveObj(obj_id):
			obj_name = self.s.get()
			self.df['label'][obj_id] = obj_name
			df2 = self.df
			df2.to_csv(self.csv_file_name, index=False)

		def saveNewObj(tl,br):
			df2 = pd.DataFrame([[tl[0],tl[1],br[0]-tl[0],br[1]-tl[1],self.t.get(),0.5]],
					columns=['xleft','yleft','width','height','label','confidence'])
			result = self.df.append(df2,ignore_index=True)
			result.to_csv(self.csv_file_name, index=False)	
		
			self.tl_list = []
			self.br_list = []
			self.t.set('')
			#print('saveNewObj')
			toggle_selector.RS.set_active(False)
		

		def toggle_selector(event):
			toggle_selector.RS.set_active(True)


		def line_select_callback(clk, rls):
		
			#print('line line_select_callback')
			self.tl_list.append(int(clk.xdata))
			self.tl_list.append(int(clk.ydata))
			self.br_list.append(int(rls.xdata))
			self.br_list.append(int(rls.ydata))

			top = Toplevel()
			top.geometry('200x120+'+str(np.random.randint(low=100,high=200))+'+'+str(np.random.randint(low=100,high=200)))
			top.title('Add Object')
			lb = Label(top,text='Enter Object Name')
			lb.pack()
			entry = Entry(top,textvariable=self.t)
			entry.pack()
			button2 = Button(top,text="Save",bg='green',command=partial(saveNewObj,self.tl_list,self.br_list))
			button2.pack()

		toggle_selector.RS = RectangleSelector(
			        self.ax, line_select_callback,
			        drawtype='box', useblit=True,
			        button=[1], minspanx=5, minspany=5,
			        spancoords='pixels', interactive=True
			    )
		bbox = plt.connect('key_press_event', toggle_selector)

		cid = self.f.canvas.mpl_connect('button_press_event', onclick)

		ani = animation.FuncAnimation(self.f, animate, interval=1000)
		#print('after')
		plt.show()
		#plt.close()



	def create_csvFile(self,result,filename):
		self.csv_file_name = 'Z' + filename.split('.')[0] + '.csv'
		#currFolder = os.getcwd()
		os.chdir(self.folderName)

		with open(self.csv_file_name, mode='w') as csv_file:
			fieldnames = ['xleft', 'yleft','width','height', 'label','confidence']
			writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

			writer.writeheader()
			for i,eachline in enumerate(result):
				writer.writerow({
					'xleft': eachline['topleft']['x'],
					'yleft' : eachline['topleft']['y'],
					'width': eachline['bottomright']['x'] - eachline['topleft']['x'],
					'height': eachline['bottomright']['y'] - eachline['topleft']['y'],
					'label' : eachline['label'],
					'confidence':eachline['confidence']})
				
		
		

	def create_xmlFile(self,savedir):
		
		def write_xml(objects,tl,br,savedir):
			height, width, depth = self.predicted_img.shape  

			annotation = ET.Element('annotation')
			# ET.SubElement(annotation, 'folder').text = folder
    			ET.SubElement(annotation, 'filename').text = self.folderContent[0] 
    			ET.SubElement(annotation, 'segmented').text = '0'
    			size = ET.SubElement(annotation, 'size')
    			ET.SubElement(size, 'width').text = str(width)
    			ET.SubElement(size, 'height').text = str(height)
    			ET.SubElement(size, 'depth').text = str(depth)
    			for obj, topl, botr in zip(objects, tl, br):
        			ob = ET.SubElement(annotation, 'object')
        			ET.SubElement(ob, 'name').text = obj
        			ET.SubElement(ob, 'pose').text = 'Unspecified'
        			ET.SubElement(ob, 'truncated').text = '0'
        			ET.SubElement(ob, 'difficult').text = '0'
        			bbox = ET.SubElement(ob, 'bndbox')
        			ET.SubElement(bbox, 'xmin').text = str(topl[0])
        			ET.SubElement(bbox, 'ymin').text = str(topl[1])
        			ET.SubElement(bbox, 'xmax').text = str(botr[0])
        			ET.SubElement(bbox, 'ymax').text = str(botr[1])

    			xml_str = ET.tostring(annotation)
    			root = etree.fromstring(xml_str)
    			xml_str = etree.tostring(root, pretty_print=True)
    			save_path = os.path.join(savedir, self.folderContent[0].replace('jpg', 'xml'))
    			with open(save_path, 'wb') as temp_xml:
        			temp_xml.write(xml_str)


		objects = []
    		tl = []
    		br = []
		for j in range(self.df.shape[0]):
        		tl.append((self.df.loc[j]['xleft'],self.df.loc[j]['yleft']))
        		br.append((self.df.loc[j]['xleft']+self.df.loc[j]['width'],self.df.loc[j]['yleft']+self.df.loc[j]['height']))
        		objects.append(self.df.loc[j]['label'])

		write_xml(objects,tl,br,savedir)
		
			
	def open_Folder(self):

		options = {}
		options['initialdir'] = self.baseFolder
		options['title'] = 'choose a folder'
		options['mustexist'] = False
		self.folderName = filedialog.askdirectory(**options)

		if self.folderName is not None:
			print(self.folderName)
			self.folderContent = os.listdir(self.folderName)
			self.folderContent = [files for files in self.folderContent if 'jpg' in files]   #check it
			self.folderContent.sort()
			#print(self.folderContent)

			if 'discard' in self.folderContent:
				self.folderContent.remove('discard')
			if 'confirm' in self.folderContent:
				self.folderContent.remove('confirm')

			#os.chdir(self.folderName)
			#print(self.folderContent)
		else:
			print('folder not found')
			exit()

		self.show_pred_image(self.folderContent[0])
		


	def discardFile(self):
		save_discard = 'discard'
		#currFolder = os.getcwd()
		#os.chdir(self.folderName)
		print(os.getcwd())
		if os.path.exists(os.path.join(self.folderName,save_discard)) == False:
			os.mkdir(save_discard)

		
		os.rename(self.folderContent[0],os.path.join(save_discard,self.folderContent[0]))
		
		self.folderContent.pop(0)
		os.remove(self.csv_file_name) 		#check it
		

		if len(self.folderContent) != 0:
			self.show_pred_image(self.folderContent[0])
		else:
			messagebox.showerror('Message','All the Images are Processed')


	def confirmFile(self):
		save_confirm = 'confirm'
		#currFolder = os.getcwd()
		#os.chdir(self.folderName)
		print(os.getcwd())
		if os.path.exists(os.path.join(self.folderName,save_confirm)) == False:
			os.mkdir(save_confirm)

		self.create_xmlFile(save_confirm)
		os.rename(self.folderContent[0], os.path.join(save_confirm, self.folderContent[0]))
		#os.chdir(self.baseFolder)
		self.folderContent.pop(0)
		os.remove(self.csv_file_name)		#check it
		

		if len(self.folderContent) != 0:
			self.show_pred_image(self.folderContent[0])
		else:
			messagebox.showerror('Message', 'All the Images are Processed')



	
	

	

root = supreme()

root.mainloop()

