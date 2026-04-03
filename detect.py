import os
import sys
import time
import math
from datetime import datetime
import pygame
import random
import glob
import threading
import json
from collections import deque

import pystray
from PIL import Image, ImageDraw, ImageFont
import psutil

is_enabled = True
sound_pack_name = "pack_default"
sounds = []
sounds_lock = threading.Lock()
icon = None

performance_tracking = False
performance_start_time = 0
performance_peak_ram = 0

# Persistent config
config = {
    "sensitivity": 0.4,
    "cooldown_ms": 1000,
    "global_volume": 1.0,
    "last_used_pack": "pack_default",
    "total_bonks": 0,
}
bonks_since_save = 0
config_lock = threading.Lock()
SETTINGS_FILE = None


def get_startup_folder():
    """Get the Windows Startup folder path."""
    return os.path.join(
        os.environ["APPDATA"],
        "Microsoft",
        "Windows",
        "Start Menu",
        "Programs",
        "Startup",
    )


def get_startup_file_path():
    """Get the path to the BonkWin startup batch file."""
    return os.path.join(get_startup_folder(), "BonkWin.bat")


def is_startup_enabled(item=None):
    """Check if the startup batch file exists."""
    return os.path.exists(get_startup_file_path())


def toggle_startup(icon, item):
    """Enable or disable auto-start by creating/removing a batch file."""
    startup_path = get_startup_file_path()
    if is_startup_enabled():
        try:
            os.remove(startup_path)
            log_output("[STEP 7] 🚀 Startup link Removed successfully")
        except Exception as e:
            log_output(f"[STEP 7] Error removing startup link: {e}")
    else:
        try:
            project_dir = get_project_dir()
            python_exe = sys.executable
            script_path = os.path.abspath(__file__)

            # Create a batch file that runs the script
            cmd = f'@echo off\ncd /d "{project_dir}"\nstart "" "{python_exe}" "{script_path}"\n'

            with open(startup_path, "w", encoding="utf-8") as f:
                f.write(cmd)
            log_output("[STEP 7] 🚀 Startup link Created successfully")
        except Exception as e:
            log_output(f"[STEP 7] Error creating startup link: {e}")

    icon.update_menu()


def create_image():
    # 64x64 bold color scheme
    width = 64
    height = 64
    color1 = (255, 69, 0)  # Red-Orange
    color2 = (255, 255, 255)  # White

    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    dc = ImageDraw.Draw(image)
    dc.ellipse([0, 0, width, height], fill=color1)

    # Draw "B"
    try:
        font = ImageFont.truetype("arialbd.ttf", 40)
    except IOError:
        font = ImageFont.load_default()

    text = "B"
    try:
        left, top, right, bottom = dc.textbbox((0, 0), text, font=font)
        text_w = right - left
        text_h = bottom - top
        dc.text(
            ((width - text_w) / 2, (height - text_h) / 2 - 4),
            text,
            font=font,
            fill=color2,
        )
    except AttributeError:
        text_w, text_h = dc.textsize(text, font=font)
        dc.text(
            ((width - text_w) / 2, (height - text_h) / 2), text, font=font, fill=color2
        )

    return image


def load_config():
    """Load config from settings.json with defaults."""
    global config, SETTINGS_FILE, sound_pack_name
    SETTINGS_FILE = os.path.join(get_data_dir(), "settings.json")

    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved_config = json.load(f)
                for key in config:
                    if key in saved_config:
                        config[key] = saved_config[key]
        except json.JSONDecodeError:
            log_output(
                "[STEP 6] Error: settings.json contains invalid JSON. Using defaults."
            )
        except Exception as e:
            log_output(f"[STEP 6] Warning: Could not load settings: {e}")

    # Update global sound_pack_name from config
    sound_pack_name = config.get("last_used_pack", "pack_default")

    log_output(f"[STEP 6] Loaded stats: {config['total_bonks']} total bonks")
    return config


def save_config():
    """Save config to settings.json. Thread-safe."""
    with config_lock:
        try:
            config["last_used_pack"] = sound_pack_name
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            log_output(f"[STEP 6] Warning: Could not save settings: {e}")


def on_open_settings(icon, item):
    """Open the settings.json file in the default text editor."""
    try:
        if os.path.exists(SETTINGS_FILE):
            os.startfile(SETTINGS_FILE)
            log_output("[STEP 5] ⚙️ Settings file opened for manual editing.")
        else:
            save_config()
            os.startfile(SETTINGS_FILE)
            log_output(
                "[STEP 5] ⚙️ Settings file created and opened for manual editing."
            )
    except Exception as e:
        log_output(f"[STEP 5] Error opening settings file: {e}")


def on_reset_stats(icon, item):
    """Reset bonk counter to 0."""
    global bonks_since_save
    config["total_bonks"] = 0
    bonks_since_save = 0
    save_config()
    update_tray_menu()
    log_output("[STEP 6] Stats reset! Counter set to 0.")


def update_tray_menu():
    """Update tray menu and tooltip with current stats."""
    global icon
    if icon is None:
        return

    count = config["total_bonks"]
    if count == 1:
        icon.title = f"BonkWin — {count} Bonk Detected"
    else:
        icon.title = f"BonkWin — {count} Bonks Detected"

    build_and_set_menu()


def on_toggle_enable(icon, item):
    global is_enabled
    is_enabled = not is_enabled
    count = config["total_bonks"]
    if is_enabled:
        if count == 1:
            icon.title = f"BonkWin — Listening ({count} Bonk)"
        else:
            icon.title = f"BonkWin — Listening ({count} Bonks)"
    else:
        if count == 1:
            icon.title = f"BonkWin — Paused ({count} Bonk)"
        else:
            icon.title = f"BonkWin — Paused ({count} Bonks)"


def get_enable_state(item):
    return is_enabled


def on_quit(icon, item):
    log_output("[STEP 3] Quitting BonkWin...")
    save_config()
    icon.stop()


def get_available_packs():
    """Scan sounds/ directory and return list of subdirectory names (sound packs)."""
    sounds_dir = os.path.join(get_project_dir(), "sounds")
    packs = []
    if os.path.exists(sounds_dir):
        for entry in os.listdir(sounds_dir):
            entry_path = os.path.join(sounds_dir, entry)
            if os.path.isdir(entry_path):
                packs.append(entry)
    return sorted(packs)


def load_pack(pack_name):
    """Load all sound files from the specified pack. Thread-safe."""
    global sounds, sound_pack_name
    sounds_dir = os.path.join(get_project_dir(), "sounds", pack_name)
    new_sounds = []

    if os.path.exists(sounds_dir):
        for ext in ("*.wav", "*.mp3", "*.ogg"):
            new_sounds.extend(glob.glob(os.path.join(sounds_dir, ext)))

    with sounds_lock:
        sounds = new_sounds
        sound_pack_name = pack_name

    log_output(
        f"[STEP 4] 📂 Switched to pack: {pack_name} (Loaded {len(new_sounds)} sounds)"
    )
    return len(new_sounds)


def get_pack_checked(item):
    """Callback to check if this pack is currently selected."""
    return item.text == f"✓ {sound_pack_name}" or item.text == sound_pack_name


def on_pack_selected(icon, pack_name):
    """Handle sound pack selection from tray menu."""
    load_pack(pack_name)
    # Save the selected pack to config immediately for persistence
    global config
    config["last_used_pack"] = pack_name
    save_config()
    icon.update_menu()


def setup_tray_and_run():
    global icon
    img = create_image()
    img.save(os.path.join(get_project_dir(), "icon.png"))
    build_and_set_menu()
    icon.run()


def build_and_set_menu():
    """Build and set the tray menu with current stats."""
    global icon
    img = create_image()
    available_packs = get_available_packs()

    pack_menu_items = []
    for pack in available_packs:
        display_name = f"✓ {pack}" if pack == sound_pack_name else pack
        pack_menu_items.append(
            pystray.MenuItem(
                display_name,
                lambda icon, p=pack: on_pack_selected(icon, p),
                radio=True,
                checked=lambda item, p=pack: p == sound_pack_name,
            )
        )

    settings_menu = pystray.Menu(
        pystray.MenuItem("Reset Stats", on_reset_stats),
        pystray.MenuItem(
            "Launch at Startup", toggle_startup, checked=is_startup_enabled
        ),
        pystray.MenuItem("Open Settings File", on_open_settings),
    )

    count = config["total_bonks"]
    stats_text = f"Total Bonks: {count}"

    if count == 1:
        tooltip = f"BonkWin — {count} Bonk Detected"
    else:
        tooltip = f"BonkWin — {count} Bonks Detected"

    menu = pystray.Menu(
        pystray.MenuItem(
            "Enable Detection", on_toggle_enable, checked=get_enable_state
        ),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(stats_text, lambda: None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Sound Packs", pystray.Menu(*pack_menu_items)),
        pystray.MenuItem(
            f"Current Pack: {sound_pack_name}", lambda: None, enabled=False
        ),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Settings", settings_menu),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", on_quit),
    )

    if icon is None:
        icon = pystray.Icon("BonkWin", img, title=tooltip, menu=menu)
        log_output("[STEP 3] System tray icon created. Right-click to manage.")
    else:
        icon.title = tooltip
        icon.menu = menu
        icon.update_menu()


def get_project_dir():
    """Get the absolute path to the directory containing the project files."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def get_data_dir():
    """Get the directory for user data (settings, output, etc.) that is writable."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


OUTPUT_FILE = os.path.join(get_data_dir(), "OUTPUT.md")
ROADMAP_FILE = os.path.join(get_data_dir(), "ROADMAP.md")


def log_output(message):
    print(message)
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")


def init_files():
    if not os.path.exists(ROADMAP_FILE):
        with open(ROADMAP_FILE, "w", encoding="utf-8") as f:
            f.write(
                "# BonkWin Roadmap\n\n## ✅ Done\n- Step 1: Detection engine\n- Step 2: Sound playback\n- Step 3: System tray icon\n- Step 4: Sound pack switcher\n- Step 5: Settings\n- Step 6: Bonk counter\n- Step 7: Auto-start\n- Step 8: Package as .exe\n- Step 9: Installer\n\n## 🔄 In Progress\n- Optimizations (OPT-1 to OPT-5)\n"
            )
    if not os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("")


def main():
    global sounds, sound_pack_name
    # Performance tracking variables
    global \
        false_trigger_count, \
        successful_knock_count, \
        performance_tracking, \
        performance_start_time, \
        pygame_initialized
    init_files()
    load_config()

    # Initialize performance tracking for this session
    performance_tracking = True
    performance_start_time = time.time()
    false_trigger_count = 0
    successful_knock_count = 0
    pygame_initialized = False

    log_output("[PERF] Performance tracking started")

    # OPT-6: Lazy load pygame - don't initialize mixer at startup
    sound_enabled = False
    pygame_initialized = False
    # Get all available sound packs
    available_packs = get_available_packs()
    log_output(f"[STEP 2] Available sound packs: {available_packs}")
    if not available_packs:
        log_output("[STEP 2] Warning: No sound packs found in sounds/ directory")
    else:
        # Try to load the last used pack if it's still available, otherwise use the first available pack
        pack_to_load = (
            sound_pack_name
            if sound_pack_name in available_packs
            else available_packs[0]
        )
        load_pack(pack_to_load)
        sound_enabled = len(sounds) > 0
        # Safely encode pack name for logging to avoid Unicode errors
        safe_pack_name = repr(pack_to_load)[1:-1]  # Remove quotes from repr
        if sound_enabled:
            log_output(
                f"[STEP 2] Sound pack loaded ({len(sounds)} sound(s) from pack '{safe_pack_name}') - mixer will initialize on first bonk"
            )
        else:
            log_output(
                f"[STEP 2] Warning: No sound files found in pack '{safe_pack_name}'"
            )

    # OPT-3: Startup Speed (Device Caching)
    target_device_index = None
    import sounddevice as sd
    import numpy as np

    if "last_device_index" in config:
        cached_index = config["last_device_index"]
        try:
            sd.check_input_settings(device=cached_index, samplerate=44100, channels=1)
            target_device_index = cached_index
            log_output(f"[STEP 1] Using cached device index {cached_index}")
        except Exception as e:
            log_output(f"[STEP 1] Cached device invalid: {e}")
            target_device_index = None

    if target_device_index is None:
        log_output("[STEP 1] Starting device discovery...")
        devices = sd.query_devices()
        realtek_devices = [
            i
            for i, d in enumerate(devices)
            if d["max_input_channels"] > 0 and "realtek" in d["name"].lower()
        ]

        SAMPLE_RATE = 44100
        # Try Realtek first
        for idx in realtek_devices:
            try:
                sd.check_input_settings(device=idx, samplerate=SAMPLE_RATE, channels=1)
                target_device_index = idx
                config["last_device_index"] = target_device_index
                save_config()
                log_output(f"[STEP 1] Found working Realtek device at index {idx}")
                break
            except sd.PortAudioError:
                continue

        if target_device_index is None:
            # Fall back to default
            target_device_index = sd.default.device[0]
            try:
                sd.check_input_settings(
                    device=target_device_index, samplerate=SAMPLE_RATE, channels=1
                )
            except sd.PortAudioError:
                # Find ANY working input
                for idx, dev in enumerate(devices):
                    if dev["max_input_channels"] > 0:
                        try:
                            sd.check_input_settings(
                                device=idx, samplerate=SAMPLE_RATE, channels=1
                            )
                            target_device_index = idx
                            break
                        except sd.PortAudioError:
                            continue
                else:
                    log_output("[STEP 1] FATAL: No working input devices found!")
                    sys.exit(1)

        # Cache the found device
        config["last_device_index"] = target_device_index
        save_config()

    log_output(
        f"[STEP 1] Active device: {sd.query_devices(target_device_index)['name']}"
    )

    SAMPLE_RATE = 44100
    BLOCK_DURATION = 0.020
    BLOCK_SIZE = int(SAMPLE_RATE * BLOCK_DURATION)

    # State variables
    last_bonk_time = 0
    potential_bonk_time = 0.0
    history_length = int(2.0 / BLOCK_DURATION)
    ambient_history = deque(maxlen=history_length)

    def process_audio(indata, frames, time_info, status):
        nonlocal last_bonk_time, potential_bonk_time, ambient_history
        global \
            is_enabled, \
            sounds, \
            false_trigger_count, \
            successful_knock_count, \
            performance_tracking, \
            performance_peak_ram

        if not is_enabled:
            return

        current_time = time.time()
        audio_data = indata[:, 0]

        # OPT-1: CPU Pre-filter (RMS check)
        raw_rms = np.sqrt(np.mean(audio_data**2))
        if raw_rms < 0.001:
            if len(ambient_history) < history_length:
                ambient_history.append(raw_rms)
            return

        # Low pass filter (< 300Hz)
        fft_data = np.fft.rfft(audio_data)
        freqs = np.fft.rfftfreq(len(audio_data), 1 / SAMPLE_RATE)
        filtered_fft = fft_data * (freqs < 300)
        filtered_audio = np.fft.irfft(filtered_fft)

        rms = np.sqrt(np.mean(filtered_audio**2))

        if len(ambient_history) < history_length:
            ambient_history.append(rms)
            return

        avg_floor = sum(ambient_history) / len(ambient_history)
        if rms < avg_floor * 3.0:
            ambient_history.append(rms)

        threshold = max(avg_floor * 5.0, 0.01)
        cooldown_seconds = config["cooldown_ms"] / 1000.0

        if rms > threshold and current_time - last_bonk_time > cooldown_seconds:
            intensity = min(rms / 0.15, 1.0)
            if intensity >= config["sensitivity"]:
                # OPT-2: Double-Hit Confirmation
                if current_time - potential_bonk_time <= 0.05:
                    # Performance tracking for knock detection
                    if performance_tracking:
                        successful_knock_count += 1
                        log_output(f"[PERF] Successful knock #{successful_knock_count}")
                    log_output(f"[STEP 2] Knock detected! Intensity: {intensity:.2f}")
                    last_bonk_time = current_time
                else:
                    # Performance tracking for false triggers
                    if performance_tracking:
                        false_trigger_count += 1
                        log_output(
                            f"[PERF] False trigger #{false_trigger_count} (single spike)"
                        )
                    potential_bonk_time = current_time

                # Process bonk
                global bonks_since_save
                with config_lock:
                    config["total_bonks"] += 1
                    bonks_since_save += 1
                    current_count = config["total_bonks"]

                if bonks_since_save >= 5:
                    threading.Thread(target=save_config, daemon=True).start()
                    with config_lock:
                        bonks_since_save = 0

                if icon:
                    threading.Thread(target=update_tray_menu, daemon=True).start()

                with sounds_lock:
                    current_sounds = sounds.copy()

                if sound_enabled and current_sounds:
                    # OPT-6: Lazy initialize pygame mixer on first bonk
                    if not pygame_initialized:
                        try:
                            pygame.mixer.init()
                            pygame_initialized = True
                            log_output(
                                "[STEP 2] 🔊 Sound system initialized (lazy load)"
                            )
                        except Exception as e:
                            log_output(
                                f"[STEP 2] Warning: Could not initialize sound system: {e}"
                            )
                            sound_enabled = False
                            pygame_initialized = True  # Prevent retry loop

                    if pygame_initialized and sound_enabled:
                        volume = max(
                            0.10, min(intensity * config["global_volume"], 1.0)
                        )
                        sound_file = random.choice(current_sounds)
                        try:
                            s = pygame.mixer.Sound(sound_file)
                            s.set_volume(volume)
                            s.play()
                            log_output(
                                f"[STEP 2] 🔊 Played: {os.path.basename(sound_file)} ({int(volume * 100)}%)"
                            )
                        except Exception:
                            pass
            else:
                potential_bonk_time = current_time

        # Update performance metrics every block (cheap checks)
        if performance_tracking:
            # Update peak RAM
            mem = psutil.Process().memory_info().rss / (1024 * 1024)
            if mem > performance_peak_ram:
                performance_peak_ram = mem

    # OPT-7: Silent crash recovery - wrap audio stream in retry loop
    while True:  # Keep retrying on failure
        try:
            with sd.InputStream(
                device=target_device_index,
                samplerate=SAMPLE_RATE,
                blocksize=BLOCK_SIZE,
                channels=1,
                callback=process_audio,
            ):
                log_output("[STEP 1] Engine ready.")
                setup_tray_and_run()
                # If we reach here, the stream ended normally (user quit)
                break
        except Exception as e:
            error_msg = f"[ERROR] Mic lost — retrying in 3s"
            log_output(error_msg)
            # Wait 3 seconds before retrying
            time.sleep(3)
            # Continue loop to retry

    # Performance tracking report (outside the retry loop)
    if performance_tracking:
        session_duration = time.time() - performance_start_time

        log_output("\n[PERF] === BONKWIN PERFORMANCE REPORT ===")
        log_output(f"[PERF] Session duration: {session_duration:.1f} seconds")
        log_output(f"[PERF] Peak RAM usage: {performance_peak_ram:.2f} MB")
        log_output(f"[PERF] False triggers (single spikes): {false_trigger_count}")
        log_output(f"[PERF] Successful knocks (double hits): {successful_knock_count}")
        log_output("[PERF] ==================================\n")

    if sound_enabled:
        pygame.mixer.quit()


if __name__ == "__main__":
    main()
