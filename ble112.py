#!/usr/bin/env python

import sys

def cli_main():
  if sys.argv[1] == 'collect':
    import collect
    collect.run()
    

if __name__ == '__main__':
  if len(sys.argv) == 1:
    sys.exit(gui.main())
  else:
    cli_main()
