import tkinter as tk
from tkinter import filedialog, Menu
from tkinter.ttk import *
import os, yt_dlp


def get_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def Sule():
    raam.destroy()
    
def alusta():
    link = sisend_kast.get()
    väljund_kast.config(text = "Töötan..")
    raam.update()
    
    ffmpeg_dir = get_path(os.path.join("bin", "ffmpeg", "bin"))
    base_out_path = os.path.join(os.getcwd(), "OUT")
    out_path = os.path.join(base_out_path, "%(title)s.%(ext)s")
    ydl_seaded= {'outtmpl': out_path,'ffmpeg_location': ffmpeg_dir, 'noplaylist': True, 'quiet': False,}
    
    if not os.path.exists(base_out_path):
        os.makedirs(base_out_path)
    
    if mp3_nupp.config('relief')[-1] == 'sunken':
        print("mp3")
        ydl_seaded.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',}],})
    elif mp4_nupp.config('relief')[-1] == 'sunken':
        print("mp4")
        ydl_seaded['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
    elif mkv_nupp.config('relief')[-1] == 'sunken':
        print("mkv")
        ydl_seaded.update({'format': 'bestvideo+bestaudio/best', 'merge_output_format': 'mkv'})
        
    try:
        with yt_dlp.YoutubeDL(ydl_seaded) as ydl:
            ydl.download([link])
        väljund_kast.config(text = "Allalaadimine õnnestus!")
        print("Allalaadimine õnnestus!")
    except Exception as e:

        väljund_kast.config(text = "Viga..")
        print(f"Viga: {e}")
    
def toggle_mp3():
    if mp3_nupp.config('relief')[-1] == 'sunken':
        mp3_nupp.config(relief="raised")
    else:
        mkv_nupp.config(relief="raised")
        mp4_nupp.config(relief="raised")
        mp3_nupp.config(relief="sunken")
        

        
        
        
def toggle_mp4():
    if mp4_nupp.config('relief')[-1] == 'sunken':
        mp4_nupp.config(relief="raised")
    else:
        mkv_nupp.config(relief="raised")
        mp4_nupp.config(relief="sunken")
        mp3_nupp.config(relief="raised")
        
def toggle_mkv():
    if mkv_nupp.config('relief')[-1] == 'sunken':
        mkv_nupp.config(relief="raised")
    else:
        mkv_nupp.config(relief="sunken")
        mp4_nupp.config(relief="raised")
        mp3_nupp.config(relief="raised")
        
def popup(event):
    try:
        menu.tk_popup(event.x_root,event.y_root)
    finally:
        menu.grab_release()

def paste():
    clipboard = raam.clipboard_get()
    sisend_kast.insert('end',clipboard)

def copy():
    inp = sisend_kast.get()
    raam.clipboard_clear()
    raam.clipboard_append(inp)

raam = tk.Tk()

raam.geometry("400x350")
raam.title("YT-DLP")

link_tekst = tk.Label(raam, text="Link:")
link_tekst.place(relx=0.05, rely=0.1)
sisend_kast = tk.Entry(raam, width=40)
sisend_kast.place(relx=0.15, rely=0.1)
sisend_kast.bind('<Button-3>',popup)

formaat = tk.Label(raam, text="Faili formaat:")
formaat.place(relx=0.1, rely=0.7, anchor="center")

menu = Menu(raam,tearoff=0)
menu.add_command(label='Copy',command=copy)
menu.add_command(label='Paste',command=paste)

väljund_kast = tk.Label(raam, text="...", bg="#E0E0E0")
väljund_kast.place(relx=0.5, rely=0.325, anchor="center")


mp3_nupp = tk.Button(raam, text='mp3', command=toggle_mp3, relief="raised")
mp3_nupp.place(relx=0.3, rely=0.7, anchor="center")

mp4_nupp = tk.Button(raam, text='mp4', command=toggle_mp4, relief="raised")
mp4_nupp.place(relx=0.5, rely=0.7, anchor="center")

mkv_nupp = tk.Button(raam, text='mkv', command=toggle_mkv, relief="raised")
mkv_nupp.place(relx=0.7, rely=0.7, anchor="center")

sule_nupp = tk.Button(raam, text='Sulge', command=Sule)
sule_nupp.place(relx=0.3, rely=0.9, anchor="center")

alusta_nupp = tk.Button(raam, text='Alusta', command=alusta)
alusta_nupp.place(relx=0.7, rely=0.9, anchor="center")

raam.mainloop()
