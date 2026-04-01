import tkinter as tk
from tkinter import filedialog, Menu
import customtkinter as ctk
import os, yt_dlp, winsound, threading, sys
from CTkMenuBar import CTkMenuBar, CustomDropdownMenu



logi_aktiivne = True
playlist_aktiivne = False
madalam_aktiivne = False
valik = "mp4"

VERSIOON = "3.0.0"
YT_DLP_VER = "2026.03.17"

väljund_kaust = None
logi_aken = None
logi_tekstikast = None

def get_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def Sule():
    raam.quit()
    raam.destroy()
    os._exit(0)
    
def alusta():
    väljund_kast.configure(text = "Töötan..", text_color="white")
    progress.start()
    alusta_nupp.configure(state="disabled")
    thread = threading.Thread(target=alusta_töö, daemon=True)
    thread.start()
    
def alusta_töö():
    
    link = sisend_kast.get()
    
    if not link:
        raam.after(0, lõpeta, "Sisesta link!")
        return
    
    ffmpeg_dir = get_path(os.path.join("bin", "ffmpeg", "bin"))
    base_out_path = väljund_kaust if väljund_kaust else os.path.join(os.getcwd(), "OUT")
    out_path = os.path.join(base_out_path, "%(title)s.%(ext)s")
    ydl_seaded= {'outtmpl': out_path,'ffmpeg_location': ffmpeg_dir, 'noplaylist': True, 'quiet': False, }
    ydl_seaded.update({'remote_components': ['ejs:github']})
    
    if not os.path.exists(base_out_path):
        os.makedirs(base_out_path)
        
    if playlist_aktiivne:
        ydl_seaded.update({'noplaylist': False})
        
    if logi_aktiivne:
        archive_file = os.path.join(os.getcwd(), 'laetud.txt')
        ydl_seaded.update({ 'download_archive': archive_file})
        
    
    if valik == 'mp3':
        print("mp3")
        ydl_seaded.update({
        'format': 'bestaudio/best',
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
            {
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            },
            {
                'key': 'EmbedThumbnail',
            }
        ],
        'writethumbnail': True,
    })
    elif valik == 'mp4':
        print("mp4")
        
        if madalam_aktiivne:
            ydl_seaded.update({
            'format': 'bestvideo[vcodec^=avc1][ext=mp4][height<=720]+bestaudio[acodec^=mp4a][ext=m4a]/bestvideo[vcodec^=avc1]+bestaudio[acodec^=mp4a]/mp4',
            'writethumbnail': True,
            'postprocessors': [{'key': 'EmbedThumbnail'}],
            'merge_output_format': 'mp4',})
       
        
        else:
            ydl_seaded.update({
            'format': 'bestvideo[vcodec^=avc1][ext=mp4]+bestaudio[acodec^=mp4a][ext=m4a]/bestvideo[vcodec^=avc1]+bestaudio[acodec^=mp4a]/mp4',
            'writethumbnail': True,
            'postprocessors': [{'key': 'EmbedThumbnail'}],
            'merge_output_format': 'mp4',})
        
    elif valik == "mkv":
        print("mkv")
        ydl_seaded.update({'format': 'bestvideo+bestaudio/best', 'merge_output_format': 'mkv', 'writethumbnail': True, 'postprocessors': [{'key': 'EmbedThumbnail'}]})
        
    def progress_hook(d):
        if d['status'] == 'downloading':
            index = d.get('info_dict', {}).get('playlist_index')
            count = d.get('info_dict', {}).get('playlist_count')
            if index and count:
                väljund_kast.configure(text=f"{index}/{count}")
            
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes', 0)
            if total:
                progress.stop()
                progress.configure(mode="determinate")
                progress.set(downloaded / total)
            else:
                progress.configure(mode="indeterminate")
                progress.start()

    ydl_seaded.update({'progress_hooks': [progress_hook]})
    
    
    try:
        with yt_dlp.YoutubeDL(ydl_seaded) as ydl:
            ydl.download([link])
        raam.after(0, lõpeta, "Allalaadimine õnnestus!")
    except Exception as e:
        with open("error_log.txt", "w", encoding="utf-8") as f:
            f.write(str(e))
        raam.after(0, lõpeta, f"Viga: {e}")
    
def lõpeta(tekst):
    progress.stop()
    väljund_kast.configure(text=tekst, text_color="white")
    alusta_nupp.configure(state="normal")
    winsound.MessageBeep(winsound.MB_ICONASTERISK)


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
    

def vali_formaat(v):
    global valik
    valik = v
    formaat_valik.set(v)

def logimine():
    global logi_aktiivne
    logi_aktiivne = not logi_aktiivne
    logi_nupp.configure(fg_color=("green" if logi_aktiivne else ctk.ThemeManager.theme["CTkButton"]["fg_color"]))

def playlist():
    global playlist_aktiivne
    playlist_aktiivne = not playlist_aktiivne
    playlist_nupp.configure(fg_color=("green" if playlist_aktiivne else ctk.ThemeManager.theme["CTkButton"]["fg_color"]))

def madalam():
    global madalam_aktiivne
    madalam_aktiivne = not madalam_aktiivne
    madalam_nupp.configure(fg_color=("green" if madalam_aktiivne else ctk.ThemeManager.theme["CTkButton"]["fg_color"]))

def progress_hook(d):
    if d['status'] == 'downloading':
        index = d.get('playlist_index')
        count = d.get('playlist_count')
        if index and count:
            raam.after(0, väljund_kast.configure, {"text": f"Laadin {index}/{count}..."})

def vali_kaust():
    global väljund_kaust
    kaust = filedialog.askdirectory()
    if kaust:
        väljund_kaust = kaust
        

def näita_versiooni():
    aken = ctk.CTkToplevel(raam)
    aken.title("Versioon")
    aken.geometry("250x100")
    aken.resizable(False, False)
    ctk.CTkLabel(aken, text=f"ET-DLP v{VERSIOON} \n yt-dlp v{YT_DLP_VER}").pack(expand=True)

raam = ctk.CTk()

raam.geometry("450x400")
raam.title("ET-DLP")

menüüriba = CTkMenuBar(raam, bg_color="#343638")

sisu_raam = ctk.CTkFrame(raam)
sisu_raam.pack(fill="both", expand=True)

sisu_raam.rowconfigure((0,1,2,3,4,5,6,7), weight=1)

menu = Menu(sisu_raam,tearoff=0)
menu.add_command(label='Copy',command=copy)
menu.add_command(label='Paste',command=paste)
menu.configure(bg="#2b2b2b", fg="white", activebackground="#3b3b3b", activeforeground="white")

faili_menüü = menüüriba.add_cascade("Fail")
abi_menüü = menüüriba.add_cascade("Abi")

valikud_fail = CustomDropdownMenu(widget=faili_menüü, corner_radius=0, border_width=2)
valikud_fail.add_option(option="Vali väljundkaust", command=vali_kaust)
valikud_fail.add_separator()
valikud_fail.add_option(option="Välju", command=Sule)

valikud_abi = CustomDropdownMenu(widget=abi_menüü, corner_radius=0, border_width=2)
valikud_abi.add_option(option="Versioon", command=näita_versiooni)


sisu_raam.columnconfigure((0,1), weight=1, uniform="col")
raam.iconbitmap(get_path("icon.ico"))

ctk.CTkLabel(sisu_raam, text="Link:").grid(row=0, column=0, columnspan=2, sticky="w", padx=(20,0), pady=10)
sisend_kast = ctk.CTkEntry(sisu_raam, width=400)
sisend_kast.grid(row=0, column=0, columnspan=2, sticky="ew", padx=(70,10), pady=10)
sisend_kast.bind('<Button-3>', popup)

väljund_kast = ctk.CTkLabel(sisu_raam, text="...", fg_color="#343638", text_color="white")
väljund_kast.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5)

playlist_nupp = ctk.CTkButton(sisu_raam, text='Playlist', command=playlist)
playlist_nupp.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

logi_nupp = ctk.CTkButton(sisu_raam, text='Logija', command=logimine)
logi_nupp.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
logi_nupp.configure(fg_color="green")


formaat_valik = ctk.CTkSegmentedButton(sisu_raam, values=["mp3", "mp4", "mkv"], command=vali_formaat)
formaat_valik.set("mp4")
formaat_valik.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

sule_nupp = ctk.CTkButton(sisu_raam, text='Sulge', command=Sule)
sule_nupp.grid(row=5, column=0, padx=5, pady=10, sticky="ew")

madalam_nupp = ctk.CTkButton(sisu_raam, text='Madalam video kvaliteet (mp4)', command=madalam)
madalam_nupp.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

alusta_nupp = ctk.CTkButton(sisu_raam, text='Alusta', command=alusta)
alusta_nupp.grid(row=5, column=1, padx=5, pady=10, sticky="ew")

progress = ctk.CTkProgressBar(sisu_raam, mode="indeterminate")
progress.grid(row=6, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

'''sisu_raam.rowconfigure(7, weight=1)'''


raam.protocol("WM_DELETE_WINDOW", Sule)

raam.mainloop()