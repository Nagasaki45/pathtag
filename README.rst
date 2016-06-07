pathtag
=======

.. image:: https://travis-ci.org/Nagasaki45/pathtag.svg?branch=master
    :target: https://travis-ci.org/Nagasaki45/pathtag

.. image:: https://badge.fury.io/py/pathtag.svg
    :target: https://badge.fury.io/py/pathtag

Your music is carefully organized into folders but your MP3 player insist on browsing (and playing) your music by its metadata information?

Use this script to override the 'Artist' and 'Album' information with data extracted from the file paths.

Usage
-----

.. code:: bash

  python pathtag.py basedir

Suppose you got something like this in your ``basedir``:

.. code:: bash

  Beatles/Revolver/Taxman.mp3

``Taxman.mp3`` will be overridden with Artist='Beatles' and Album='Revolver'

In addition:

- Files in paths as ``Beatles/Yesterday.mp3`` will be overridden with Artist='Beatles' and Album='Unknown'.
- Files in any other path structure will not be affected.
- Files without ID3v2 header will not be affected either (don't worry about your album covers etc.).
