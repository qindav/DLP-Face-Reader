#!/usr/bin/env python
# Structured light programming application
# Matthew Kroesche
# ECEN 403

from ecen403.master import Master

if __name__ == '__main__':
    app = Master()
    app.init()
    try:
        app.run()
    finally:
        app.quit()
