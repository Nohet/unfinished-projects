import json
import tkinter
from random import randint
from tkinter import messagebox, ttk

from PIL import ImageGrab, Image, ImageTk


with open("config.json") as f:
    config = json.load(f)


def on_closing():
    with open("config.json") as s:
        sett = json.load(s)

    if sett["config"]["on_exit"].lower() == "close":
        quit()

    elif sett["config"]["on_exit"].lower() == "minimize":
        root.iconify()

    else:
        tkinter.messagebox.showerror("Error", f"An error occured with '{sett['config']['on_exit']}' on close option.")

        return


def change_settings():
    with open("config.json") as s:
        sett = json.load(s)

    sett["config"]["description"] = desc.get()
    sett["config"]["on_exit"] = selected_option.get()

    with open("config.json", "w") as w:
        json.dump(sett, w, indent=4)

    tkinter.messagebox.showinfo("Success", "Successfully changed settings!")


def remove_image():
    labels_list = image_tab.pack_slaves()
    for label in labels_list:
        if ".!label" in str(label):
            label.destroy()


def get_image_from_clipboard():
    im = ImageGrab.grabclipboard()

    random_number = randint(1, 999999999999)

    try:
        im.save(f"images/{random_number}.png", format="PNG")

    except Exception as e:
        tkinter.messagebox.showerror("Error", e)

        return

    remove_image()

    image1 = Image.open(f"images/{random_number}.png")
    img = ImageTk.PhotoImage(image1)

    img_label = tkinter.Label(image_tab,
                              image=img,
                              width=500,
                              height=500,
                              cursor="heart")
    img_label.image = img
    img_label.pack(pady=7)

    ttk.Label(
        image_tab,
        text="Preview of image has been minimized to 500x500, "
             "image will be uploaded to hosting in original resolution.").pack()

    root.update()


root = tkinter.Tk()

options = (("Minimize", "minimize"),
           ("Close", "close"))

selected_option = tkinter.StringVar()

root.geometry("640x670")

root.title("Image Uploader")
root.iconbitmap("static/icon.ico")

root.resizable(False, False)

root.protocol("WM_DELETE_WINDOW", on_closing)

tabControl = ttk.Notebook(root)

image_tab = ttk.Frame(tabControl)
upload_history_tab = ttk.Frame(tabControl)
settings_tab = ttk.Frame(tabControl)


tabControl.add(image_tab, text="Images")
tabControl.add(upload_history_tab, text="Upload History")
tabControl.add(settings_tab, text="Settings")


tabControl.pack(expand=1, fill="both")

ttk.Button(image_tab,
           text="Grab image from clipboard",
           command=get_image_from_clipboard,
           cursor="hand2").pack(pady=10)

ttk.Button(image_tab,
           text="Upload",
           cursor="hand2").pack()

tkinter.Label(settings_tab, text="Image Description:").pack()

desc = ttk.Entry(settings_tab, width=75)
desc.insert(tkinter.END, config["config"]["description"])

desc.pack(pady=10)

ttk.Label(settings_tab, text="On exit:").pack()

for option in options:
    r = ttk.Radiobutton(
        settings_tab,
        text=option[0],
        value=option[1],
        cursor="hand2",
        variable=selected_option
    )
    r.pack(fill="x", padx=87, pady=5)

ttk.Button(settings_tab, text="Submit", command=change_settings, cursor="hand2").pack(fill="x", padx=87, pady=10)

ttk.Label(upload_history_tab, text="Here is all your links to your uploaded images.").pack(pady=10)

root.mainloop()

