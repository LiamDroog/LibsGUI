"""
##################################################
Displays images from an image directory and
txt spectra files from a spectra directory side by
side for use within LIBS experiments
##################################################
# Author:   Liam Droog
# Email:    droog@ualberta.ca
# Year:     2021
# Version:  V.1.0.0
##################################################
"""
import tkinter as tk
from tkinter import font, ttk
import os
from PIL import ImageTk, Image
import matplotlib.pyplot as plt
import numpy as np
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class imageViewer:
    def __init__(self, image_target_dir, spectra_target_dir, file_extension, master=None):
        # self.window = tk.Tk(className='\Image Viewer')
        self.num_of_images = 5
        self.iter = 1
        # instatiate master window
        # below is all gui setup
        self.window = tk.Toplevel(master=master)
        self.window.title('LibsGUI')
        self.window.resizable(False, False)
        self.canvasframe = tk.Frame(master=self.window)
        self.canvas = tk.Canvas(master=self.canvasframe, width=1250, height=810)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.update_time_label = tk.Label(master=self.window, text='LibsGUI v1.0.1')

        # breaks .grid layout. WTF
        # self.canvas.bind('<Configure>', self.resize_canvas)

        self.scrollbar = ttk.Scrollbar(master=self.window, orient='vertical', command=self.canvas.yview)
        self.scrollFrame = ttk.Frame(master=self.canvas)
        self.scrollFrame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas.create_window((0, 0), window=self.scrollFrame, anchor='nw')
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # initialize lists to store entities later on so that we are nice to the RAM
        self.list_of_rtnframe = []
        self.list_of_imgframe = []
        self.list_of_specframe = []
        self.list_of_sample_header = []
        self.list_of_sample_images_label = []
        self.list_of_spectra_headers = []
        self.list_of_spectra_figures = []
        self.list_of_spectra_plots = []
        self.list_of_spectra_plot_ax = []
        self.list_of_spectra_plot_lineplot = []
        self.list_of_spectra_plot_ax_line = []

        # stuff for the image frames
        font = tk.font.Font(family='Helvetica', size=16, weight='bold')
        # plt.ion()
        for i in range(self.num_of_images):
            # frames
            self.list_of_rtnframe.append(tk.Frame(master=self.scrollFrame, borderwidth=3, relief='groove'))
            self.list_of_imgframe.append(tk.Frame(master=self.list_of_rtnframe[i]))
            self.list_of_specframe.append(tk.Frame(master=self.list_of_rtnframe[i]))
            self.list_of_sample_header.append(tk.Label(master=self.list_of_imgframe[i], font=font))
            self.list_of_sample_images_label.append(tk.Label(master=self.list_of_imgframe[i]))
            self.list_of_spectra_headers.append(tk.Label(master=self.list_of_specframe[i], font=font))
            self.list_of_spectra_plots.append(plt.Figure(figsize=(8, 4), dpi=100))
            self.list_of_spectra_plot_ax.append(self.list_of_spectra_plots[i].add_subplot(111))
            self.list_of_spectra_plot_lineplot.append(
                FigureCanvasTkAgg(self.list_of_spectra_plots[i], self.list_of_specframe[i]))

        # initialize plots so that we can update them later
        for i in range(self.num_of_images):
            self.list_of_spectra_plot_ax_line.append(self.list_of_spectra_plot_ax[i].plot(0, 0, linewidth=0.65))
        # grid ALL the things!
        for i in range(self.num_of_images):
            self.list_of_spectra_headers[i].grid(row=1, column=0, columnspan=2)
            self.list_of_sample_header[i].grid(row=0, column=0, columnspan=2)
            self.list_of_sample_images_label[i].grid(row=1, column=0, columnspan=2)

            # not sure about below. seems to work?
            self.list_of_imgframe[i].grid(row=0, column=1)
            self.list_of_specframe[i].grid(row=0, column=0)
            self.list_of_rtnframe[i].grid(row=i, column=0)

        self.canvasframe.grid(row=1, column=0, sticky='nsew')
        self.canvas.grid(row=0, column=0, sticky='nesw')
        self.scrollbar.grid(row=1, column=1, sticky='nse')
        self.update_time_label.grid(row=0, column=0, sticky='ew')

        # Transfer imputs to class variables
        self.image_target_dir = image_target_dir
        self.spectra_target_dir = spectra_target_dir
        self.most_recent_spectra = None
        self.most_recent_image = None
        self.file_ext = file_extension
        self.current_display = None
        self.img_dir_list = []
        self.spectra_dir_list = []
        self.iter = 0

        # kickstart directory polling
        self.pollDirectory()
        # run self.onClosing when we close the window to ensure proper cleanup
        self.window.protocol('WM_DELETE_WINDOW', self.onClosing)
        # L O O P
        self.window.mainloop()

    def resize_canvas(self, event):
        w, h = event.width - 100, event.height - 100
        self.canvas.config(width=w, height=h)

    def pollDirectory(self):
        """
        Polls target directories and pulls lists of files to pass to update_image
        :return: None
        """
        # Make sure cwd is the same as the target wd
        if not os.getcwd() == self.image_target_dir:
            os.chdir(self.image_target_dir)
        try:
            # get a lits of all files in image_directory
            self.img_dir_list = sorted(filter(os.path.isfile, os.listdir('.')), key=os.path.getmtime)
            # set current top image to the most recently modified file in the image_directory
            if not self.current_display or self.current_display != self.img_dir_list[-1]:
                self.current_display = self.img_dir_list[-1]
            # change dir to spectra dir and get a list of present files
            os.chdir(self.spectra_target_dir)
            self.spectra_dir_list = sorted(filter(os.path.isfile, os.listdir('.')), key=os.path.getmtime)

            # update images for your viewing pleasure
            self.update_image(self.img_dir_list, self.spectra_dir_list)

        except Exception as e:
            print(e)
        finally:
            # ensure that running polldirectory takes <1000ms before changing!
            self.update_time_label.config(text='LibsGUI v1.0.1 \nLast update time: ' + str(time.strftime("%H:%M:%S", time.localtime())))
            self.window.after(1000, self.pollDirectory)

    def _on_mousewheel(self, event):
        """
        Scrolls the window when you use the scrollwheel
        :param event: Event?
        :return:
        """
        # scroll on command
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def update_image(self, img_dir_list, spectra_dir_list):
        """
        Updates screen with specified number of images in init, side by side with
        their corresponding spectra.
        :param: img_dir_list: List of files present in the image directory. Does not
                include full file path
        :param: spectra_dir_list: List of files present in the spectra directory.
                Does not include full file path
        :return:
        """

        # get 5 most recent files and reverse list so that the most recent is index 0
        self.img_dir_list = img_dir_list[-self.num_of_images:]
        self.img_dir_list.reverse()
        self.spectra_dir_list = spectra_dir_list[-self.num_of_images:]
        self.spectra_dir_list.reverse()

        if self.most_recent_spectra == self.spectra_dir_list[0] and self.most_recent_image == self.img_dir_list[0]:
            return
        else:
            self.most_recent_image = self.img_dir_list[0]
            self.most_recent_spectra = self.spectra_dir_list[0]

        for j, i in enumerate(self.img_dir_list):
            # change dir to image dir
            os.chdir(self.image_target_dir)
            # set title of frame to file name
            self.list_of_sample_header[j].config(text=i.split('\\')[-1])

            # open and scale image, then insert into label
            self.sample_image = Image.open(i)
            factor = 0.35
            self.sample_image = self.sample_image.resize(
                (int(self.sample_image.size[0] * factor), int(self.sample_image.size[1] * factor)),
                Image.ANTIALIAS)
            self.sample_tkimage = ImageTk.PhotoImage(self.sample_image)

            self.list_of_sample_images_label[j].config(image=self.sample_tkimage)
            self.list_of_sample_images_label[j].image = self.sample_tkimage

            # Change dir to spectra dir
            os.chdir(self.spectra_target_dir)
            # yeet old plot
            self.list_of_spectra_plot_ax[j].clear()
            # set title of the plot to file name
            self.list_of_spectra_headers[j].config(text=self.spectra_dir_list[j].split('\\')[-1])
            # pull data from target file
            dat = np.loadtxt(self.spectra_dir_list[j], dtype=float, delimiter=';')
            # plot
            self.list_of_spectra_plot_ax[j].plot(dat[:, 0], dat[:, 1], linewidth=0.65)
            # Set plot-oriented stuff
            self.list_of_spectra_plot_ax[j].set_xlim([200, 1000])
            self.list_of_spectra_plot_ax[j].set_ylim([0, 1])
            self.list_of_spectra_plot_ax[j].set_xlabel('Wavelength(nm)')
            self.list_of_spectra_plot_ax[j].set_ylabel('Intensity')
            self.list_of_spectra_plot_ax[j].set_title(self.spectra_dir_list[j].split('\\')[-1])
            self.list_of_spectra_plots[j].canvas.draw()
            # actually display the graph
            self.list_of_spectra_plot_lineplot[j].get_tk_widget().grid(row=1, column=0, columnspan=2)
            # garbage collection?
            del dat
        self.iter += 1

    def onClosing(self):
        """
        Allows closing of windows to be cleaner versus tkinter's build in methods
        :return: None
        """
        self.window.destroy()


if __name__ == '__main__':
    # imageViewer('C:\\Users\\Liam Droog\\Desktop\\controlTest\\Images', 'bmp')
    pass
