from matplotlib import pyplot as plt
import gc, time, math

class BMP:
	def __init__(self, height, width):
		self.height = height
		self.width = width
		self.true_size = width
		self.x = 0
		self.y = 0
		self.line_len = 0
		self.count = 0

		self.bmp_header = bytearray([
		0x42, 0x4D, # 'B', 'M' - bmp file signature
		0, 0, 0, 0, # file size (dynamic)
		0, 0, 0, 0, # reserved (means nothing)
		62, 0, 0, 0 # at what byte does the image start
		])

		width_b = width.to_bytes(4, 'little')
		height_b = height.to_bytes(4, 'little')

		self.dib_header = bytearray([ 
			40, 0, 0, 0, # size of this header (constant 40 for BITMAPINFOHEADER)
			width_b[0], width_b[1], width_b[2], width_b[3], # image width
			height_b[0], height_b[1], height_b[2], height_b[3], # image height
			1, 0, # Planes (must be one)
			1, 0, # bits per pixel
			0, 0, 0, 0, # compression (none)
			0, 0, 0, 0, # image size (can be 0 for uncrompressed)
			0, 0, 0, 0, # x pixels per meter (not used)?
			0, 0, 0, 0, # y pixels per meter (not used)?
			2, 0, 0, 0, # Total colors (0=default)?
			0, 0, 0, 0  # Important colors (0=all)?
		])

		self.color_palette = bytearray([
            0, 0, 0, 0,  # Black
            255, 255, 255, 0  # White
        ])

		bytes_per_row = (self.width + 7) // 8 # +7 pushes amount to next whole number that is (int) divided by 8
		
		# bmp requires that each row of pixel data (width x bytes per pixel)
		# must have a total size that is divisible by 4.
		# if it is not, extra padding bytes (0x00) must be added at the end of each row
		self.row_padding = (4-(bytes_per_row%4))%4
			# bytes_per_row%4 - finds remainder bytes
			# 4-(bytes_per_row % 4) - how many bytes are needed as filler in each row
			# (4-(bytes_per_row%4))%4 - in case no padding is needed
			
		self.row_size = bytes_per_row + self.row_padding

		image_size = height * self.row_size # height amount of rows
		file_size = 62 + image_size # sum of header and image bytes
		self.bmp_header[2:6] = file_size.to_bytes(4, 'little') # converts file_size into a 4-byte little-endian representation
			# 4 byte little endian meaning that when the number is converted into hex form (0x00000000),
			# it is divided into 4 pairs and then arranged in the array in such a way that the LSB is added first and MSB is added last.
			# *'big'(-endian) - MSB first, LSB last*

		# generate black bmp sheet of pixels
		self.pixel_data = bytearray([0]*image_size)

	# change one pixel
	def set_pixel(self, x, y):
		self.count+=1
		if 0 <= x < self.width and 0 <= y < self.height:
			index = (self.height-1-y) * self.row_size + (x // 8) # find exact byte
			bit = 7 - (x % 8) # find index of the bit inside of the byte

			self.pixel_data[index] |= (1 << bit)
				# at the index where the byte is, insert (bitwise left shift) a 1 into the index bit (0-7)
				# the use bitwise OR assign to apply it

	# draw vertical line
	def vertical_line(self, x, y):
		for y in (range(y[0], y[1]+1) if y[0] < y[1] else range(y[1], y[0]+1)):
			self.count +=1
			self.set_pixel(x, y)

	# draw horizontal line
	def horizontal_line(self, x, y):
		for x in (range(x[0], x[1]) if x[0] < x[1] else range(x[1], x[0])):
			self.count +=1
			self.set_pixel(x, y)
	
	def draw_line(self, x, y):
		self.count+=1
		if x[0] != x[1]:
			self.horizontal_line(x, y[0])
		else:
			self.vertical_line(x[0], y)
	
	# # type - section in the fractal
	# def rec_minkowski(self, n, type):
	# 	self.count += 1
	# 	if (self.x>=self.width):
	# 		return
	# 	elif (n<=0): # when max depth is reached start drawing
	# 		match type:
	# 			case 'left':
	# 				#print('left')
	# 				self.horizontal_line(self.y, self.x, self.x-self.line_len)
	# 				self.x = self.x - self.line_len # save last position to use later
	# 			case 'right':
	# 				#print('right')
	# 				self.horizontal_line(self.y, self.x, self.x+self.line_len+1)
	# 				self.x = self.x + self.line_len
	# 			case 'down':
	# 				#print('down')
	# 				self.vertical_line(self.x, self.y, self.y+self.line_len+1)
	# 				self.y = self.y + self.line_len
	# 			case'up':
	# 				#print('up')
	# 				self.vertical_line(self.x, self.y, self.y-self.line_len)
	# 				self.y = self.y - self.line_len
	# 	else:
	# 		match type:
	# 			case 'left':
	# 				self.rec_minkowski(n-1, 'left')
	# 				self.rec_minkowski(n-1, 'down')
	# 				self.rec_minkowski(n-1, 'left')
	# 				self.rec_minkowski(n-1, 'up')
	# 				self.rec_minkowski(n-1, 'up')
	# 				self.rec_minkowski(n-1, 'left')
	# 				self.rec_minkowski(n-1, 'down')
	# 				self.rec_minkowski(n-1, 'left')
	# 			case 'right':
	# 				self.rec_minkowski(n-1, 'right')
	# 				self.rec_minkowski(n-1, 'up')
	# 				self.rec_minkowski(n-1, 'right')
	# 				self.rec_minkowski(n-1, 'down')
	# 				self.rec_minkowski(n-1, 'down')
	# 				self.rec_minkowski(n-1, 'right')
	# 				self.rec_minkowski(n-1, 'up')
	# 				self.rec_minkowski(n-1, 'right')
	# 			case 'up':
	# 				self.rec_minkowski(n-1, 'up')
	# 				self.rec_minkowski(n-1, 'left')
	# 				self.rec_minkowski(n-1, 'up')
	# 				self.rec_minkowski(n-1, 'right')
	# 				self.rec_minkowski(n-1, 'right')
	# 				self.rec_minkowski(n-1, 'up')
	# 				self.rec_minkowski(n-1, 'left')
	# 				self.rec_minkowski(n-1, 'up')
	# 			case 'down':
	# 				self.rec_minkowski(n-1, 'down')
	# 				self.rec_minkowski(n-1, 'right')
	# 				self.rec_minkowski(n-1, 'down')
	# 				self.rec_minkowski(n-1, 'left')
	# 				self.rec_minkowski(n-1, 'left')
	# 				self.rec_minkowski(n-1, 'down')
	# 				self.rec_minkowski(n-1, 'right')
	# 				self.rec_minkowski(n-1, 'down')
	
	def rec_minkowski_depth(self, x, y, n):
		self.count += 2
		fullx = x[1]-x[0] #C1
		fully = y[0]-y[1] #C2

		self.count += 2
		if x[0]>=self.width: #C3
			return
		elif n==0: 			 #C4	
			self.draw_line(x, y) #N^2
			return
		else:

			# C5 * 16
			self.count += 16
			quarterx = fullx//4					
			quartery = fully//4					
			Ax = x[0]+quarterx					
			Ay = y[0]-quartery					
			Mx = x[0]+quarterx*2			
			My = y[0]-quartery*2			
			Fx = x[1]-quarterx			
			Fy = y[1]+quartery			
			Bx = Ax-quartery			
			By = Ay-quarterx			
			Cx = Mx-quartery			
			Cy = My-quarterx			
			Dx = Mx+quartery			
			Dy = My+quarterx			
			Ex = Fx+quartery			
			Ey = Fy+quarterx			
			
			# T(n-1) * 8
			self.rec_minkowski_depth((x[0], Ax), (y[0], Ay), n-1)
			self.count+=1
			self.rec_minkowski_depth((Ax, Bx), 	(Ay, By), 	n-1)
			self.count+=1
			self.rec_minkowski_depth((Bx, Cx), 	(By, Cy), 	n-1)
			self.count+=1
			self.rec_minkowski_depth((Cx, Mx), 	(Cy, My), 	n-1)
			self.count+=1
			self.rec_minkowski_depth((Mx, Dx), 	(My, Dy), 	n-1)
			self.count+=1
			self.rec_minkowski_depth((Dx, Ex), 	(Dy, Ey), 	n-1)
			self.count+=1
			self.rec_minkowski_depth((Ex, Fx), 	(Ey, Fy), 	n-1)
			self.count+=1
			self.rec_minkowski_depth((Fx, x[1]), (Fy, y[1]), n-1)
			self.count+=1

	def rec_minkowski_dim(self, x, y):
		self.count += 2 
		lengthx = (x[1]-x[0])//4 #C1
		lengthy = (y[0]-y[1])//4 #C2

		self.count += 1 # C3
		if ((((-1*self.line_len)<=lengthx<=self.line_len) and x[1]!=x[0]) or
			((-1*self.line_len)<=lengthy<=self.line_len and y[0]!=y[1])): #C4
			self.count += 1
			self.draw_line(x, y) # N^2
			return
		else:
			# C5 * 16
			self.count+=16
			quarterx = lengthx	
			quartery = lengthy	
			Ax = x[0]+quarterx	
			Ay = y[0]-quartery	
			Mx = x[0]+quarterx*2	
			My = y[0]-quartery*2	
			Fx = x[1]-quarterx	
			Fy = y[1]+quartery	
			Bx = Ax-quartery	
			By = Ay-quarterx	
			Cx = Mx-quartery	
			Cy = My-quarterx	
			Dx = Mx+quartery	
			Dy = My+quarterx	
			Ex = Fx+quartery	
			Ey = Fy+quarterx	

			# T(n-1) * 8
			self.count+=1
			self.rec_minkowski_dim((x[0], Ax), (y[0], Ay))
			self.count+=1
			self.rec_minkowski_dim((Ax, Bx), 	(Ay, By))
			self.count+=1
			self.rec_minkowski_dim((Bx, Cx), 	(By, Cy))
			self.count+=1
			self.rec_minkowski_dim((Cx, Mx), 	(Cy, My))
			self.count+=1
			self.rec_minkowski_dim((Mx, Dx), 	(My, Dy))
			self.count+=1
			self.rec_minkowski_dim((Dx, Ex), 	(Dy, Ey))
			self.count+=1
			self.rec_minkowski_dim((Ex, Fx), 	(Ey, Fy))
			self.count+=1
			self.rec_minkowski_dim((Fx, x[1]), (Fy, y[1]))
			self.count+=1

		
	# def draw_minkowski(self, depth, line_len=3): # minimum 3 because at 
	# 	self.line_len = line_len
	# 	self.x = 0
	# 	self.y = self.height//2
	# 	self.rec_minkowski(depth, 'right') # first call to recursion function
	# 	return self.count

	def draw_minkowski_depth(self, depth, line_len=3): # minimum 3 because at 
		self.line_len = line_len
		y = self.height//2
		self.rec_minkowski_depth((0, self.true_size), (y, y), depth) # first call to recursion function
		return self.count
	
	def draw_minkowski_dim(self, width, line_len=3):
		self.line_len = line_len
		y = self.height//2
		self.rec_minkowski_dim((0, width), (y,y))
		return self.count
	
	def calculate_depth(self):
		for n in range(1, 8): # 7 max depth as a precaution as any depth >7 breaches 20k pixel dimensions
			size = ((4**n)*line_len)
			if size>self.width:
				self.true_size = size
				return n

	def generate_image(self, f_name):
		with open(f_name, "wb") as file: # wb - write in binary mode
			file.write(self.bmp_header) 
			file.write(self.dib_header)
			file.write(self.color_palette)
			file.write(self.pixel_data)
		print("BMP file created")

def run_depth(depths):
	t = []
	c = []
	for d in depths:
		size = ((4**d)*line_len)
		start = time.perf_counter()
		image = BMP(size, size)
		#image.horizontal_line((0, 10), 1)
		c.append(image.draw_minkowski_depth(d, line_len))
		image.generate_image(f"output/outputD{d}.bmp")
		end = time.perf_counter()
		t.append(end-start)
		image = None # clear to not hog memory
		gc.collect()
	return (c, t)

def run_width(widths):
	t = []
	c = []
	for w in widths:
		start = time.perf_counter()
		image = BMP(w, w)
		c.append(image.draw_minkowski_dim(w, line_len))  # Starting point and size
		image.generate_image(f"output/outputW{w}.bmp")
		end = time.perf_counter()
		t.append(end-start)
		image = None
		gc.collect()
	return (c, t)

if __name__ == '__main__':
	line_len = 3

	fig, axes = plt.subplots(2, 2, figsize=(12,6)) # 1 line, 2 graphs
	ax1, ax2, ax3, ax4 = axes.flatten()
	fig.suptitle("Graphs of Minkowski sausage performance")

	ds = [x for x in range(1, 8)]

	# depth x ops
	cs, ts = run_depth(ds)
	ax1.plot(ds, cs, '-o')
	ax1.spines['right'].set_visible(False)
	ax1.spines['top'].set_visible(False)
	for i, num in enumerate(cs):
		ax1.annotate(f'{num:.2e}', (ds[i], cs[i]), xytext=(-6,5), textcoords='offset points')
	ax1.set_xlabel('Depth')
	ax1.set_ylabel('Operations')

	# depth x time
	ax3.plot(ds, ts, '-o')
	ax3.spines['right'].set_visible(False)
	ax3.spines['top'].set_visible(False)
	for i, num in enumerate(ts):
		ax3.annotate(f'{num:.2e}', (ds[i], ts[i]), xytext=(-10,5), textcoords='offset points')
	ax3.set_xlabel('Depth')
	ax3.set_ylabel('Time')

	ws = [x for x in range(2000, 20001, 2000)]
	# width x ops
	cs, ts = run_width(ws)
	ax2.plot(ws, cs, '-o')
	ax2.spines['right'].set_visible(False)
	ax2.spines['top'].set_visible(False)
	for i, num in enumerate(cs):
		ax2.annotate(f'{num:.2e}', (ws[i], cs[i]), xytext=(-10,5), textcoords='offset points')
	ax2.set_xlabel('Width')
	ax2.set_ylabel('Operations')

	# width x time
	ax4.plot(ws, ts, '-o')
	ax4.spines['right'].set_visible(False)
	ax4.spines['top'].set_visible(False)
	for i, num in enumerate(ts):
		ax4.annotate(f'{num:.2e}', (ws[i], ts[i]), xytext=(-10,5), textcoords='offset points')
	ax4.set_xlabel('Width')
	ax4.set_ylabel('Time')

	plt.tight_layout()
	plt.show()

	# TODO
	# make algoritm for making image with given width
	# decide and setup test cases
	# make 4 graphs
		# 2 graphs - with given depth
			# 1 shows time v depth, other 1 - operations v depth
 		# 2 graphs - with given width
			# 1 shows time v width, other 1 - operations v width