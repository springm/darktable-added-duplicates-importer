# darktable-added-duplicates-importer
Add image duplicates not present in library.db to darktable

## Basic principles
Darktable keeps a database, ~/.config/darktable/library.db, where all imported images and their settings are registered. If configured accordingly, for each (processed) image, also a sidecar file with the suffix .xmp is written next to the image file itself.

If all editing work is done on only one computer, the number of image records is higher (because it contains imported but not processed images) or equal to the number of .xmp files for a given directory.

## Working on multiple computers
The foreseen darktable mechanism to have local copies of image files on the secondary computer does not work for me, as I use my computers alternatingly, with the laptop having only a subset of the images, but when travelling getting all the imports.

Synchronising the computer's image directories with syncthing or rsync helps, and darktable discovers changed .xmp files during startup (if configured that way, again)

If you create a new version of a already registered file however on one computer, the database does not get updated, i.e. on the second computer, this new version remains unknown.

# The added duplicates importer
For a directory given as command line argument, the script iterates over all images in the directory, counts their versions and compares this with the number of versions in the database. 

If there are more .xmp versions, at the end of the discovery darktable is called with the xmp files as commandline argument, triggering an import and registration of these in the database.