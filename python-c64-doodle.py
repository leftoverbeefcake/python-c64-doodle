from PIL import Image, ImageFilter
import numpy as np

# edited on Mac - 11/24/2021 5:07pm
# https://www.geeksforgeeks.org/python-pillow-tutorial/
# http://www.legendu.net/misc/blog/python-pillow-image-convert/

# open image in RGB mode
im = Image.open(r'my-test-image.jpg')

# show some stats about the old image
print( "old size: " + str(im.size) )
print( "old format: " + str(im.format) )
print( "old mode: " + str(im.mode) )

print("----------")

# resize the image down to 320 by 200
newsize = (320, 200)
im1 = im.resize(newsize, resample=Image.BILINEAR)

# convert to B&W with dithering (mode 1)
im1 = im1.convert("1") # option no dithering: dither=Image.NONE

# show some stats about the new image
print("new size: " + str(im1.size) )
print("new format: " + str(im1.format) )
print("new mode: " + str(im1.mode) )

# save the temp image as png, just in case we need to examine/compare it later
im1.save("bwtemp.png")

#convert image data to 2D array (lists of boolean values 0 and 1)
image_array = np.array(im1).astype(int) # 2D image array is 200 lines, 320 pixel elements across

# byte array to hold converted Doodle image data
byte_arr = bytearray()

# write the load address first
byte_arr += bytearray(b'\x00\x5c') # begin file with load address $5C00 (as low byte/high byte) 23552 in decimal

# C64 doodle - first 1000 bytes is color info (each 8x8 screen chunk) + 24 + 2
while len(byte_arr) < 1026:
    byte_arr += bytearray(b'\x10') # fill 1000 bytes color memory with white bg and black fg colors

# change the 2D array into a string containing bits (0/1)
bm_data = ""
for line in image_array:
    for pixel_data in line:
        bm_data += str(pixel_data)

# break string into a list of 8 bit chunks
new_data = [bm_data[start:start+8] for start in range(0, len(bm_data), 8)]

# convert chunk into hex so the data can be reordered into C64 screen format
hex_data = ""
count = 1
for a_byte in new_data:
    decimal_representation = int(a_byte, 2)
    hexadecimal_string = hex(decimal_representation)
    hexadecimal_string = hexadecimal_string[2:]
    hexadecimal_string = hexadecimal_string.zfill(2)
    hex_data += hexadecimal_string

new_hex_data = [hex_data[start:start+2] for start in range(0, len(hex_data), 2)]

print("block data ---------------")

list_of_lists = []
for i in range(1000):
    # In each iteration, add an empty list to the main list
    list_of_lists.append([])

block_num = 0
index = 0
block_count = 0
while block_num < 1000:
    list_of_lists[block_num].append(new_hex_data[index])
    print(str(index) + " " + new_hex_data[index])
    for block_line in new_hex_data:
        if len(list_of_lists[block_num])<8: # each block is 8 lines of 8 hex chars
            index = index + 40
            list_of_lists[block_num].append(new_hex_data[index])
            print(str(index) + " " + new_hex_data[index])

    block_num = block_num + 1
    if block_num < 40:
        index = block_num
    elif block_num >=40 and block_num < 80:
        index = block_num + 280
    elif block_num >=80 and block_num < 120:
        index = block_num + 560
    elif block_num >=120 and block_num < 160:
        index = block_num + 840
    elif block_num >=160 and block_num < 200:
        index = block_num + 1120
    elif block_num >=200 and block_num < 240:
        index = block_num + 1400
    elif block_num >=240 and block_num < 280:
        index = block_num + 1680
    elif block_num >=280 and block_num < 320:
        index = block_num + 1960
    elif block_num >=320 and block_num < 360:
        index = block_num + 2240
    elif block_num >=360 and block_num < 400:
        index = block_num + 2520
    elif block_num >=400 and block_num < 440:
        index = block_num + 2800
    elif block_num >=440 and block_num < 480:
        index = block_num + 3080
    elif block_num >=480 and block_num < 520:
        index = block_num + 3360
    elif block_num >=520 and block_num < 560:
        index = block_num + 3640
    elif block_num >=560 and block_num < 600:
        index = block_num + 3920
    elif block_num >=600 and block_num < 640:
        index = block_num + 4200
    elif block_num >=640 and block_num < 680:
        index = block_num + 4480
    elif block_num >=680 and block_num < 720:
        index = block_num + 4760
    elif block_num >=720 and block_num < 760:
        index = block_num + 5040
    elif block_num >=760 and block_num < 800:
        index = block_num + 5320
    elif block_num >=800 and block_num < 840:
        index = block_num + 5600
    elif block_num >=840 and block_num < 880:
        index = block_num + 5880
    elif block_num >=880 and block_num < 920:
        index = block_num + 6160
    elif block_num >=920 and block_num < 960:
        index = block_num + 6440
    elif block_num >=960 and block_num < 1000:
        index = block_num + 6720

    print("blocknum " + str(block_num))

for a_list in list_of_lists:
    for element in a_list:
        byte_arr += bytearray.fromhex(element)

# Write bytes to file - file name must start with dd so it can load into Doodle!
with open("ddmytestimage", "wb") as binary_file:
    binary_file.write(byte_arr)
