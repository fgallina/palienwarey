# -*- coding: utf-8 -*-
from .defines import (
    MODE_VERSION_1, MODE_VERSION_2, defregister_machine, defzone)


# -- Start backports from pyalienfx
_m11xr1_zones = (
    defzone(0x6000, "Power Button", alias='power', is_power=True),
    defzone(0x0001, "Keyboard: Right", alias='kbd-right'),

    defzone(0x0020, "Speaker: Right", alias='speaker-right'),
    defzone(0x0040, "Speaker: Left", alias='speaker-left'),
    defzone([0x0020, 0x0040], "Speakers", alias='speakers'),

    defzone(0x0100, "Alien Name", alias='name'),
    defzone(0x0800, "Media Bar", alias='media')
)

_m15xr2_zones = (
    defzone(0x2000, "Power Button", alias='power', is_power=True),
    defzone(0x0010, "Power Button 2", alias='power2', is_power=True),
    defzone(0x4000, "Indicators", alias='indicators',
            can_morph=False, can_pulse=False),

    defzone(0x0004, "Keyboard: Left", alias='kbd-left'),
    defzone(0x0008, "Keyboard: Middle Left", alias='kbd-middle-left'),
    defzone(0x0002, "Keyboard: Middle Right", alias='kbd-middle-right'),
    defzone(0x0001, "Keyboard: Right", alias='kbd-right'),
    defzone([0x0001, 0x0002, 0x0004, 0x0008], "Keyboard", alias='kbd'),

    defzone(0x0020, "Speaker: Right", alias='speaker-right'),
    defzone(0x0040, "Speaker: Left", alias='speaker-left'),
    defzone([0x0020, 0x0040], "Speakers", alias='speakers'),

    defzone(0x0080, "Alien Logo", alias='alien'),
    defzone(0x0100, "Alien Name", alias='name'),
    defzone(0x0200, "Touchpad", alias='touchpad'),
    defzone(0x01c00, "Media Bar", alias='media')
)

defregister_machine(0x0511, "M15XArea51", (
    defzone(0x8000, "Power Button", alias='power',
            can_morph=False, can_pulse=False, is_power=True),
    defzone(0x0400, "Keyboard", alias='kbd'),
    defzone(0x0001, "Touchpad", alias='touchpad'),
    defzone(0x0020, "Lightpipe", alias='lightpipe'),
    defzone(0x0100, "Alien Logo", alias='alien'),
    defzone(0x0080, "Alien Name", alias='name'),
    defzone(0x10000, "Media Bar", alias='media')
), MODE_VERSION_2)

defregister_machine(0x0512, "M15XAllPowerful", _m15xr2_zones, MODE_VERSION_2)

defregister_machine(0x0514, "M11XR1", _m11xr1_zones, MODE_VERSION_1)

defregister_machine(0x0515, "M11XR2", _m11xr1_zones, MODE_VERSION_1)

defregister_machine(0x0516, "M11XR25", _m11xr1_zones, MODE_VERSION_1)

defregister_machine(0x0518, "M18XR2", _m15xr2_zones, MODE_VERSION_1)

defregister_machine(0x0520, "M17XR3", _m15xr2_zones, MODE_VERSION_2)

defregister_machine(0x0521, "M14XR1", _m15xr2_zones, MODE_VERSION_2)

defregister_machine(0x0522, "M11XR3", _m11xr1_zones, MODE_VERSION_1)
# -- End backports from pyalienfx

defregister_machine(0x0525, "Alienware 14 2013", (
    defzone(0x2000, "Power Button", alias='power', is_power=True),

    defzone(0x0001, "Keyboard: Left", alias='kbd-left'),
    defzone(0x0002, "Keyboard: Middle Left", alias='kbd-middle-left'),
    defzone(0x0004, "Keyboard: Middle Right", alias='kbd-middle-right'),
    defzone(0x0008, "Keyboard: Right", alias='kbd-right'),
    defzone([0x0002, 0x0004], "Keyboard Middle", alias='kbd-middle'),
    defzone([0x0001, 0x0002, 0x0004, 0x0008], "Keyboard", alias='kbd'),

    defzone(0x0020, "Side: Left", alias='side-left'),
    defzone(0x0040, "Side: Right", alias='side-right'),
    defzone([0x0020, 0x0040], "Sides", alias='sides'),

    defzone(0x0080, "Alien Logo and Lid Stripes", alias='alien'),
    defzone(0x0100, "Alien Name", alias='name'),
    defzone(0x0200, "Touchpad", alias='touchpad'),

    defzone(0x0800, "Wifi Led", alias='wifi'),
    defzone(0x4000, "HD Led", alias='hd'),
    defzone([0x0800, 0x4000], "Indicators", alias='indicators'),
), MODE_VERSION_2)
