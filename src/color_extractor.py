########################################################
# ---------------- github.com/duruburak ----------------#
########################################################
import os
import tkinter as tk

import customtkinter
import numpy as np
import pyperclip
from PIL import ExifTags, Image


customtkinter.deactivate_automatic_dpi_awareness()

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.toplevel_window: customtkinter.CTkToplevel = None

        self.var_color_type: customtkinter.StringVar = customtkinter.StringVar(
            value=" HEX")
        self.var_background_color: customtkinter.StringVar = customtkinter.StringVar(
            value="color_dark")
        self.is_process_over: customtkinter.BooleanVar = customtkinter.BooleanVar(
            value=False)

        self.toplevel_progressbar : customtkinter.CTkProgressBar = None

        self.open_image = None
        self.target_image: Image.Image = None
        self.target_image_transparent: Image.Image = None
        self.target_image_ctk: customtkinter.CTkImage = None

        self.file_extension: str = ""
        self.target_image_size: tuple = None
        self.target_image_aspect_ratio_1: float = 1.0
        self.target_image_aspect_ratio_2: float = 1.0
        self.target_image_ar_type: int = None

        self.pixels: np.ndarray = None
        self.target_image_array: np.ndarray = None
        self.color_counts: dict = {}
        self.sorted_15_colors_and_counts: list = []
        self.top_15_colors: np.ndarray = None

        self.list_of_result_buttons: list = []
        self.list_of_top_15_colors_rgb: list = []
        self.list_of_top_15_colors_hex: list = []

        self.dict_result_widgets: dict = {}

        self.minsize(700, 650)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.title("Color Extractor")

        self.btns_container_frame = customtkinter.CTkFrame(
            self, fg_color="gray14")
        self.btns_container_frame.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_upload_image = customtkinter.CTkButton(self.btns_container_frame, width=120,
                                                        corner_radius=15, text="Upload an Image",
                                                        text_color="#00F5FF",
                                                        font=(
                                                            "Century Gothic", 15, "bold"),
                                                        fg_color="#CD104D",
                                                        hover_color="#FC2947",
                                                        command=self.upload_image)

        self.btn_upload_image.grid(row=0, column=0, padx=10, pady=0)

        self.switch_color_type = customtkinter.CTkSwitch(self.btns_container_frame, text=" HEX",
                                                         text_color="#A4EBF3",
                                                         font=(
                                                             "Century Gothic", 16, "normal"),
                                                         variable=self.var_color_type,
                                                         onvalue=" RGB", offvalue=" HEX",
                                                         fg_color="#BE9FE1",
                                                         progress_color="#E84545",
                                                         button_color="#CD104D",
                                                         button_hover_color="#850E35",
                                                         command=self.toggle_color)

        self.switch_color_type.toggle()
        self.switch_color_type.grid(row=0, column=1, padx=10, pady=0)

        self.target_and_result_image_container = customtkinter.CTkFrame(
            self, fg_color="#433D3C")
        self.target_and_result_image_container.grid(
            row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.target_and_result_image_container.grid_columnconfigure(
            (0, 1), weight=1)
        self.target_and_result_image_container.grid_rowconfigure(1, weight=1)

        self.switch_toggle_background_color = customtkinter.CTkSwitch(
            self.target_and_result_image_container,
            text="Toggle Background Color",
            text_color="#FDCEDF",
            font=("Bauhaus 93", 17, "normal"),
            variable=self.var_background_color,
            onvalue="color_light", offvalue="color_dark",
            fg_color="#DB005B", progress_color="#99627A",
            button_color="#A0D8B3",
            button_hover_color="#C88EA7",
            command=self.toggle_background_color)

        self.switch_toggle_background_color.grid(
            row=0, column=0, columnspan=2, padx=(10, 5), pady=10, sticky="ns")

        self.label_target_image = customtkinter.CTkLabel(self.target_and_result_image_container,
                                                         text="", corner_radius=10,
                                                         fg_color="#272121", image=None)
        self.label_target_image.grid(
            row=1, column=0, padx=(10, 5), pady=10, sticky="nsew")

        self.label_result_image = customtkinter.CTkLabel(self.target_and_result_image_container,
                                                         text="", corner_radius=10,
                                                         fg_color="#272121", image=None)
        self.label_result_image.grid(
            row=1, column=1, padx=(5, 10), pady=10, sticky="nsew")
        self.update()

        self.width_label_target_image: int = self.label_target_image.winfo_width()
        self.height_label_target_image: int = self.label_target_image.winfo_height()

        self.results_container_frame = customtkinter.CTkFrame(
            self, fg_color="transparent")
        self.results_container_frame.grid(
            row=2, column=0, padx=20, pady=10, sticky="ew")
        self.results_container_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.results_container_frame.grid_rowconfigure(
            (0, 1, 2, 3, 4), weight=1)

        self.label_number_font = customtkinter.CTkFont("Consolas", 16, "bold")
        self.result_color_font = customtkinter.CTkFont(
            "Arial Rounded MT", 15, "bold")

        for i in range(1, 16):
            frame_name = f"result_{i}_frame"
            label_name = f"label_{i}"
            result_name = f"result_{i}"

            frame = customtkinter.CTkFrame(
                self.results_container_frame, fg_color="transparent")
            frame.grid(row=(i-1)//3, column=(i-1) %
                       3, padx=10, pady=5, sticky="nsew")
            frame.grid_columnconfigure(1, weight=1)
            frame.grid_rowconfigure(0, weight=1)
            self.dict_result_widgets[frame_name] = frame

            label = customtkinter.CTkLabel(frame, text=f"{i}: ", text_color="#A5F1E9",
                                           fg_color="transparent", font=self.label_number_font)
            label.grid(row=0, column=0, padx=(10, 2), pady=5, sticky="ns")
            self.dict_result_widgets[label_name] = label

            result = customtkinter.CTkButton(frame, text="——", font=self.result_color_font,
                                             fg_color="transparent", corner_radius=6,
                                             hover_color="#967E76",
                                             command=lambda i=i: self.copy_color_onclick(self.dict_result_widgets[f"result_{i}"]))
            result.grid(row=0, column=1, padx=(2, 10), pady=5, sticky="nsew")
            self.dict_result_widgets[result_name] = result

    def reset_image(self):

        self.label_result_image.configure(image=None)
        self.label_target_image.configure(image=None)

        self.is_process_over.set(False)

        self.update_idletasks()

        self.list_of_result_buttons.clear()

        self.open_image = None
        self.target_image = None
        self.target_image_transparent = None

        self.pixels = None
        self.target_image_array = None
        self.color_counts.clear()
        self.sorted_15_colors_and_counts.clear()
        self.top_15_colors = None

        self.list_of_top_15_colors_rgb.clear()
        self.list_of_top_15_colors_hex.clear()

    def loading_window(self):

        self.toplevel_window = customtkinter.CTkToplevel(self)
        self.toplevel_window.title("Analyzing the image...")
        screen_width = self.toplevel_window.winfo_screenwidth()
        screen_height = self.toplevel_window.winfo_screenheight()
        x_coordinate = int((screen_width/2)-(500/2))
        y_coordinate = int((screen_height/2)-(300/2))
        self.toplevel_window.geometry(f"500x300+{x_coordinate}+{y_coordinate}")
        self.toplevel_window.overrideredirect(1)

        frame = customtkinter.CTkFrame(self.toplevel_window,
                                       fg_color="gray14", bg_color="gray14")
        frame.place(x=140, y=130)

        label1 = customtkinter.CTkLabel(frame, text='Please wait',
                                        fg_color="gray14", bg_color="gray14",
                                        font=("Game Of Squids", 21, "bold"))
        label1.pack(padx=10, pady=5)

        self.toplevel_progressbar = customtkinter.CTkProgressBar(frame, width=100,
                                                                 height=13, indeterminate_speed=2,
                                                                 mode="indeterminate", progress_color="#B71375")
        self.toplevel_progressbar.start()
        self.toplevel_progressbar.pack(padx=(10, 15), pady=10)

        label2 = customtkinter.CTkLabel(self.toplevel_window, text='Analyzing the image...',
                                        fg_color="gray14", bg_color="gray14", font=("Helvetica", 11))
        label2.place(x=10, y=270)

        def update_splash_screen():
            if self.is_process_over.get():
                self.toplevel_window.destroy()
                return
            self.after(100, update_splash_screen)

        if self.is_process_over.get():
            self.toplevel_window.destroy()
            return

        self.after(100, update_splash_screen)
        self.toplevel_window.grab_set()

    def toggle_color(self):

        current_color_type = self.var_color_type.get()
        self.switch_color_type.configure(text=current_color_type)

        try:
            if current_color_type == " RGB":
                for i in range(1, 16):
                    widget_name = f"result_{i}"
                    self.dict_result_widgets[widget_name].configure(
                        text=str(self.list_of_top_15_colors_rgb[i-1]))
            else:
                for i in range(1, 16):
                    widget_name = f"result_{i}"
                    self.dict_result_widgets[widget_name].configure(
                        text=self.list_of_top_15_colors_hex[i-1])

        except (KeyError, IndexError, AttributeError):
            pass

        self.update_idletasks()

    def toggle_background_color(self):

        current_value = self.var_background_color.get()

        if current_value == "color_dark":
            self.label_target_image.configure(fg_color="#272121")
            self.label_result_image.configure(fg_color="#272121")

        else:
            self.label_target_image.configure(fg_color="#F9FBE7")
            self.label_result_image.configure(fg_color="#F9FBE7")

        self.update_idletasks()

    def upload_image(self):

        filetypes = (
            ('Image', '*.png *.PNG *.jpg *.JPG *.jpeg *.JPEG *.gif *.GIF *.ppm *.PPM *.tiff *.TIFF *.bmp *.BMP'),
            ('All files', '*.*')
        )

        filepath = tk.filedialog.askopenfilename(
            title='Select an Image',
            filetypes=filetypes
        )

        try:
            self.reset_image()

        except:
            pass

        if filepath == "":
            return

        try:
            self.open_image = Image.open(filepath)
            self.target_image = self.open_image.convert("RGB")
            self.target_image_transparent = self.open_image.convert("RGBA")
            self.loading_window()

        except Image.UnidentifiedImageError:
            self.open_image.close()
            return

        try:
            exif = dict(self.target_image.getexif().items())
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
                if exif[orientation] == 3:
                    self.target_image = self.target_image.transpose(
                        Image.ROTATE_180)
                elif exif[orientation] == 6:
                    self.target_image = self.target_image.transpose(
                        Image.ROTATE_270)
                elif exif[orientation] == 8:
                    self.target_image = self.target_image.transpose(
                        Image.ROTATE_90)

        except (AttributeError, KeyError, IndexError):
            # If the image has no orientation metadata, do nothing
            pass

        self.file_extension = os.path.splitext(filepath)[1]

        self.target_image_size = self.target_image.size

        self.target_image_aspect_ratio_1 = round(
            self.target_image.size[0] / self.target_image.size[1], 3)
        self.target_image_aspect_ratio_2 = round(
            self.target_image.size[1] / self.target_image.size[0], 3)

        if self.target_image_aspect_ratio_1 < 1:
            self.target_image_ar_type = 1
            self.target_image_size = (
                self.target_image_size[0] * self.height_label_target_image / self.target_image_size[1], self.height_label_target_image)

        else:
            self.target_image_ar_type = 2
            self.target_image_size = (self.width_label_target_image, self.width_label_target_image *
                                      self.target_image_size[1] / self.target_image_size[0])

        self.target_image_ctk = customtkinter.CTkImage(light_image=self.target_image_transparent,
                                                       dark_image=self.target_image_transparent,
                                                       size=self.target_image_size) if self.file_extension in (".PNG", ".png") \
            else customtkinter.CTkImage(light_image=self.target_image,
                                        dark_image=self.target_image,
                                        size=self.target_image_size)

        self.label_target_image.configure(image=self.target_image_ctk)

        self.color_processing()
        self.open_image.close()

    def color_processing(self):

        # Flatten the array to a list of RGB tuples (Array of all self.pixels)
        if self.file_extension in (".PNG", ".png"):
            self.target_image_array = np.array(self.target_image_transparent)
            self.pixels = self.target_image_array.reshape(-1, 4)
            self.get_top_15_colors_png()
        else:
            self.target_image_array = np.array(self.target_image)
            self.pixels = self.target_image_array.reshape(-1, 3)
            self.get_top_15_colors()

        self.remove_non_top_color_pixels()
        self.declare_results()
        self.bell()

    def get_top_15_colors_png(self):
        # Count the occurrence of each RGB tuple
        for pixel in self.pixels:

            pixel = tuple(pixel)
            if pixel[-1] == 0:
                continue

            if pixel in self.color_counts:
                self.color_counts[pixel] += 1
            else:
                self.color_counts[pixel] = 1

            self.toplevel_progressbar.update()

        # Sort the colors by their count in descending order
        self.sorted_15_colors_and_counts = sorted(
            self.color_counts.items(), key=lambda x: x[1], reverse=True)[:15]

        # Extract the top 15 colors
        self.top_15_colors = np.array(
            [color[0] for color in self.sorted_15_colors_and_counts])

        # Assign them in lists
        for color in self.top_15_colors:
            color_as_tuple = tuple(color)
            self.list_of_top_15_colors_rgb.append(color_as_tuple)
            self.list_of_top_15_colors_hex.append(
                self.rgb_to_hex(color_as_tuple))

    def get_top_15_colors(self):
        # Count the occurrence of each RGB tuple
        for pixel in self.pixels:

            pixel = tuple(pixel)

            if pixel in self.color_counts:
                self.color_counts[pixel] += 1
            else:
                self.color_counts[pixel] = 1

            self.toplevel_progressbar.update()

        # Sort the colors by their count in descending order
        self.sorted_15_colors_and_counts = sorted(
            self.color_counts.items(), key=lambda x: x[1], reverse=True)[:15]

        # Extract the top 6 colors
        self.top_15_colors = np.array(
            [color[0] for color in self.sorted_15_colors_and_counts])

        # Assign them in lists
        for color in self.top_15_colors:
            color_as_tuple = tuple(color)
            self.list_of_top_15_colors_rgb.append(color_as_tuple)
            self.list_of_top_15_colors_hex.append(
                self.rgb_to_hex(color_as_tuple))

    def remove_non_top_color_pixels(self):

        na = self.target_image_array.copy()
        na_transparent = np.array(self.target_image_transparent)

        masks = np.zeros_like(na[..., 0], dtype=bool)

        for color in self.top_15_colors:
            masks |= np.all(na == color, axis=-1)

        na_transparent[~masks] = (0, 0, 0, 0)

        modified_img = Image.fromarray(na_transparent)
        modified_img_ctk = customtkinter.CTkImage(
            light_image=modified_img, dark_image=modified_img, size=self.target_image_size)

        self.label_result_image.configure(image=modified_img_ctk)

        self.update()

    def declare_results(self):

        current_color_type = self.var_color_type.get()
        self.list_of_result_buttons: list = [
            self.dict_result_widgets[f"result_{i}"] for i in range(1, 16)]

        how_many_colors_found = len(self.list_of_top_15_colors_rgb)

        if current_color_type == " RGB":
            for i in range(15):
                if i < how_many_colors_found:
                    self.list_of_result_buttons[i].configure(
                    text=str(self.list_of_top_15_colors_rgb[i]), fg_color=self.list_of_top_15_colors_hex[i])
                else:
                    self.list_of_result_buttons[i].configure(
                    text="——", fg_color="transparent")

        else:
            for i in range(15):
                if i < how_many_colors_found:
                    self.list_of_result_buttons[i].configure(
                    text=self.list_of_top_15_colors_hex[i], fg_color=self.list_of_top_15_colors_hex[i])
                else:
                    self.list_of_result_buttons[i].configure(
                     text="——", fg_color="transparent")

        self.is_process_over.set(True)
        self.update_idletasks()

    def rgb_to_hex(self, rgb) -> str:
        """
        Convert an RGB color value to a hexadecimal color code.
        Input: RGB tuple (r, g, b), where r, g, b are integers between 0 and 255
        Output: Hexadecimal color code string in the format "#RRGGBB"
        """
        try:
            r, g, b = rgb
            return f"#{r:02x}{g:02x}{b:02x}"

        except:
            r, g, b, a = rgb

            hex_r = format(int(r), '02x')
            hex_g = format(int(g), '02x')
            hex_b = format(int(b), '02x')
            hex_a = format(int(a * 255), '02x')

            hex_value = '#' + hex_r + hex_g + hex_b + hex_a
            return hex_value[:7]

    def copy_color_onclick(self, widget):

        pyperclip.copy(widget.cget("text"))


if __name__ == "__main__":
    app = App()
    app.mainloop()
