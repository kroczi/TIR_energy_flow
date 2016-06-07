# -*- coding: utf-8 -*-
# Copyright (c) 2009 Darwin M. Bautista
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import ConfigParser
import signal
import sys
from PyQt4 import QtCore, QtGui

import interface
import router


def main():
    app = QtGui.QApplication(sys.argv)

    if len(sys.argv) != 2:
        sys.exit(1)

    configfile = sys.argv[1]
    cfg = ConfigParser.SafeConfigParser()
    try:
        cfg.read(str(configfile))
    except ConfigParser.MissingSectionHeaderError:
        print('MissingSectionHeaderError')
        sys.exit(app.quit())

    hostname = cfg.get('Router', 'hostname')
    demand = int(cfg.get('Router', 'demand'))
    rrouter = router.Router(hostname, demand)

    links = [i for i in cfg.sections() if i.startswith('Link')]
    for link in links:
        link_id = cfg.get(link, 'link')
        cost = int(cfg.get(link, 'cost'))
        capacity = int(cfg.get(link, 'capacity'))
        rrouter.add_link(link_id, cost, capacity)

    router_timer = QtCore.QTimer()
    QtCore.QObject.connect(router_timer, QtCore.SIGNAL('timeout()'), interface.poll)
    router_timer.start(500)
    rrouter.start()
    signal.signal(signal.SIGTERM, lambda s, f: app.exit())
    signal.signal(signal.SIGINT, lambda s, f: app.exit())
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

# TODO: Prepare presentation graph with node configurations, breakdown and graph elements addition scenarios.
