# Patlite UDP Tower Light (Custom Integration for Home Assistant)

![Patlite Logo](https://raw.githubusercontent.com/<your_github>/patlite/main/logo.png)

A custom Home Assistant integration to control [Patlite](https://www.patlite.com/) network tower lights over UDP.
This integration lets you switch tiers on/off, pick colors, enable flashing, and control buzzer patterns — all from Home Assistant.

---

## ✨ Features
- Control up to **5 tiers** of the Patlite tower
- Choose from **9 colors** (Red, Amber, Lemon, Green, Sky Blue, Blue, Purple, Pink, White)
- Per-tier **on/off control** (as lights)
- Per-tier **color selection** (as selects)
- **Flash switch**
- **Buzzer control**
- Fully local: no cloud required
- Works with **automations, scripts, dashboards, and voice assistants**

---

## 📦 Installation

### Via HACS (Recommended)
1. Open HACS → Integrations → Menu (⋮) → **Custom Repositories**
2. Add this repository URL:
   ```
   https://github.com/xj42/patlite
   ```
   Category: `Integration`
3. Find **Patlite** in HACS and install.
4. Restart Home Assistant.

### Manual
1. Copy `custom_components/patlite/` to your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.

---

## ⚙️ Configuration

1. In Home Assistant, go to **Settings → Devices & Services → Integrations**.
2. Click **+ Add Integration** and search for **Patlite**.
3. Enter the **host/IP address** and **port** of your Patlite tower light.
   - Default port: `10000`
4. Done! Entities will be created:
   - `light.patlite_tier_1` … `light.patlite_tier_5`
   - `select.patlite_tier_X_color`
   - `switch.patlite_flash`
   - `switch.patlite_buzzer`

---

## 🖥️ Usage Examples

### Lovelace Dashboard

```yaml
type: picture-glance
title: Patlite Tower
image: /local/tower.gif   # place your tower.gif in config/www/
entities:
  - light.patlite_tier_1
  - select.patlite_tier_1_color
  - switch.patlite_flash
  - switch.patlite_buzzer
```

### Automation Example

```yaml
alias: Alert on Motion
trigger:
  - platform: state
    entity_id: binary_sensor.motion_hallway
    to: "on"
action:
  - service: light.turn_on
    target:
      entity_id: light.patlite_tier_1
  - service: select.select_option
    target:
      entity_id: select.patlite_tier_1_color
    data:
      option: Red
  - service: switch.turn_on
    target:
      entity_id: switch.patlite_buzzer
```

---

## 🚧 Limitations
- **Integration logos/icons** on the Devices & Services tile use HA’s [brands repo](https://github.com/home-assistant/brands). Custom logos work in dashboards (`/local/logo.png`) but won’t appear in the tile unless merged into brands.
- Tested on firmware supporting **UDP “Detailed Motion Control”** (AB D 00 00 07 …).

---

## 🙌 Credits
- Built by [xj42](https://github.com/xj42)
- Inspired by community discussions around Patlite UDP integration

---

## 🛠️ Support
For issues, feature requests, or contributions, please open an [issue](https://github.com/<your_github>/patlite/issues).
