# Grenobj #

At some point in your life, you will have written enough shitty value objects by hand.
For me, this point was tonight, so *Grenobj* was born. It will be a simple commandline
utility which eats JSON and shits code for Objective-C value objects. 

You will need a configuration file *~/.grenobj* with contents like this:

    [grenobj]
    author = John Appleseed
    prefix = AAPL

where *author* is your name (used for the code comments) and prefix is prepended to 
all class names.

---

Boris Bügling <boris@icculus.org>
