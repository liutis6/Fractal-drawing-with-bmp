class BMP:
	def __init__(self, height, width):
		self.height = height
		self.width = width
		self.x = 0
		self.y = 0
		self.line_len = 0

		self.bmp_header = bytearray([
		0x42, 0x4D, # 'B', 'M' - bmp file signature
		0, 0, 0, 0, # file size (dynamic)
		0, 0, 0, 0, # reserved (mean nothing)
		54, 0, 0, 0 # at what byte does the image start
		])

		width_b = width.to_bytes(4, 'little')
		height_b = height.to_bytes(4, 'little')

		self.dib_header = bytearray([ 
			40, 0, 0, 0, # size of this header (constant 40 for BITMAPINFOHEADER)
			width_b[0], width_b[1], width_b[2], width_b[3], # image width
			height_b[0], height_b[1], height_b[2], height_b[3], # image height
			1, 0, # Planes (must be one)
			24, 0, # bits per pixel
			0, 0, 0, 0, # compression (none)
			0, 0, 0, 0, # image size (can be 0 for uncrompressed)
			0, 0, 0, 0, # x pixels per meter (not used)?
			0, 0, 0, 0, # y pixels per meter (not used)?
			0, 0, 0, 0, # Total colors (0=default)?
			0, 0, 0, 0  # Important colors (0=all)?
		])

		# bmp requires that each row of pixel data (width x bytes per pixel)
		# must have a total size that is divisible by 4.
		# if it is not, extra padding bytes (0x00) must be added at the end of each row
		self.row_padding = (4-((width*3)%4))%4
			# width*3 - each pixel is 3 bytes, thus a row has width*3 bytes
			# (width*3 % 4) - finds remainder
			# 4-(width*3 % 4) - how many bytes are needed as filler in each row
			# 4-(width*3 % 4) %4 - in case no padding is needed
			
		self.row_size = width*3 + self.row_padding

		image_size = height * self.row_size # height amount of rows
		file_size = 54 + image_size # sum of BMP(14 bytes) and DIB (40 bytes) headers
		self.bmp_header[2:6] = file_size.to_bytes(4, 'little') # converts file_size into a 4-byte little-endian representation
			# 4 byte little endian meaning that when the number is converted into hex form (0x00000000),
			# it is divided into 4 pairs and then arranged in the array in such a way that the LSB is added first and MSB is added last.
			# *'big'(-endian) - MSB first, LSB last*

		# generate blue bmp sheet of pixels
		self.pixel_data = bytearray()
		for y in range(height): # for every row
			for x in range(width): # for every column
				self.pixel_data += bytearray([255, 0, 0]) # add blue pixel (BGR) at every coordinate
			self.pixel_data += b'\x00' * self.row_padding # ficticious bytes to fill meet padding requirement
		
	# change one pixel
	def set_pixel(self, x, y, color):
		if 0 <= x < self.width and 0 <= y < self.height:
			index = (self.height - 1 - y) * self.row_size + x * 3
			self.pixel_data[index:index+3] = bytearray(color)

	# draw vertical line
	def vertical_line(self, x, y1, y2):
		for y in (range(y1, y2) if y1 < y2 else range(y2, y1)):
			pixel_offset = (y * self.row_size + # skip over traversed rows
							+ x*3) # starting byte index in column
			self.pixel_data[pixel_offset:pixel_offset+3] = bytearray([0, 0, 255])

	# draw horizontal line
	def horizontal_line(self, y, x1, x2):
		pixel_offset = (y * self.row_size)
		for x in (range(x1, x2) if x1 < x2 else range(x2, x1)):
			self.pixel_data[pixel_offset+x*3:pixel_offset+x*3+3] = bytearray([0, 0, 255])

	# draw diagonal line
	def diagonal_line(self, x_start):
		if(x_start>=0):
			x = x_start
			for y in range(self.height-x_start):
				pixel_offset = (y*self.row_size + x*3)
				self.pixel_data[pixel_offset:pixel_offset+3] = bytearray([0, 0, 255])
				x+=1
		else:
			x = 0
			for y in range(abs(x_start), self.height): # first pixel will be at y=abs(x), stop when it reaches the top
				pixel_offset = (y*self.row_size + x*3)
				self.pixel_data[pixel_offset:pixel_offset+3] = bytearray([0, 0, 255])
				x+=1
	
	# i - section in the fractal
	def rec_minkowski(self, n, type):
		if (n<=0):
			if(type=='left'):
				self.horizontal_line(self.y, self.x, self.x-self.line_len)
				self.x = self.x - self.line_len
			elif(type=='right'):
				self.horizontal_line(self.y, self.x, self.x+self.line_len)
				self.x = self.x + self.line_len
			elif(type=='down'):
				self.vertical_line(self.x, self.y, self.y-self.line_len)
				self.y = self.y - self.line_len
			elif(type=='up'):
				self.vertical_line(self.x, self.y, self.y+self.line_len)
				self.y = self.y + self.line_len
		else:
			if(type=='right'):
				self.rec_minkowski(n-1, 'right')
				self.rec_minkowski(n-1, 'up')
				self.rec_minkowski(n-1, 'right')
				self.rec_minkowski(n-1, 'down')
				self.rec_minkowski(n-1, 'down')
				self.rec_minkowski(n-1, 'right')
				self.rec_minkowski(n-1, 'up')
				self.rec_minkowski(n-1, 'right')
			elif (type=='up'):
				self.rec_minkowski(n-1, 'up')
				self.rec_minkowski(n-1, 'left')
				self.rec_minkowski(n-1, 'up')
				self.rec_minkowski(n-1, 'right')
				self.rec_minkowski(n-1, 'right')
				self.rec_minkowski(n-1, 'up')
				self.rec_minkowski(n-1, 'left')
				self.rec_minkowski(n-1, 'up')
			elif (type=='down'):
				self.rec_minkowski(n-1, 'down')
				self.rec_minkowski(n-1, 'right')
				self.rec_minkowski(n-1, 'down')
				self.rec_minkowski(n-1, 'left')
				self.rec_minkowski(n-1, 'left')
				self.rec_minkowski(n-1, 'down')
				self.rec_minkowski(n-1, 'right')
				self.rec_minkowski(n-1, 'down')
	
	def draw_minkowski(self, x, y, depth, line_len=3):
		self.line_len = line_len
		self.x = x
		self.y = y
		self.rec_minkowski(depth, 'right')

	def generate_image(self, f_name):
		with open(f_name, "wb") as file: # wb - write in binary mode
			file.write(self.bmp_header) 
			file.write(self.dib_header)
			file.write(self.pixel_data)
		print("BMP file created")

if __name__ == '__main__':
	image = BMP(3000, 8000)
	image.draw_minkowski(30, 1000, 5, 5)  # Starting point and size
	image.generate_image("output.bmp")