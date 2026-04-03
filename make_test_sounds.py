import os
import numpy as np
import wave


def generate_tone(frequency, duration, sample_rate=44100):
    """Generate a short percussive tone with exponential decay envelope"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # Generate sine wave
    wave_signal = np.sin(frequency * 2 * np.pi * t)
    # Create punchy exponential decay envelope
    envelope = np.exp(-t * 15)  # Decay factor for punchy sound
    # Apply envelope
    signal = wave_signal * envelope
    # Normalize to 16-bit range
    signal = signal * 0.3 * 32767  # Reduce volume to avoid clipping
    return signal.astype(np.int16)


def save_wav(filename, data, sample_rate=44100):
    """Save numpy array as WAV file"""
    with wave.open(filename, "w") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(data.tobytes())


def main():
    sample_rate = 44100

    # Define sound packs with different characteristics
    packs = {
        "pack_default": [
            ("low_thud.wav", 80, 0.3),  # 80 Hz, 300ms
            ("mid_bonk.wav", 220, 0.2),  # 220 Hz, 200ms
            ("high_tap.wav", 800, 0.1),  # 800 Hz, 100ms
        ],
        "pack_retro": [
            ("retro_blip.wav", 440, 0.15),  # 440 Hz, 150ms - classic blip
            ("retro_beep.wav", 880, 0.1),  # 880 Hz, 100ms - higher beep
            ("retro_boop.wav", 220, 0.25),  # 220 Hz, 250ms - low boop
        ],
        "pack_nature": [
            ("wood_knock.wav", 150, 0.2),  # 150 Hz, 200ms - wooden knock
            ("stone_tap.wav", 600, 0.08),  # 600 Hz, 80ms - sharp stone tap
            ("deep_thump.wav", 60, 0.4),  # 60 Hz, 400ms - deep thump
        ],
    }

    for pack_name, sounds in packs.items():
        sounds_dir = os.path.join(os.path.dirname(__file__), "sounds", pack_name)
        os.makedirs(sounds_dir, exist_ok=True)

        for filename, freq, duration in sounds:
            print(f"Generating {pack_name}/{filename}...")
            tone = generate_tone(freq, duration, sample_rate)
            filepath = os.path.join(sounds_dir, filename)
            save_wav(filepath, tone, sample_rate)
            print(f"Saved {filepath}")

    print("Test sound generation complete for all packs!")


if __name__ == "__main__":
    main()
