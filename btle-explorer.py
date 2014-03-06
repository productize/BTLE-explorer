#!/usr/bin/env python
#
# (c) 2014 Joost Yervante Damad <joost@productize.be>

import sys

def cli_main():
  if sys.argv[1] == 'collect':
    import collect
    collect.run()
    

if __name__ == '__main__':
  if len(sys.argv) == 1:
    import gui
    sys.exit(gui.main())
  else:
    cli_main()
