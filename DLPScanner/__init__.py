#!/usr/bin/env python
# Entry point for structured light programming application
# Matthew Kroesche
# ECEN 403-404

from DLPScanner.master import Master

if __name__ == '__main__':
    app = Master()
    app.init()
    try:
        app.run()
    finally:
        app.quit()
