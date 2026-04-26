# TantuSpank Competitor Analysis & Feature Gap Report

**Date:** 2026-04-21  
**Version:** 1.0.0  
**Analyst:** AI Assistant

---

## Executive Summary

TantuSpank is a unique Windows tray application that detects physical knocks via microphone FFT analysis and plays sound effects. It occupies a niche between soundboard apps and physical interaction tools. This analysis identifies **12 potential features** across competitors, with **prioritized recommendations** for implementation.

---

## Current Feature Matrix

| Feature | TantuSpank | Soundplant | Soundpad | Stream Deck | KnockKnock |
|---------|:----------:|:----------:|:--------:|:-----------:|:----------:|
| Physical Trigger (Knock Detection) | ? | ? | ? | ? | ? |
| Hotkey Trigger | ? | ? | ? | ? | ? |
| FFT Audio Analysis | ? | ? | ? | ? | ? |
| Sound Packs/Multiple Banks | ? | ? | ? | ? | ? |
| Visual Overlay Effects | ? | ? | ? | ? | ? |
| Statistics/Analytics | ? | ? | ? | ? | ? |
| Custom Sound Import | ? | ? | ? | ? | ? |
| Volume Normalization | ? | ? | ? | ? | ? |
| Recording Capability | ? | ? | ? | ? | ? |
| MIDI Support | ? | ? | ? | ? | ? |
| Plugin/Extension System | ? | ? | ? | ? | ? |
| Multi-Monitor Support | Partial | ? | ? | ? | ? |
| Mobile App/Remote | ? | ? | ? | ? | ? |
| Cloud Sync | ? | ? | ? | ? | ? |
| Social Sharing | ? | ? | ? | ? | ? |
| Scheduling/Timers | ? | ? | ? | ? | ? |
| Accessibility Features | ? | ? | ? | ? | ? |

---

## Immediate Priorities (Implement Now)

### 1. Hotkey Fallback System
**Effort:** Low-Medium | **Impact:** High  
Allow triggering sounds via keyboard when mic detection fails or in quiet environments.
- Configurable hotkeys per sound pack
- Global hotkeys (work even when app not focused)
- Visual overlay showing hotkey assignments

**Why:** Removes single point of failure, increases accessibility

### 2. Volume Normalization
**Effort:** Low | **Impact:** Medium  
Analyze and normalize all sounds to same perceived loudness (LUFS or RMS).
- Auto-normalize on pack load
- Per-sound gain adjustment in settings
- Prevent ear-rape from poorly mastered samples

**Why:** User experience - consistent volume prevents jarring jumps

---

## Future Plans (v1.2+)

The following features are identified as valuable but deferred to future releases:

### 2. Knock Pattern Recognition
**Effort:** High | **Impact:** High | **Target:** v1.2+  
Detect specific knock patterns (Shave and a Haircut, SOS, etc.) and trigger different actions.
- Pattern training mode
- 3-5 built-in patterns
- Custom pattern creation
- Different actions per pattern (sound A vs sound B)

**Why:** Core differentiator, unique to physical trigger apps

### 3. OBS/Streaming Integration
**Effort:** Medium | **Impact:** Medium | **Target:** v1.2+  
Send knock events to OBS as sources/triggers.
- OBS WebSocket integration
- On-screen knock counter for streams
- Trigger scene changes on knock
- Chat bot integration (announce knock count)

**Why:** Streamers are ideal demographic (interactive content)

### 6. Multi-Action Chains
**Effort:** Medium | **Impact:** Medium | **Target:** v1.2+  
Allow sounds to trigger additional effects simultaneously.
- Sound + Screen Flash
- Sound + Notification Toast
- Sound + Webhook/API call
- Sound + Execute script/program

**Why:** Power user feature, opens automation possibilities

---

## Other Features (Nice to Have)

### Recording & Sound Creator
**Effort:** Medium | **Impact:** Low-Medium  
Record custom sounds directly in app.
- One-click record from mic
- Basic trim/crop
- Save to custom pack
- Voice effects (pitch shift, robot)

### Sound Pack Categories/Tags
**Effort:** Low | **Impact:** Low  
Organize sounds with metadata.
- Tags: Funny, Scary, Game, Meme, etc.
- Filter by tag
- Search sounds
- Recently played

### Accessibility Features
**Effort:** Medium | **Impact:** Medium  
Make app usable for more people.
- Visual knock indicator (for deaf/hard-of-hearing)
- High contrast mode
- Screen reader support
- Keyboard-only navigation

---

## Quick Wins (Can Implement Today)

1. **Volume normalization** - 2-3 lines with pydub or manual RMS calculation
2. **Hotkey support** - Use keyboard library (pynput or keyboard)
3. **Sound pack search/filter** - Simple text filter on existing menu
4. **Export stats** - Add "Export to CSV" button
5. **Dark mode tray icon** - Alternative icon for light taskbars

---

## Recommended Roadmap

### v1.1 (Immediate - Stability & Polish)
- [x] Volume normalization
- [x] Hotkey fallback
- [ ] Bug fixes and performance
- [ ] Sound pack search
- [ ] Export stats

### v1.2 (Future Plans)
- [ ] Knock pattern recognition
- [ ] OBS integration
- [ ] Multi-action chains
- [ ] Recording feature

### v1.3 (Expansion)
- [ ] Full pattern recognition
- [ ] Accessibility features
- [ ] Plugin API (experimental)

### v2.0 (Platform)
- [ ] Plugin marketplace
- [ ] Community hub
- [ ] Cloud sync (optional account)
- [ ] macOS/Linux ports

---

## Conclusion

**TantuSpank has strong differentiation** with its FFT-based knock detection. The app is feature-complete for its core use case but has room to grow into a **physical trigger platform**.

**Current Priority:**
1. **Hotkey fallback** - Remove single point of failure
2. **Volume normalization** - User experience polish

**Future Priorities:**
3. **Pattern recognition** - Core differentiator expansion  
4. **OBS integration** - Capture streamer market
5. **Multi-action chains** - Automation platform

**Verdict:** ? Worth updating - unique market position with clear growth path

---

*Analysis generated for TantuSpank v1.0.0*
