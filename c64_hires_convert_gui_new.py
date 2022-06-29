# edited on HP 6/23/2022
""" converts an image file to Commodore 64 Doodle! hi-res 320x200 black & white format"""

# TODO: separate doodle formatter into another thread
# TODO: timer to see how quickly the Doodle conversion happens
# TODO: checkbox to stretch image to full width
# TODO: fix save filename, max 16 chars, lowercase, remove special chars
# OPTIONAL: save to a .d64 disk
# https://pypi.org/project/d64/
# https://style64.org/cbmdisk/documentation/

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog as fd

from PIL import Image, ImageTk, ImageFilter
import numpy as np

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # label frame for action buttons
        self.action_group = tk.LabelFrame(self, padx=10, pady=10, text=" Action Buttons ")
        self.action_group.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # action buttons
        self.open_button = ttk.Button(self.action_group, text='Open an Image', command=self.selectFile)
        self.open_button.pack(pady=(0, 20))

        self.cnvt_bw_button = ttk.Button(self.action_group, text='Convert to B&W', command=self.convertFileToBW, state=tk.DISABLED)
        self.cnvt_bw_button.pack(pady=(0, 20))

        self.cnvt_doodle_button = ttk.Button(self.action_group, text='Convert to Doodle', command=self.convertFileToDoodle, state=tk.DISABLED)
        self.cnvt_doodle_button.pack()

        # labelframe for display picture
        self.imgprev_group = tk.LabelFrame(self, padx=10, pady=10, text=" Image Preview ")
        self.imgprev_group.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # blank white label to display picture
        self.default_image = Image.new( mode = "L", size = (320, 200), color = (255,) )
        self.def_img = ImageTk.PhotoImage(self.default_image)
        self.disp_lbl = ttk.Label(self.imgprev_group, anchor="nw", image=self.def_img)
        self.disp_lbl.pack()

        # labelframe for event log
        self.log_group = tk.LabelFrame(self, padx=10, pady=10, text=" Event Log ")
        self.log_group.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        # event log with scrollbar
        self.scrollbar = tk.Scrollbar(self.log_group)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)

        self.textlog = tk.Text(self.log_group, yscrollcommand=self.scrollbar.set, height=10)
        self.textlog.pack(side=tk.LEFT)

        self.scrollbar.config(command=self.textlog.yview)

    def selectFile(self):
        self.filetypes = (
            ('image files', '*.jpg *.jpeg *.JPG *.JPEG *.png *.PNG *.gif *.GIF'),
            ('All files', '*.*')
        )

        self.filename = fd.askopenfilename(
            title='Open a file',
            initialdir='/',
            filetypes=self.filetypes
        )

        if not self.filename:
            pass
        else:
            self.textlog.delete('1.0', tk.END) # clear textbox first
            self.textlog.insert(tk.END, "Chosen file: " + self.filename + "\n")
            self.textlog.insert(tk.END, "----------" + "\n")
            self.textlog.see(tk.END)

            self.loadImage(self.filename)

            # make sure B&W convert button is enabled
            self.cnvt_bw_button.config(state=tk.NORMAL)
            # make sure doodle convert button is disabled
            self.cnvt_doodle_button.config(state=tk.DISABLED)


    def loadImage(self, imageToLoad):
        # open image in RGB mode
        self.im = Image.open(imageToLoad)

        # get old image width and height
        old_width = self.im.size[0]
        old_height = self.im.size[1]

        # show some stats about the old image
        self.textlog.insert(tk.END, "Loaded: " + str(imageToLoad) + "\n")
        self.textlog.insert(tk.END, "Old image width: " + str(old_width) + "\n")
        self.textlog.insert(tk.END, "Old image height: " + str(old_height) + "\n")
        self.textlog.insert(tk.END, "Old format: " + str(self.im.format) + "\n")
        self.textlog.insert(tk.END, "Old mode: " + str(self.im.mode) + "\n")

        self.textlog.insert(tk.END, "----------" + "\n")

        # rescale the image down to 320 by 200
        # (largest source dimension / largest target dimension) * smallest source dimension = new smallest target
        new_width = 320
        new_height = 200
        hpercent = ( new_height / float(old_height) )
        wsize = int( (float(old_width) * float(hpercent)) )
        self.ph_new = self.im.resize((wsize, new_height), resample=Image.Resampling.BICUBIC)
        self.ph = ImageTk.PhotoImage(self.ph_new) # turn into PhotoImage before display in a label!

        # show new size stats about the old image
        self.textlog.insert(tk.END, "New image width: " + str( self.ph_new.size[0] ) + "\n" )
        self.textlog.insert(tk.END, "New image height: " + str( self.ph_new.size[1] ) + "\n" )
        self.textlog.insert(tk.END, "----------" + "\n")
        self.textlog.see(tk.END)

        # update the label to display the PhotoImage
        self.disp_lbl.config(image=self.ph)
        self.disp_lbl.image = self.ph

    def convertFileToBW(self):
        # get resized image from label
        self.im1_new = ImageTk.getimage(self.disp_lbl.image)

        # convert to B&W with dithering (mode 1)
        self.im1_bw = self.im1_new.convert("1") # option no dithering: dither=Image.NONE
        new_bg_image = self.default_image.convert("1")

        # show some stats about the new image
        self.textlog.insert(tk.END, "New format: " + str(self.im1_bw.format) + "\n" )
        self.textlog.insert(tk.END, "New mode: " + str(self.im1_bw.mode) + "\n" )

        self.textlog.insert(tk.END, "----------" + "\n")
        self.textlog.see(tk.END)

        # merge image with background if new image width is smaller than 320
        if self.im1_bw.size[0] < 320:
            paste_coord = (320 - self.im1_bw.size[0])/2
            x_paste_coord = int(paste_coord)
            new_bg_image.paste(self.im1_bw, (x_paste_coord,0))
        else:
            new_bg_image.paste(self.im1_bw, (0,0))

        # turn into PhotoImage before display in a label!
        self.photoimg = ImageTk.PhotoImage(new_bg_image)

        # update the label to display the image
        self.disp_lbl.config(image=self.photoimg)
        self.disp_lbl.image = self.photoimg

        # save the temp image
        new_bg_image.save("bwtemp.png")

        # enable doodle convert button
        self.cnvt_doodle_button.config(state=tk.NORMAL)

    def getHex(self, list_to_process):
        # from a list of 8 elements (each element a 1 or 0) as a byte, turn into hex format
        power = 7
        new_hex = 0
        for x in np.nditer(list_to_process):
            new_hex = new_hex + ( int(x) * (2**power) ) # change from binary to decimal
            power = power - 1
        new_hex = hex(new_hex)
        new_hex = new_hex[2:]
        new_hex = new_hex.zfill(2)
        return new_hex

    def convertFileToDoodle(self):
        self.config(cursor="clock")

        self.textlog.insert(tk.END, "Converting to Doodle..." + "\n")
        self.textlog.see(tk.END)

        # get resized image from label
        self.im2_new = ImageTk.getimage(self.disp_lbl.image)
        self.im2_new = self.im2_new.convert("1")

        # convert image data to 2D array (lists of boolean values)
        image_array = np.array(self.im2_new).astype(int) # 2D image array is 200 lines, 320 pixel elements across

        # get info about the new array
        self.textlog.insert(tk.END, "Number of lines: " + str(len(image_array)) + "\n" ) # number of lines
        self.textlog.insert(tk.END, "Number of array dimensions: " + str(image_array.ndim) + "\n" )  # number of dimensions
        self.textlog.insert(tk.END, "Nunber of elements in a line: " + str(len(image_array[0])) + "\n" ) # number of elements in a line
        self.textlog.insert(tk.END, str(image_array.shape) + "\n") # 200 lines (arrays) with 320 elements in each line (array)
        self.textlog.see(tk.END)

        # byte array to hold converted Doodle image data
        byte_arr = bytearray()

        # write the C64 file load address first
        byte_arr += bytearray(b'\x00\x5c') # begin file with load address $5C00 (as low byte/high byte) 23552 in decimal

        # C64 doodle - first 1000 bytes is color info (each 8x8 screen chunk) + 24 + 2
        while len(byte_arr) < 1026:
            byte_arr += bytearray(b'\x10') # fill 1000 bytes color memory with white bg and black fg colors

        # slice image array into 8x8 character blocks (C64 screen = 40 blocks across, 25 blocks down)
        # from lines 0 thru 7, get first 8 elements of each line
        block_count = 0
        line_count = 0
        xmin = 0
        xmax = 8
        ymin = 0
        ymax = 8
        while block_count < 40:
            self.textlog.insert(tk.END, "Block count: " + str(block_count) + " -- xmin: " + str(xmin) + " -- xmax: " + str(xmax) + "\n" )
            self.textlog.see(tk.END)
            #print(image_array[ymin:ymax, xmin:xmax])
            # process each line of the block into hex
            for line_item in image_array[ymin:ymax, xmin:xmax]:
                hex_line = self.getHex(line_item)
                byte_arr += bytearray.fromhex(hex_line)
            #print(image_array[ymin:ymax, xmin:xmax].shape)
            xmin = xmin + 8
            xmax = xmax + 8
            block_count = block_count + 1
            if block_count == 40:
                line_count = line_count + 1
                self.textlog.insert(tk.END, "Line count: " + str(line_count) + " -- ymin: " + str(ymin) + " -- ymax: " + str(ymax) + "\n" )
                self.textlog.see(tk.END)
                if line_count < 25:
                    block_count = 0
                    xmin = 0
                    xmax = 8
                    ymin = ymin + 8
                    ymax = ymax + 8

        self.textlog.insert(tk.END, "Saving C64 Doodle file..." + "\n")
        self.textlog.see(tk.END)

        # Write bytes to file
        with open("ddtest", "wb") as binary_file:
            binary_file.write(byte_arr)

        self.textlog.insert(tk.END, "DONE!!!!!" + "\n")
        self.textlog.see(tk.END)

        self.config(cursor="")

if __name__ == "__main__":
    app = App()
    app.title('C64 Doodle HiRes Converter')
    app.geometry("+100+100")
    app.resizable(False, False)
    app.iconphoto(False, tk.PhotoImage(file='c64icon.png')) # icon size 32x32px
    app.mainloop()
