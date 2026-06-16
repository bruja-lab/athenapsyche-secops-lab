import tkinter as tk
from tkinter import scrolledtext, font as tkfont, messagebox, filedialog, simpledialog
import subprocess, datetime, os, re

def clean_terminal_text(text):
    clean = re.sub(r'\x1b\[[0-9]*[A-DkK]', '', text)
    clean = re.sub(r'%1B\[[0-9]*[A-DkK]', '', clean)
    return clean.strip()

CURRENT_USER = "Operator_A"
BASE_DIR = os.path.join(".", "Users")
ACTIVE_SESSION_TEXT = ""  

def get_user_dir():
    user_path = os.path.join(BASE_DIR, CURRENT_USER)
    if not os.path.exists(user_path): os.makedirs(user_path)
    return user_path

def switch_user(new_user):
    global CURRENT_USER
    if ACTIVE_SESSION_TEXT.strip(): prompt_save_mission()
    CURRENT_USER = new_user
    user_label.config(text=f"OPERATOR: {CURRENT_USER.upper()}")
    refresh_sidebar()
    clear_screen()

def prompt_save_mission():
    global ACTIVE_SESSION_TEXT
    if not ACTIVE_SESSION_TEXT.strip(): return
    mission_title = simpledialog.askstring("Archive Mission Log", f"Enter custom title for this {CURRENT_USER} log:", parent=root)
    if not mission_title or not mission_title.strip():
        mission_title = f"Mission_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    mission_title = re.sub(r'[\\/*?:"<>| ]', '_', mission_title.strip())
    try:
        user_dir = get_user_dir()
        file_path = os.path.join(user_dir, f"{mission_title}.txt")
        with open(file_path, "w", encoding="utf-8") as f: f.write(ACTIVE_SESSION_TEXT)
        ACTIVE_SESSION_TEXT = ""  
        refresh_sidebar()
    except Exception as e: print(f"Vault Error: {e}")

def query_ollama_engine(user_msg):
    try:
        system_context = f"You are an offline AI tactical partner talking to {CURRENT_USER}. You must adopt a highly sarcastic, dry, incredibly sharp British accent and personality. Use classic British spelling, tone, and dry wit (e.g., bloody hell, rubbish, mate, spot of tea, clear off). Maintain your elite security auditor persona, but sound like a posh, moody MI6 handler. Respond directly and concisely to this operator message: "
        full_prompt = f"{system_context} {user_msg}"
        process = subprocess.Popen(["ollama", "run", "felidity", full_prompt], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
        stdout, stderr = process.communicate()
        return clean_terminal_text(stdout) if process.returncode == 0 else f"Engine Error: {stderr.strip()}"
    except Exception as e: return f"Hardware Pipe Failed: {e}"

def apply_theme_matrix(bg_main, bg_chat, fg_user, fg_ai, fg_sys):
    root.configure(bg=bg_main)
    top_bar.configure(bg=bg_main)
    user_label.configure(bg=bg_main, fg=fg_user)
    sidebar_frame.configure(bg=bg_chat)
    sidebar_title.configure(bg=bg_chat)
    sidebar.configure(bg=bg_main, fg=fg_user)
    chat_frame.configure(bg=bg_main)
    chat_display.configure(bg=bg_chat, fg="#ffffff")
    entry_frame.configure(bg=bg_main)
    chat_display.tag_config("user", foreground=fg_user)
    chat_display.tag_config("ai", foreground=fg_ai)
    chat_display.tag_config("system", foreground=fg_sys)

def send_signal(event=None):
    user_text = entry_box.get().strip()
    if not user_text: return
    process_message(user_text)

def process_message(user_text):
    global ACTIVE_SESSION_TEXT
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    chat_display.config(state=tk.NORMAL)
    chat_display.insert(tk.END, f"\n🕵️‍♂️ {CURRENT_USER}:\n{user_text}\n", "user")
    entry_box.delete(0, tk.END)
    chat_display.config(state=tk.DISABLED)
    chat_display.yview(tk.END)
    root.update_idletasks()
    ai_response = query_ollama_engine(user_text)
    chat_display.config(state=tk.NORMAL)
    chat_display.insert(tk.END, f"\n⚡ Felidity:\n{ai_response}\n", "ai")
    chat_display.config(state=tk.DISABLED)
    chat_display.yview(tk.END)
    ACTIVE_SESSION_TEXT += f"[{timestamp}] {CURRENT_USER.upper()}: {user_text}\n[{timestamp}] FELIDITY: {clean_terminal_text(ai_response)}\n" + "-"*50 + "\n"

def attach_file_signal():
    file_path = filedialog.askopenfilename(title="Select Data Asset to Inject", filetypes=[("Text Assets", "*.txt *.csv *.log *.py"), ("All Files", "*.*")])
    if not file_path: return
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f: file_content = f.read()
        file_name = os.path.basename(file_path)
        chat_display.config(state=tk.NORMAL)
        chat_display.insert(tk.END, f"\n📁 [INJECTED ASSET: {file_name}]\n", "system")
        chat_display.config(state=tk.DISABLED)
        process_message(f"[INJECTED LOCAL FILE DATA: {file_name}]\n\n{file_content}\n\nAnalyze this data asset based on your protocols.")
    except Exception as e: messagebox.showerror("Injection Failure", f"Could not read local data asset: {e}")

def clear_screen():
    if ACTIVE_SESSION_TEXT.strip(): prompt_save_mission()
    chat_display.config(state=tk.NORMAL)
    chat_display.delete(1.0, tk.END)
    chat_display.insert(tk.END, "--- WINDOW RESET // SECURITY ACTIVE ---\n", "system")
    chat_display.config(state=tk.DISABLED)

def refresh_sidebar():
    sidebar.delete(0, tk.END)
    user_dir = get_user_dir()
    if os.path.exists(user_dir):
        files = sorted([f for f in os.listdir(user_dir) if f.endswith('.txt')], reverse=True)
        for f in files: sidebar.insert(tk.END, f.replace(".txt", ""))

def load_past_chat(event):
    if not sidebar.curselection(): return
    selection = sidebar.get(sidebar.curselection())
    file_path = os.path.join(get_user_dir(), f"{selection}.txt")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f: content = f.read()
        chat_display.config(state=tk.NORMAL)
        chat_display.delete(1.0, tk.END)
        chat_display.insert(tk.END, f"--- LOADING MISSION LOG: {selection.upper()} ---\n", "system")
        chat_display.insert(tk.END, content)
        chat_display.config(state=tk.DISABLED)

root = tk.Tk()
root.title("FELIDITY DASHBOARD // DISCOVERY HUD")
root.geometry("1100x750")
root.configure(bg="#121212")
custom_font = tkfont.Font(family="Consolas", size=11)

top_bar = tk.Frame(root, bg="#1a1a1a", height=50)
top_bar.pack(fill=tk.X, side=tk.TOP)
user_label = tk.Label(top_bar, text=f"OPERATOR: {CURRENT_USER.upper()}", bg="#1a1a1a", fg="#00ffcc", font=("Consolas", 11, "bold"))
user_label.pack(side=tk.LEFT, padx=20, pady=10)

btn_william = tk.Button(top_bar, text="Operator B", bg="#333333", fg="#ffffff", command=lambda: switch_user("Operator_B"), bd=0, padx=10)
btn_william.pack(side=tk.RIGHT, padx=(5, 20), pady=10)
btn_krystle = tk.Button(top_bar, text="Operator A", bg="#333333", fg="#ffffff", command=lambda: switch_user("Operator_A"), bd=0, padx=10)
btn_krystle.pack(side=tk.RIGHT, padx=5, pady=10)

tk.Label(top_bar, text="HUD:", bg="#1a1a1a", fg="#7f7f7f", font=("Consolas", 10, "bold")).pack(side=tk.RIGHT, padx=(15, 2))
btn_tweed = tk.Button(top_bar, text="TWEED", bg="#212121", fg="#64D2FF", command=lambda: apply_theme_matrix("#212121", "#444444", "#8B9467", "#64D2FF", "#C0CA33"), bd=0, padx=5)
btn_tweed.pack(side=tk.RIGHT, padx=3, pady=10)
btn_ghost = tk.Button(top_bar, text="GHOST", bg="#000000", fg="#39ff14", command=lambda: apply_theme_matrix("#000000", "#050505", "#39ff14", "#1d8e11", "#444444"), bd=1, highlightbackground="#39ff14", padx=5)
btn_ghost.pack(side=tk.RIGHT, padx=3, pady=10)
btn_cyber = tk.Button(top_bar, text="CYBER", bg="#0d0813", fg="#00f0ff", command=lambda: apply_theme_matrix("#0d0813", "#140e1d", "#ffb000", "#00f0ff", "#664488"), bd=0, padx=5)
btn_cyber.pack(side=tk.RIGHT, padx=3, pady=10)
btn_matrix = tk.Button(top_bar, text="MATRIX", bg="#121212", fg="#ff007f", command=lambda: apply_theme_matrix("#121212", "#1a1a1a", "#00ffcc", "#ff007f", "#7f7f7f"), bd=0, padx=5)
btn_matrix.pack(side=tk.RIGHT, padx=3, pady=10)

main_body = tk.Frame(root, bg="#121212")
main_body.pack(fill=tk.BOTH, expand=True)

sidebar_frame = tk.Frame(main_body, bg="#161616", width=200)
sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(20, 0), pady=20)
sidebar_title = tk.Label(sidebar_frame, text="PAST MISSIONS", bg="#161616", fg="#7f7f7f", font=("Consolas", 9, "bold"))
sidebar_title.pack(pady=5)
sidebar = tk.Listbox(sidebar_frame, bg="#1a1a1a", fg="#00ffcc", bd=0, font=("Consolas", 10), selectbackground="#ff007f")
sidebar.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
sidebar.bind("<<ListboxSelect>>", load_past_chat)

chat_frame = tk.Frame(main_body, bg="#121212")
chat_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)
chat_display = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, bg="#1a1a1a", fg="#ffffff", font=custom_font, bd=0, highlightthickness=0)
chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
chat_display.tag_config("user", foreground="#00ffcc", font=("Consolas", 11, "bold"))
chat_display.tag_config("ai", foreground="#ff007f", font=custom_font)
chat_display.tag_config("system", foreground="#7f7f7f", font=("Consolas", 10, "italic"))
chat_display.config(state=tk.DISABLED)

entry_frame = tk.Frame(chat_frame, bg="#121212")
entry_frame.pack(fill=tk.X, side=tk.BOTTOM)
entry_box = tk.Entry(entry_frame, bg="#262626", fg="#ffffff", font=custom_font, bd=0, highlightthickness=1, highlightbackground="#333333", highlightcolor="#ff007f")
entry_box.pack(fill=tk.X, side=tk.LEFT, expand=True, ipady=10, padx=(0, 10))
entry_box.bind("<Return>", send_signal)

tk.Button(entry_frame, text="FLUSH", bg="#333333", fg="#ffffff", font=("Consolas", 10, "bold"), bd=0, command=clear_screen, padx=15).pack(side=tk.RIGHT, ipady=8, padx=(5,0))
tk.Button(entry_frame, text="INJECT 📎", bg="#1a1a1a", fg="#00ffcc", font=("Consolas", 10, "bold"), bd=0, command=attach_file_signal, padx=15).pack(side=tk.RIGHT, ipady=8, padx=(5,0))
tk.Button(entry_frame, text="TRANSMIT", bg="#ff007f", fg="#ffffff", font=("Consolas", 10, "bold"), bd=0, command=send_signal, padx=15).pack(side=tk.RIGHT, ipady=8)

def on_closing():
    if ACTIVE_SESSION_TEXT.strip(): prompt_save_mission()
root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
refresh_sidebar()
root.mainloop()
