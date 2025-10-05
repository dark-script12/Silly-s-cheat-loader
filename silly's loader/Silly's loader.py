import customtkinter as ctk
import tkinter as tk
import subprocess
import os
import datetime
import json
import sys

# Set dark theme with purple accents
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")  # Tweak for purple

class SillysCheatLoader(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Silly's Cheat Loader")
        self.geometry("800x400")
        self.resizable(False, False)
        
        # Determine base path so bundled exe (PyInstaller) can access resources
        if getattr(sys, "frozen", False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        # Cheat folder and config (absolute paths when bundled)
        self.cheat_folder = os.path.join(base_path, "cheats")
        self.config_file = os.path.join(base_path, "config.json")
        self.load_config()
        
        self.selected_game = None
        self.status_message = None  # For in-UI messages
        self.create_ui()
    
    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                self.cheats = json.load(f)
            # Load discord invite from config meta if present
            try:
                self.discord_invite = self.cheats.get("__meta__", {}).get("discord_invite", "https://discord.gg/uYKTG8HHbf")
            except Exception:
                self.discord_invite = "https://discord.gg/example"
        else:
            self.cheats = {
                "FiveM": {"path": os.path.join(self.cheat_folder, "fivem.exe"), "status": "Online", "last_update": "0 Days Ago", "version": "1.2"},
                "GTA5": {"path": os.path.join(self.cheat_folder, "gta5.exe"), "status": "Offline", "last_update": "0 Days Ago", "version": "1.2"},
                "CSGO": {"path": os.path.join(self.cheat_folder, "csgo.exe"), "status": "Online", "last_update": "0 Days Ago", "version": "1.2"},
                "Warzone": {"path": os.path.join(self.cheat_folder, "warzone.exe"), "status": "Online", "last_update": "0 Days Ago", "version": "1.2"},
                "Minecraft": {"path": os.path.join(self.cheat_folder, "minecraft.exe"), "status": "Offline", "last_update": "0 Days Ago", "version": "1.2"},
            }
            # Add default discord invite setting
            self.discord_invite = "https://discord.gg/example"
            # Embed discord invite in config to persist it
            self.cheats["__meta__"] = {"discord_invite": self.discord_invite}
            self.save_config()
    
    def save_config(self):
        with open(self.config_file, "w") as f:
            json.dump(self.cheats, f, indent=4)
    
    def create_ui(self):
        # Main frame
        main_frame = ctk.CTkFrame(self, fg_color="#1a1a1a")
        main_frame.pack(fill="both", expand=True)
        
        # Subtitle (made by)
        subtitle = ctk.CTkLabel(main_frame, text="Made by: Silly Boy", font=ctk.CTkFont(size=12), text_color="gray")
        subtitle.pack(anchor="nw", padx=10, pady=5)
        
        # Content frame
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)
        
        # Sidebar (left)
        sidebar = ctk.CTkFrame(content_frame, width=200, fg_color="#2b2b2b", corner_radius=10)
        sidebar.pack(side="left", fill="y", padx=(0, 1))
        
        # Game buttons in sidebar
        self.sidebar = sidebar
        self.rebuild_sidebar()
        
    # Sidebar controls are built inside rebuild_sidebar()
        
        # Main pane (right)
        self.main_pane = ctk.CTkFrame(content_frame, fg_color="#1a1a1a", corner_radius=10)
        self.main_pane.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        # Default: Select first game
        if self.cheats:
            self.select_game(list(self.cheats.keys())[0])
    
    def select_game(self, game):
        self.selected_game = game
        for widget in self.main_pane.winfo_children():
            widget.destroy()
        
        info = self.cheats[game]
        
        # Game card in main pane
        card = ctk.CTkFrame(self.main_pane, fg_color="#2b2b2b", border_width=2, border_color="#9932CC", corner_radius=10)
        card.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Logo placeholder (clean text, no emoji)
        logo_label = ctk.CTkLabel(card, text=game.upper(), 
                                  font=ctk.CTkFont(size=40, weight="bold"), text_color="#FFA500")
        logo_label.pack(pady=10)
        
        # Status header
        status_header = ctk.CTkLabel(card, text=f"-- {game} Status: --", font=ctk.CTkFont(size=14), text_color="gray")
        status_header.pack()
        
        # Status details frame
        status_frame = ctk.CTkFrame(card, fg_color="transparent")
        status_frame.pack(pady=5, anchor="w", padx=10)  # Tighter padding and anchor
        
        status_label = ctk.CTkLabel(status_frame, text=f"Status: {info['status']}", 
                                    text_color="green" if info['status'] == "Online" else "red")
        status_label.pack(anchor="w")
        
        update_label = ctk.CTkLabel(status_frame, text=f"Last Update: {info['last_update']}", text_color="white")
        update_label.pack(anchor="w")
        
        version_label = ctk.CTkLabel(status_frame, text=f"Version: {info['version']}", text_color="white")
        version_label.pack(anchor="w")
        
        # Open button at bottom of main pane
        open_btn = ctk.CTkButton(self.main_pane, text=f"Open {game}", fg_color="#9932CC", hover_color="#8A2BE2", width=200,
                                 command=lambda p=info['path']: self.open_cheat(p))
        open_btn.pack(pady=20)
        
        # Status message label (starts hidden)
        self.status_message = ctk.CTkLabel(self.main_pane, text="", font=ctk.CTkFont(size=12), text_color="yellow")
        self.status_message.pack(pady=5)
    
    def show_status_message(self, message, color="green"):
        if self.status_message:
            # Safely update status message and schedule a safe clear that
            # checks the widget still exists before configuring it.
            try:
                self.status_message.configure(text=message, text_color=color)
            except Exception:
                return

            def safe_clear():
                try:
                    # Ensure the widget still has a valid tk name before configuring
                    if str(self.status_message):
                        self.status_message.configure(text="")
                except Exception:
                    # Widget no longer exists or was destroyed; ignore
                    pass

            self.after(5000, safe_clear)  # Hide after 5s
    
    def open_cheat(self, cheat_path):
        if os.path.exists(cheat_path):
            try:
                # Try to launch as admin on Windows using ShellExecute "runas"
                if os.name == 'nt':
                    try:
                        import ctypes
                        from ctypes import wintypes

                        ShellExecute = ctypes.windll.shell32.ShellExecuteW
                        # HWND = None (0), lpOperation = 'runas', lpFile = path
                        res = ShellExecute(None, 'runas', cheat_path, None, None, 1)
                        # On success, returns value > 32
                        if int(res) > 32:
                            self.show_status_message("Opened with admin privileges", "green")
                        else:
                            # Fall back to subprocess if ShellExecute failed
                            subprocess.Popen(cheat_path)
                            self.show_status_message("Opened (no elevation)", "yellow")
                    except Exception as e:
                        # If anything goes wrong with ctypes approach, fallback
                        subprocess.Popen(cheat_path)
                        with open("loader_log.txt", "a") as log:
                            log.write(f"{datetime.datetime.now()}: Elevation attempt failed - {e}\n")
                        self.show_status_message("Opened (fallback, no elevation)", "yellow")
                else:
                    # Non-Windows: regular launch
                    subprocess.Popen(cheat_path)
                    self.show_status_message("Opened successfully", "green")
            except Exception as e:
                with open("loader_log.txt", "a") as log:
                    log.write(f"{datetime.datetime.now()}: Open failed - {e}\n")
                self.show_status_message(f"Cannot open: {str(e)}", "red")
        else:
            self.show_status_message(f"Cannot open: File not found at {cheat_path}", "red")
    
    def reset_to_home(self):
        if self.cheats:
            self.select_game(list(self.cheats.keys())[0])

    def rebuild_sidebar(self):
        """Recreate the sidebar buttons from current self.cheats.

        Keeps the same command callbacks and simple styling. Call after
        changing self.cheats to refresh UI and avoid stale KeyErrors.
        """
        # Clear existing sidebar contents
        for widget in self.sidebar.winfo_children():
            widget.destroy()

        # Game buttons in sidebar
        for game in self.cheats.keys():
            btn = ctk.CTkButton(self.sidebar, text=game, fg_color="transparent", hover_color="#9932CC", anchor="w",
                                command=lambda g=game: self.select_game(g))
            btn.pack(fill="x", pady=5, padx=10)

        # Spacer
        spacer = ctk.CTkLabel(self.sidebar, text="")
        spacer.pack(expand=True)

        # Bottom icons in sidebar (recreate same layout)
        icon_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        icon_frame.pack(fill="x", pady=10)

        home_btn = ctk.CTkButton(icon_frame, text="🏠", width=30, fg_color="transparent", hover_color="#9932CC",
                                 command=self.reset_to_home)
        home_btn.pack(side="left", padx=5)

        gear_btn = ctk.CTkButton(icon_frame, text="⚙️", width=30, fg_color="transparent", hover_color="#9932CC",
                                 command=self.open_settings)
        gear_btn.pack(side="left", padx=5)

        discord_btn = ctk.CTkButton(icon_frame, text="🔗", width=30, fg_color="transparent", hover_color="#9932CC",
                                    command=self.open_discord)
        discord_btn.pack(side="left", padx=(2,5))

        x_btn = ctk.CTkButton(icon_frame, text="❌", width=30, fg_color="transparent", hover_color="#9932CC",
                              command=self.quit_app)
        x_btn.pack(side="left", padx=5)
    
    def open_settings(self):
        settings = ctk.CTkToplevel(self)
        settings.title("Settings")
        settings.geometry("600x400")
        
        label = ctk.CTkLabel(settings, text="Edit Config (JSON format)")
        label.pack(pady=10)
        
        text_box = ctk.CTkTextbox(settings, height=200, width=500)
        # Show config without internal metadata by creating a copy
        config_copy = dict(self.cheats)
        # Remove __meta__ if present to avoid confusion
        config_copy.pop("__meta__", None)
        text_box.insert("0.0", json.dumps(config_copy, indent=4))
        text_box.pack(pady=10)
        
        def save_settings():
            try:
                new_config = json.loads(text_box.get("0.0", "end"))
                # Preserve any existing metadata (like discord invite)
                meta = self.cheats.get("__meta__", {})

                # Keep a copy of the old cheats dict and current selection
                old_cheats = dict(self.cheats)
                old_selected = self.selected_game

                # Replace cheats with new config and preserve meta
                self.cheats = new_config
                if meta:
                    self.cheats["__meta__"] = meta

                # Save config to disk
                self.save_config()

                # Try to preserve selection when an item was renamed.
                # Strategy: If old_selected exists, try to find a new key in
                # self.cheats that has the same path value as the old one.
                new_selected = None
                if old_selected and old_selected in old_cheats:
                    old_info = old_cheats.get(old_selected)
                    # Search for a key in the new config with matching path/version
                    for k, v in self.cheats.items():
                        # Skip meta
                        if k == "__meta__":
                            continue
                        try:
                            if isinstance(old_info, dict) and isinstance(v, dict):
                                # Compare unique-ish identifiers (path + version)
                                if old_info.get("path") == v.get("path") and old_info.get("version") == v.get("version"):
                                    new_selected = k
                                    break
                        except Exception:
                            continue

                # If no direct match found, but the exact old_selected key still exists in new cheats, keep it
                if not new_selected and old_selected in self.cheats:
                    new_selected = old_selected

                # Fallback to first game if nothing maps
                if not new_selected:
                    # pick first non-meta key
                    for k in self.cheats.keys():
                        if k != "__meta__":
                            new_selected = k
                            break

                self.show_status_message("Settings saved and loaded", "green")
                settings.destroy()

                # Rebuild sidebar to reflect renames/adds/removals
                try:
                    self.rebuild_sidebar()
                except Exception:
                    pass

                # Select the resolved game
                if new_selected:
                    self.select_game(new_selected)
                else:
                    self.reset_to_home()
            except json.JSONDecodeError:
                self.show_status_message("Invalid JSON - check your edits", "red")
        
        save_btn = ctk.CTkButton(settings, text="Save", command=save_settings)
        save_btn.pack(pady=10)
    
    def quit_app(self):
        self.destroy()

    def open_discord(self):
        """Open the configured Discord invite URL in the default web browser."""
        try:
            # Try to read from config meta if present
            invite = None
            if isinstance(self.cheats, dict):
                meta = self.cheats.get("__meta__")
                if isinstance(meta, dict):
                    invite = meta.get("discord_invite")

            if not invite:
                # Fallback to attribute saved during init
                invite = getattr(self, "discord_invite", None) or "https://discord.gg/example"

            import webbrowser
            webbrowser.open(invite)
            self.show_status_message("Opened Discord invite", "green")
        except Exception as e:
            with open("loader_log.txt", "a") as log:
                log.write(f"{datetime.datetime.now()}: Open Discord failed - {e}\n")
            self.show_status_message(f"Cannot open Discord: {e}", "red")

if __name__ == "__main__":
    app = SillysCheatLoader()
    app.mainloop()