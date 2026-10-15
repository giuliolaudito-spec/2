import discord
from discord.ext import commands
import asyncio
import threading
import tkinter as tk
import os
import win32com.client

intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

finestra_principale = None
lista_popup_secondari = []
attacco_attivo = False
wmp_player = None

def _esecuzione_pulizia_safe():
    global finestra_principale, lista_popup_secondari
    for popup in lista_popup_secondari:
        try:
            popup.destroy()
        except:
            pass
    lista_popup_secondari.clear()

    if finestra_principale:
        try:
            finestra_principale.quit()
            finestra_principale.destroy()
        except:
            pass
        finestra_principale = None

def chiudi_tutti_i_popup():
    global attacco_attivo, wmp_player
    attacco_attivo = False 
    try:
        if wmp_player:
            wmp_player.controls.stop()
            wmp_player = None
        print("[+] Attacco terminato. Audio e finestre rimosse.")
    except Exception as e:
        print(f"[-] Errore nello spegnere l'audio: {e}")
    
    if finestra_principale:
        try:
            finestra_principale.after(0, _esecuzione_pulizia_safe)
        except Exception as e:
            print(f"[-] Errore nel pianificare la chiusura: {e}")

def lancia_finestre_errore_locali():
    global finestra_principale, attacco_attivo, wmp_player
    attacco_attivo = True

    cartella_corrente = os.path.dirname(os.path.abspath(__file__))
    
    # --- TROVA IL FILE AUDIO IN MODO AUTOMATICO ---
    estensioni_test = [".mp4", ".mp3", ".wav", "", ".mp4.mp4"]
    percorso_rilevato = None
    
    for est in estensioni_test:
        nome_test = f"earrape{est}"
        strada_completa = os.path.join(cartella_corrente, nome_test)
        if os.path.exists(strada_completa):
            percorso_rilevato = strada_completa
            break

    if percorso_rilevato:
        try:
            wmp_player = win32com.client.Dispatch("WMPlayer.OCX")
            wmp_player.settings.volume = 100
            wmp_player.URL = percorso_rilevato
            
            def loop_audio_wmp():
                while attacco_attivo and wmp_player:
                    try:
                        stati_fermo = [1, 8]
                        if wmp_player.playState in stati_fermo:
                            wmp_player.controls.play()
                    except:
                        break
                    import time
                    time.sleep(0.5)
            
            wmp_player.controls.play()
            threading.Thread(target=loop_audio_wmp, daemon=True).start()
            print(f"[+] Audio avviato trovando il file: {os.path.basename(percorso_rilevato)}")
        except Exception as e:
            print(f"[-] Impossibile avviare Windows Media Player: {e}")
    else:
        print(f"⚠️ ERRORE CRITICO: Non trovo nessun file chiamato 'earrape' dentro: {cartella_corrente}")
        print("I file presenti in questa cartella sono:")
        for f in os.listdir(cartella_corrente):
            print(f" -> {f}")

    # --- PARTE GRAFICA POP-UP ---
    finestra_principale = tk.Tk()
    finestra_principale.title("Errore di sistema")
    finestra_principale.geometry("450x200")
    finestra_principale.resizable(False, False)
    finestra_principale.attributes('-topmost', True)
    finestra_principale.protocol("WM_DELETE_WINDOW", lambda: None)

    try:
        percorso_immagine = os.path.join(cartella_corrente, "gamer_gun.png")
        img_originale = tk.PhotoImage(file=percorso_immagine)
        larghezza_sub = max(1, img_originale.width() // 150)
        altezza_sub = max(1, img_originale.height() // 150)
        img_piccola = img_originale.subsample(larghezza_sub, altezza_sub)
        
        label_img = tk.Label(finestra_principale, image=img_piccola)
        label_img.image = img_piccola
        label_img.pack(side="left", padx=15, pady=15)
    except Exception as e:
        print(f"[-] Impossibile caricare l'immagine 'gamer_gun.png': {e}")

    testo_errore = (
        "Il sistema ha rilevato un sovraccarico energetico.\n\n"
        "Ehi, spegni il pc gamer! Stai sprecando energia totalmente!"
    )
    label_testo = tk.Label(finestra_principale, text=testo_errore, font=("Segoe UI", 10), justify="left", wraplength=250)
    label_testo.pack(side="left", padx=10, pady=15)

    def tempesta_popup_personalizzati():
        import random
        while attacco_attivo:
            if not finestra_principale:
                break
            try:
                sub_popup = tk.Toplevel(finestra_principale)
                sub_popup.title("Risparmio Energetico")
                sub_popup.geometry("300x100")
                sub_popup.resizable(False, False)
                sub_popup.attributes('-topmost', True)
                sub_popup.protocol("WM_DELETE_WINDOW", lambda: None)
                
                pos_x = random.randint(100, 800)
                pos_y = random.randint(100, 600)
                sub_popup.geometry(f"+{pos_x}+{pos_y}")

                lbl = tk.Label(sub_popup, text="SPEGNI IL PC!\nL'OCCHIO LASER TI FISSA!!! 🔋❌", font=("Segoe UI", 10, "bold"), fg="red")
                lbl.pack(pady=20)
                
                lista_popup_secondari.append(sub_popup)
            except:
                pass
            import time
            time.sleep(0.4)

    threading.Thread(target=tempesta_popup_personalizzati, daemon=True).start()
    finestra_principale.mainloop()

@bot.event
async def on_ready():
    print(f"[+] Bot Anti-Spam e Ricerca File pronto come {bot.user}")

@bot.event
async def on_presence_update(before: discord.Member, after: discord.Member):
    if after.bot:
        return

    gioco_prima = any(act.type == discord.ActivityType.playing for act in before.activities)
    gioco_dopo = any(act.type == discord.ActivityType.playing for act in after.activities)

    if gioco_dopo and not gioco_prima:
        try:
            await after.send("Ehi!, ti controllo!, non devi superare il limite di gioco Gamer!")
            
            # Timer di test rapido a 10 secondi
            await asyncio.sleep(10)
            
            guild = after.guild
            member_aggiornato = guild.get_member(after.id) if guild else None
            
            if member_aggiornato:
                ancora_in_gioco = any(act.type == discord.ActivityType.playing for act in member_aggiornato.activities)
                
                if ancora_in_gioco:
                    await after.send("Ehi, spegni il pc gamer!, stai sprecando energia totalmente!")
                    await asyncio.sleep(1)
                    
                    print(f"[!] Scatto limite per {after.name}. Lancio attacco totale...")
                    threading.Thread(target=lancia_finestre_errore_locali, daemon=True).start()
                    
                    contatore = 1
                    while ancora_in_gioco:
                        await after.send(f"⚠️ [AVVISO #{contatore}] TI HO DETTO DI SPEGNERE! 🔋❌")
                        contatore += 1
                        # --- MODIFICA ANTI RATE-LIMIT: Pausa di 2 secondi ---
                        await asyncio.sleep(2.0) 
                        
                        member_aggiornato = guild.get_member(after.id)
                        if member_aggiornato:
                            ancora_in_gioco = any(act.type == discord.ActivityType.playing for act in member_aggiornato.activities)
                        else:
                            break
                    
                    chiudi_tutti_i_popup()
                    
                    if contatore > 1:
                        await after.send("♻️ Test concluso con successo!")
                        
        except discord.Forbidden:
            print(f"[-] Impossibile inviare DM a {after.name} (DM chiusi).")

bot.run("MTU1NTI2NjEwNDUxNDA1NjMzNQ.G8hcPs.UShS58uBESPB_aimk6tKUydLSgCvYQ2a83lqHY")
