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

import argparse

import interface
import router
from timer import Timer


def main():
    args = parse_args()

    if not args.logs:
        router.disable_log()

    rrouter = router.Router()
    rrouter.init_router(args.confOrName, args.demand)

    router_timer = Timer(1, interface.poll)
    router_timer.start()
    rrouter.start()

    if args.interactive:
        from generator import InputThread
        InputThread(rrouter).start()


def parse_args():
    parser = argparse.ArgumentParser(description='Smart grid control module')

    name_or_config = parser.add_mutually_exclusive_group(required=True)
    name_or_config.add_argument('-c', '--config', dest='confOrName')
    name_or_config.add_argument('-n', '--name', dest='confOrName')

    parser.add_argument('-d', '--demand', type=int, dest='demand', default=0)
    parser.add_argument('-I', dest='interactive', action='store_false', default=True)
    parser.add_argument('-L', dest='logs', action='store_false', default=True)

    return parser.parse_args()


if __name__ == '__main__':
    main()
