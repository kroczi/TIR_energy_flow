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

import signal
import sys
from PyQt4 import QtCore, QtGui

import interface
import router
from generator import EventGenerator, InputThread
from plotter import Plotter


def main():
    if len(sys.argv) < 2:
        print('You must pass path to the config file or hostname [with demand].')
        sys.exit(1)

    app = QtGui.QApplication(sys.argv)

    plotter = Plotter()
    demand = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    rrouter = router.Router(on_graph_recalculated=lambda g: plotter.updateGraph(g))
    rrouter.configure(sys.argv[1], demand)

    router_timer = QtCore.QTimer()
    QtCore.QObject.connect(router_timer, QtCore.SIGNAL('timeout()'), interface.poll)
    router_timer.start(500)
    signal.signal(signal.SIGTERM, lambda s, f: app.exit())
    signal.signal(signal.SIGINT, lambda s, f: app.exit())

    rrouter.start()
    plotter.start()
    InputThread(EventGenerator(rrouter)).start()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

# TODO: Prepare presentation graph with node configurations, breakdown and graph elements addition scenarios.
