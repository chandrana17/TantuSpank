# BonkWin 🔨

**Bonk your laptop. It bonks back. Works on ANY Windows laptop.**

BonkWin is a lightweight Windows system tray utility that transforms your laptop into an interactive, audio-reactive device. It listens for physical knocks, taps, or thuds on your laptop chassis or desk and responds with satisfying sound effects. No special hardware required—just your built-in microphone and a bit of FFT magic.

---

## ✨ Features

- 🎤 **Smart Detection** — Advanced FFT filtering isolates physical impacts from speech and background noise.
- 🔊 **Sound Packs** — Swap between built-in packs (Default, Retro, Nature) or add your own .wav files.
- ⚡ **0% Idle CPU** — Optimized RMS pre-filtering ensures the detection engine sleeps when you're silent.
- 📊 **Bonk Counter** — Persistent tracking of your lifetime "bonks" with milestone stats.
- 🚀 **Auto-Start** — One-click toggle from the tray to launch at Windows startup.
- 🖥️ **System Tray** — Lives quietly in your taskbar with a polished hammer icon—right-click to manage everything.

---

## 🚀 Installation

1. Go to the [Releases](https://github.com/chandrana17/BonkWin/releases) page.
2. Download and run `BonkWin_Setup.exe`.
3. BonkWin will appear in your system tray. Give your desk a solid knock to test!

---

## 🧠 How It Works

BonkWin uses real-time digital signal processing (DSP) to distinguish physical shocks from airborne sound:
- **Low-Pass Filtering**: Isolates frequencies below 300Hz (where thuds live).
- **Double-Hit Confirmation**: Prevents false triggers from single sharp noises like keyboard clicks.
- **Adaptive Baseline**: Maintains a rolling 2-second ambient noise average to maintain sensitivity in different environments.
- **Silent Crash Recovery**: Automatically reconnects to the microphone if the input is lost or the system wakes from sleep.

---

## 📂 Sound Packs

Swap packs via the tray menu to change the vibe:
- `pack_default`: Classic percussion thuds.
- `pack_retro`: 8-bit style arcade bleeps.
- `pack_nature`: Organic wood and stone impact sounds.

**Custom Sounds**: Add your own `.wav` files to the `sounds/` directory in the installation folder, and they will appear in the switcher instantly.

---

## 🤝 Contributing

Contributions are welcome! If you have optimized detection algorithms or new sound packs, feel free to open a Pull Request.

---

## 📄 License

This project is licensed under the **MIT License**.

---

**Made with 🔨 and way too many desk knocks.**
