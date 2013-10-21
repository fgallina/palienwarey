# -*- coding: utf-8 -*-
from .defines import (
    MODE_VERSION_2, defregister_machine, defzone)


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
