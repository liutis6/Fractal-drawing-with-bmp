width = 100 #columns
height = 100 #rows 

bmp_header = bytearray([
    0x42, 0x4D, # 'B', 'M' - bmp file signature
    0, 0, 0, 0, # file size (dynamic)
    0, 0, 0, 0, # reserved (mean nothing)
    54, 0, 0, 0 # at what byte does the image start
])

dib_header = bytearray([ 
    40, 0, 0, 0, # size of this header (constant 40 for BITMAPINFOHEADER)
    width, 0, 0, 0, # image width
    height, 0, 0, 0, # image height
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
row_padding = ((width*3)%4) %4
    # width*3 - each pixel is 3 bytes, thus a row has width*3 bytes
    # (width*3 % 4) - finds remainder
    # (width*3 % 4) % 4 - how many bytes are needed as filler
row_size = width*3 + row_padding

image_size = height * row_size # height amount of rows
file_size = 54 + image_size # sum of BMP(14 bytes) and DIB (40 bytes) headers
bmp_header[2:6] = file_size.to_bytes(4, 'little') # converts file_size into a 4-byte little-endian representation
    # 4 byte little endian meaning that when the number is converted into hex form (0x00000000),
    # it is divided into 4 pairs and then arranged in the array in such a way that the LSB is added first and MSB is added last.
    # *'big'(-endian) - MSB first, LSB last*

pixel_data = bytearray()
for y in range(height): # for every row
    for x in range(width): # for every column
        pixel_data += bytearray([255, 0, 0]) # add blue pixel (BGR) at every coordinate
    pixel_data += b'\x00' * row_padding # ficticious bytes to fill meet padding requirement

with open("output.bmp", "wb") as file: # wb - write in binary mode
    file.write(bmp_header) 
    file.write(dib_header)
    file.write(pixel_data)

print("BMP file created")