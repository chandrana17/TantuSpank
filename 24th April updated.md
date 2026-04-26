# TantuSpank Update Log - 24th April 2026

## Summary of Changes
Added USB/audio device connection sound feature to TantuSpank.

## Detailed Implementation

### 1. New Sound Pack Created
- Created folder: `sound-packs/device_connect/`
- Added manifest: `sound-packs/device_connect/pack-manifest.json`
  ```json
  {
    "id": "device_connect",
    "name": "Device Connect",
    "description": "Sounds for USB/audio device connections",
    "adult": false,
    "warning": null
  }
  ```

### 2. Device Monitoring System
- Added device monitoring thread that polls audio devices every 2 seconds
- Detects when new audio input devices are connected
- Plays a random sound from the device_connect pack when a device is connected
- Uses existing sounddevice dependency for device enumeration

### 3. Configuration Updates
- Added new config option: `"device_connect_enabled": false` to DEFAULT_CONFIG in constants.py
- User can toggle this feature via system tray menu

### 4. User Interface Changes
- Added menu item: "Device Connect Sounds" under Settings menu
- Menu item toggles the device connect feature on/off
- Shows current state with checkmark when enabled

### 5. Core Functions Added
- `get_current_audio_devices()`: Retrieves set of connected audio input devices
- `load_device_connect_pack()`: Loads and caches device connect sounds
- `play_device_connect_sound()`: Plays a random device connect sound
- `monitor_device_changes()`: Background thread that detects device connections
- `on_toggle_device_connect()`: Handles menu toggle action
- `is_device_connect_enabled()`: Checks if feature is enabled

### 6. Code Integration
- Modified detect.py to:
  - Add device monitoring state variables
  - Initialize device monitoring thread during startup
  - Add device connect menu item to settings
  - Load device connect sound pack during initialization
  - Added device connect feature functions

## Files Modified
1. `constants.py` - Added device_connect_enabled to DEFAULT_CONFIG
2. `detect.py` - Major modifications including:
   - Added device monitoring state variables (lines 90-98)
   - Added device monitoring functions (lines 218-328)
   - Added menu item and toggle functions (lines 1230-1242)
   - Updated initialization sequence (lines 1840-1851)
   - Added device connect menu item to Settings (line 1753)

## How to Use
1. Place .mp3, .wav, or .ogg files in `sound-packs/device_connect/`
2. Enable "Device Connect Sounds" from the TantuSpank tray menu under Settings
3. When you connect a USB microphone, headphones, or other audio input device, a sound will play
4. Disable the feature anytime from the same menu

## Notes
- The feature only triggers on device connection (not disconnection) to avoid excessive sounds
- Uses the same audio playback system as knock detection for consistency
- Respects the global volume settings
- Runs as a low-priority background thread with minimal CPU usage
- Automatically detects the device_connect sound pack if present

## Testing
- Verified syntax compiles without errors
- Confirmed app starts successfully with device monitoring active
- Confirmed device_connect pack is detected in pack registry (shows 8 total packs vs previous 7)
- Core knock detection functionality remains intact

## Future Improvements
- Add option to play disconnect sounds
- Implement full rotation shuffle for device sounds (like regular packs)
- Add volume slider specifically for device connect sounds
- Allow custom device connect sound selection