===========
palienwarey
===========

Cross platform Alienware Leds commandline tool, driver and library.

Info
====

+ Author: Fabián Ezequiel Gallina
+ Contact: fabian at anue dot biz
+ Project homepage: https://github.com/fgallina/palienwarey/

|flattr|

Installation
============

Using pip should suffice::

    $ pip install palienwarey

Usage
=====

Besides the library, this package comes with three handy commandline tools:

+ lsd: the led software driver commandline tool.
+ lsdetect: a tool to detect led addresses on Alienware devices.
+ lsdaemon: a driver daemon intended to provide access to lsd commands to
  non-root users. The use of the daemon is a convenience and it's not
  mandatory.

The ``lsd`` command can be run either using the ``lsdaemon`` as intermediary
to talk to the Alienware lights device (this enables non-root users to send
commands to the device without the need of custom udev rules) or,
alternatively, can be used directly with no daemon, provided it has enough
priviledges.

See the ``lsd`` help for usage and examples.

lsdaemon
========

The lsdaemon has no much variants, it only needs to be run with administrative
priviledges and after that you can send commands to it::

    # lsdaemon
    INFO lsdaemon:140 Serving on: 0.0.0.0:6587 (coding utf-8)

If you saw that, you are ready to go. Check the ``--port`` and ``--host``
switches and use the ``--help`` to check what else the daemon has to offer. A
cool possibility for the daemon is not to only allow you to run ``lsd`` in
userspace but also you could remotely control your leds!

lsd
===

This is the main reason for palienware to exists, it can be run standalone
(provided it has enough priviledges to access the USB device) or send messages
to the device through the ``lsdaemon`` by adding the ``--daemon`` flag.

Depending on your machine definition the flags vary, but they should be pretty
similar. Anyhow all these examples are based on the Alienware 14 2013 model
since that's the only thing I have at hand. Check your machine specific flags
by calling the ``lsd`` command with the ``--help`` switch.

Every zone supports up to three commands: ``color`` (shorthand ``c``),
``morph`` (shorthand ``m``) and ``pulse`` (shorthand ``p``). Capabilities for
each zone are set by defzone when defining new machines.

Example 1: Set all leds to red (except power).
----------------------------------------------

The ``lsd`` command comes with a handy switch called ``--all`` to define a set
of color configurations for all zones that not groups nor power::

    # lsd --all color:ffcc00

You can also use ``c`` shorthand for the set color command::

    # lsd --all c:ffcc00

Example 2: Set a loop on the keyboard.
--------------------------------------

The keyboard is a special group zone (just like the previous ``--all``), it
might or might not have been defined for your machine. Again add ``--help``
when calling ``lsd`` to check for defined zones. If a group zone so
fundamental like this has not yet been added to your machine, please file a
bug and I'll add it (pull requests welcome)::

    # lsd --kbd morph:ffcc00:ff0000 pulse:ff0000 morph:ff0000:ffcc00 pulse:ffcc00

Example 3: Use group commands as default and override with other zones.
-----------------------------------------------------------------------

This is handy for when you want an specific configuration shared for most
zones that belong to a group but you need one or more zones in it to be
different. For this there's the ``--override-groups`` switch.

Consider this example::

    # lsd --kbd c:ffcc00 --kbd-left c:00ff00 --kbd-right c:00ff00

With this, what will happen is that all keyboard zones will be set to
``ffcc00``, but then for the left side and right side of the keyboard the
``00ff00`` color will be added as another configuration for the zone loop, so
that will render in a color switch for keyboard sides. If what you really
wanted was to provide a default configuration for the whole keyboard but set
different configurations for both sides, then the ``--override-groups`` switch
will come to help::

    # lsd --kbd c:ffcc00 --kbd-left c:00ff00 --kbd-right c:00ff00 --override-groups

Example 4: Set a led configuration for specific power modes.
------------------------------------------------------------

In this case we are saving the provided leds configuration for boot and ac,
check your machine supported modes with the handy ``--help`` switch::

    # lsd --kbd morph:ffcc00:ff0000 pulse:ff0000 morph:ff0000:ffcc00 pulse:ffcc00 --mode-boot --mode-ac --save

Example 5: My power led doesn't do anything!
--------------------------------------------

In newer models using the ``MODE_VERSION_2`` (I assume this, since the only
device I ever got my hands on is an Alienware 14 2013), it seems the power
button won't update when no specific modes has been set for commands sent to
the USB device. This means that you won't see the power button changing,
unless you set an specific power mode and you are actually using it. A tip is
to use the ``--mode-ac`` (or whatever power mode you are currently into) to
try out power button configurations and then set it properly into the mode you
really wanted::

    # Lsd --power c:ffcc00 --mode-ac # we'll set this to show when on battery

    # lsd --power c:ff0000 --mode-ac # we'll set this to shown when battery is low

Now that you tested color (or even loop) configurations and are sure of what
you would use for the different power modes available in your machines you can
now proceed and just do that::

    # lsd --power c:00ff00 --mode-ac --save # Use green when on AC Power

    # lsd --power c:ffcc00 --mode-batpower # Use orange when on Battery Power

    # lsd --power c:ff0000 --mode-batlow # Use red when Battery is Low

lsdetect
--------

The lsdetect is a really simple, interactive command that will guide you in
the process of finding your machine led addresses by going through the list of
every possible address and prompting you if something changed. The most
relevant switch for this command is the ``--color`` one (defaults to
``ffffff``).

Once you are done with all the lsdetect questions, it will print a
``defmachine`` you can add in the ``palienware.machines`` module and use as a
starting point for adding support to your device.

Supported Machines
==================

+ Alienware 14 2013
+ M11XR3
+ M14XR1
+ M17XR3
+ M18XR2
+ M11XR25
+ M11XR2
+ M11XR1
+ M15XAllPowerful
+ M15XArea51

Acknowledgements
================

+ `USBPcap <http://desowin.org/usbpcap/>`_: for the Windows USB packet capture I
  used as a start.
+ `Wireshark <http://wireshark.org>`_: for their awesome GUI for checking pcap
  files.
+ `PyAlienFX <https://code.google.com/p/pyalienfx/>`_: I used it fairly good as
  a reference for how the USB protocol was like and support for other machines
  than mine.
+ `Benjamin Thaut <http://3d.benjamin-thaut.de/?p=19>`_: for his handy AlienFX
  leds tester which inspired lsdetect and which I used to detect mine.

TODO
====

1. Cleanup and push tests.
2. Support for more machines.
3. Add support for theme files.
4. Add a configuration files for overriding defaults.
5. Handle daemon concurrency properly.

.. Flattr
.. |flattr|
   image:: http://api.flattr.com/button/flattr-badge-large.png
   :target: https://flattr.com/submit/auto?user_id=fgallina&url=https://github.com/fgallina/palienwarey&title=palienwarey&language=en_GB&tags=github&category=software
   :alt: Flattr this git repo
   :width: 93px
   :height: 20px
