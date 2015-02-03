Cylindrical Printer
====

The early ugly prototype was built during June and July 2014 and was the one on which I made my
first successful 3D print, an octohedral shape made with green SubGPlus from MakerJuice. The
layers are clearly visible because they are 1/40th of an inch (a half-rotation of a 1/4-20
threaded rod; I didn't have a working stepper motor at the time). Those layers are much less
conspicuous at 1/100th of an inch.

![Picture of octohedron](http://4.bp.blogspot.com/-_HxTxJrZhs0/U7nyiwFbxMI/AAAAAAAAHow/woSWXhDpvNo/s1600/best_yet_sunday.png)

This was my proof to myself that I had a good enough handle on the basic
principles to invest more time and energy. The design has evolved over time. I
wanted to keep it kind of steampunk-ish with lots of gears and widgets, but
still simple enough to build that it could be accomplished by a horribly bad
craftsperson like myself.

While I've been doing this, I've been blogging and occasionally posting Youtube videos.

* http://willware.blogspot.com/2014/07/homebrew-stereolithographic-3d-printer.html
* http://willware.blogspot.com/2014/07/cleaning-up-sla-printer-design.html
* http://willware.blogspot.com/2014/08/once-more-with-feeling.html
* http://willware.blogspot.com/2014/08/of-bicycle-chain-and-sprockets.html
* https://www.youtube.com/watch?v=k0KcZ39T2KY

If you decide you want to build one of these (and by all means, please feel free), you should
think of this information as a starting point. I don't have the bandwidth to offer much more
than encouragement beyond what I've posted online. Be prepared to experiment. Don't be too
surprised if it takes more time, money, and stamina than you expected. Don't get too attached
to any clever approaches to anything, you may find you need to abandon them to progress further.

Makerfaire, and Beyond the Infinite
----

I showed the printer at Makerfaire NYC 2014, and again at a mini-Makerfaire in Providence RI
a month or so later. This taught me a few things.

* Don't depend upon a laptop when you're doing a demo in a not-too-controlled environment.
  It's way too easy to spill liquids and other things on a laptop. And laptops are precious
  and difficult to replace, unlike Raspberry Pis or Arduinos.
* Don't ask a Raspberry Pi or an Arduino to slice a model into layers. That needs to be done
  by a laptop or desktop, but it can be done before the show. So you want to store those layers
  on something like a USB stick.
* That division of labor makes things really simple on the Raspberry Pi end. You want UP and
  DOWN buttons to move the build platform manually, and you want a PRINT button to do the actual
  build. Various parameters like layer exposure time and motor steps per layer can be stored
  on the USB stick, so you get flexibility without needing to change the RPi code.

These parameters can be customized to accommodate differences in electronics and hardware as
well, for instance the polarity of the stepper motor. So carefully constructed RPi code can
be used over multiple revisions of the physical hardware.
