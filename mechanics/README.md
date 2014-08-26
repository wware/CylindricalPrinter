Mechanics for the cylindrical printer
==

I'm not a mechanical genius and I'm a laughably bad craftsman. An important
design goal of this set of mechanics is that anybody should be able to build it
without being a highly skilled craftsperson. So there are very few critical
tolerances, hopefully none more exacting than 1/16", and most of them much
less exacting. Wherever possible I've used the commonest, cheapest, most
widely-available parts I could find.

Just so you know what you're trying to build, here is a picture. The orange
thing is a five-gallon bucket from Home Depot.

![One picture of the printer](https://raw.githubusercontent.com/wware/CylindricalPrinter/master/mechanics/printer_1.png)

![Another picture of the printer](https://raw.githubusercontent.com/wware/CylindricalPrinter/master/mechanics/printer_2.png)

Sprockets and bike chain
--

The drive chain of the printer uses 1/2"-1/8" single-speed bicycle chain and
four [3d-printed sprockets](http://www.thingiverse.com/thing:426854). To build
this printer you will need these sprockets. If you have a friend with a 3d
printer, they can print them for you. Otherwise you can go to a service bureau
such as Shapeways or Sculpteo. Once your printer is built, you can print
sprockets (and maybe other parts) for yourself and other people.

Plywood pieces
--

I began this project with an enthusiasm to do a lot of laser cutting of plywood.
I learned that laser cutters are hard to find, finicky, and unreliable. The
plywood pieces are therefore made with a jig saw and hand drill (or a drill
press if you have one) from a template that is printed on paper. Use 1/4"
plywood. You should be able to make all the pieces with one or two 24"x24"
sheets from Home Depot.

So if you're nervous about getting it right, take a slow deep breath and
remember this isn't rocket surgery. Even if you totally mess up the first time,
it's only about ten bucks worth of plywood.

Remember that thing about commonest cheapest most widely-available? On the paper
template I may have fallen short of that ambition. I am ending up getting the
pattern printed on a
[large-format black-and-white printer at Staples](http://documents.staples.com/ASP1/CATEGORIES/SKU/oversizedprints.aspx).
If you don't have a Staples or something equivalent locally available, they can
probably print you a template via mail order or online order. Either way,
remember that they need to *enlarge the template by a factor of three*. I made
it small enough to fit on a sheet of paper so that I could do the `ps2pdf`
conversion.

I simply cannot get my hands on a large-format printer
--

Do this instead. On the last line of template.ps, replace "singleBigSheet" with
"overlappingSeparatePages" and then run

```bash
ps2pdf template.ps template.pdf
```

The resulting PDF is a six-page template on 8.5"x11" sheets, and after printing
them you'll need to line up the registration marks (circles with X's in them)
as you tape them all together. Use a light table if you can find one, otherwise
hold them against a sunny window. I've done it, it's a pain, it's well worth
your time to hunt up a large-format printer if humanly possible.
