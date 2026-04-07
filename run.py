import tkinter as tk
from tkinter import filedialog, Menu
import customtkinter as ctk
import os, yt_dlp, winsound, threading, sys, json, shutil
from CTkMenuBar import CTkMenuBar, CustomDropdownMenu

deno_path = shutil.which("deno")
if deno_path:
    os.environ['PATH'] = os.path.dirname(deno_path) + os.pathsep + os.environ.get('PATH', '')

logi_aktiivne = True
playlist_aktiivne = False
madalam_aktiivne = False
kaustade_seaded = {"mp3": None, "mp4": None, "mkv": None}

VERSIOON = "3.1.5 - 07.04.2026"
YT_DLP_VER = "2026.3.17.0"
valik = "mp4"

väljund_kaust = kaustade_seaded.get(valik)
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
    
    '''deno_path = get_path(os.path.join("bin", "deno.exe"))
    if os.path.exists(deno_path):
        ydl_seaded.update({'javascript_executor': deno_path})'''

    
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
            '''ydl.cache.remove()'''
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

def paste(event=None):
    sisend_kast.focus_set()
    try:
        lõikelaud = raam.clipboard_get()
        try:
            sisend_kast.delete("sel.first", "sel.last")
            sisend_kast.insert("insert", lõikelaud)
        except tk.TclError:
            sisend_kast.delete(0, "end")
            sisend_kast.insert("insert", lõikelaud)
        return "break"
    except tk.TclError:
        pass

def copy(event=None):
    try:
        try:
            algus = sisend_kast.index("sel.first")
            lõpp = sisend_kast.index("sel.last")
            tekst = sisend_kast.get()
            valitud_tekst = tekst[algus:lõpp]
        except tk.TclError:
            valitud_tekst = sisend_kast.get()
        raam.clipboard_clear()
        raam.clipboard_append(valitud_tekst)
    except tk.TclError:
        pass

def vali_formaat(v):
    global valik, väljund_kaust
    valik = v
    väljund_kaust = kaustade_seaded.get(v)
    if väljund_kaust:
        kausta_nimi = os.path.basename(väljund_kaust)
        väljund_kast.configure(text=f"Salvestan ({v}): {kausta_nimi}", text_color="yellow")
    else:
        väljund_kast.configure(text=f"Kasutan ({v}) jaoks vaikekausta OUT", text_color="white")
    salvesta_seaded()

def logimine():
    global logi_aktiivne
    logi_aktiivne = not logi_aktiivne
    if logi_aktiivne:
        logi_nupp.configure(fg_color="green", hover_color="#006400")
    else:
        logi_nupp.configure(
            fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"], hover_color=ctk.ThemeManager.theme["CTkButton"]["hover_color"])
    
def playlist():
    global playlist_aktiivne
    playlist_aktiivne = not playlist_aktiivne
    if playlist_aktiivne:
        playlist_nupp.configure(fg_color="green", hover_color="#006400")
    else:
        playlist_nupp.configure(
            fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"], hover_color=ctk.ThemeManager.theme["CTkButton"]["hover_color"])
def madalam():
    global madalam_aktiivne
    madalam_aktiivne = not madalam_aktiivne
    if madalam_aktiivne:
        madalam_nupp.configure(fg_color="green", hover_color="#006400")
    else:
        madalam_nupp.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"], hover_color=ctk.ThemeManager.theme["CTkButton"]["hover_color"])
        
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
        kaustade_seaded[valik] = kaust
        salvesta_seaded()
        
        kausta_nimi = os.path.basename(kaust)
        väljund_kast.configure(text=f"Salvestan ({valik}): {kausta_nimi}", text_color="yellow")
        

def näita_versiooni():
    aken = ctk.CTkToplevel(raam)
    aken.title("Versioon")
    aken.geometry("250x100")
    aken.resizable(False, False)
    ctk.CTkLabel(aken, text=f"ET-DLP v{VERSIOON} \n yt-dlp v{YT_DLP_VER}").pack(expand=True)

def ava_juhend():
    faili_nimi = "juhend.txt"
    if os.path.exists(faili_nimi):
        os.startfile(faili_nimi)
    else:
        väljund_kast.configure(text="Viga: Juhendi faili ei leitud!", text_color="red")

def salvesta_seaded():
    seaded = {
        "kaustad": kaustade_seaded,
        "viimane_formaat": valik
    }
    with open("seadistused.json", "w") as f:
        json.dump(seaded, f)

def laadi_seaded():
    global väljund_kaust, valik, kaustade_seaded
    if os.path.exists("seadistused.json"):
        try:
            with open("seadistused.json", "r") as f:
                seaded = json.load(f)
                kaustade_seaded = seaded.get("kaustad", {"mp3": None, "mp4": None, "mkv": None})
                valik = seaded.get("viimane_formaat", "mp4")
                väljund_kaust = kaustade_seaded.get(valik)
        except Exception:
            pass
        
def kasuta_vaikekausta():
    global väljund_kaust
    kaustade_seaded[valik] = None
    väljund_kaust = None
    salvesta_seaded()
    väljund_kast.configure(text=f"({valik}) kasutab nüüd vaikekausta", text_color="white")

def puhasta_seaded():
    global väljund_kaust, valik
    
    if os.path.exists("seadistused.json"):
        os.remove("seadistused.json")
    
    väljund_kaust = None
    valik = "mp4"
    
    väljund_kast.configure(text="Seadistused tühjendatud. Kasutan vaikekausta (OUT)", text_color="yellow")
    formaat_valik.set("mp4")
    
    print("Seaded on puhastatud!")
    
def puhasta_logi():
    global väljund_kaust, valik
    
    if os.path.exists("laetud.txt"):
        os.remove("laetud.txt")
    väljund_kast.configure(text="Logi tühjendatud", text_color="yellow")

raam = ctk.CTk()

raam.geometry("400x400")
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
väljund_nupp = menüüriba.add_cascade("Vali Kaust", command=vali_kaust)

valikud_fail = CustomDropdownMenu(widget=faili_menüü, corner_radius=0, border_width=2)
valikud_fail.add_option(option="Kasuta vaikekausta (OUT)", command=kasuta_vaikekausta)
valikud_fail.add_separator()
valikud_fail.add_option(option="Tühjenda seadistused", command=puhasta_seaded)
valikud_fail.add_option(option="Tühjenda logi", command=puhasta_logi)
valikud_fail.add_option(option="Välju", command=Sule)

valikud_abi = CustomDropdownMenu(widget=abi_menüü, corner_radius=0, border_width=2)
valikud_abi.add_option(option="Juhend", command=ava_juhend)
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
playlist_nupp.grid(row=2, column=0, padx=5, pady=5, sticky="e")

logi_nupp = ctk.CTkButton(sisu_raam, text='Logija', command=logimine)
logi_nupp.grid(row=2, column=1, padx=5, pady=5, sticky="w")
logi_nupp.configure(fg_color="green", hover_color="#006400")

laadi_seaded()

formaat_valik = ctk.CTkSegmentedButton(sisu_raam, values=["mp3", "mp4", "mkv"], command=vali_formaat)
formaat_valik.set(valik)
formaat_valik.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

sule_nupp = ctk.CTkButton(sisu_raam, text='Sulge', command=Sule)
sule_nupp.grid(row=5, column=0, padx=5, pady=10, sticky="e")

alusta_nupp = ctk.CTkButton(sisu_raam, text='Alusta', command=alusta)
alusta_nupp.grid(row=5, column=1, padx=5, pady=10, sticky="w")

madalam_nupp = ctk.CTkButton(sisu_raam, text='Madalam video kvaliteet (mp4)', command=madalam)
madalam_nupp.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

progress = ctk.CTkProgressBar(sisu_raam, mode="indeterminate")
progress.grid(row=6, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

raam.protocol("WM_DELETE_WINDOW", Sule)
sisend_kast.bind('<Control-v>', paste)
sisend_kast.bind('<Control-c>', lambda e: copy())

if väljund_kaust:
    kausta_nimi = os.path.basename(väljund_kaust)
    väljund_kast.configure(text=f"Salvestan ({valik}): {kausta_nimi}", text_color="yellow")
else:
    väljund_kast.configure(text=f"Kasutan ({valik}) jaoks vaikekausta OUT", text_color="white")


raam.mainloop()