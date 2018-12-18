#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Arturo Busleiman <buanzo@buanzo.com.ar>
# This is a zmq streamer device tasked
# with receiving job execution requests
# from Ronald.
#
# The code is too simple to make use of a
# class, but refactoring might happen.
# With that in mind, I rather design the
# class later on.

import zmq
import time


def main():
    try:
        context = zmq.Context(1)
    except Exception:
        print("Dispatcher: Cant obtain ZMQ Context")
        return

    try:
        # Jobs API will send messages to this socket:
        frontend = context.socket(zmq.PULL)
        frontend.bind("tcp://*:5559")
    except Exception:
        print("Dispatcher: cant bind frontend socket")
        return

    try:
        # Socket facing workers. Workers connect to this
        # Streamer balances what pushers (jobs api) send among them.
        backend = context.socket(zmq.PUSH)
        backend.bind("tcp://*:5560")
    except Exception:
        print("Dispatcher: cant bind backend socket")
        return

    try:
        # Let's start this streamer device:
        print("Dispatcher: Starting ZMQ Device...")
        zmq.device(zmq.STREAMER, frontend, backend)

    except Exception:  # TODO: add error variable
        print("Bringing Streamer down. Will restart.")

    finally:
        print("Dispatcher: Finishing")
        frontend.close()
        backend.close()
        context.term()


if __name__ == "__main__":
    try:
        while True:
            main()
            print("Dispatcher: main() exited. Should not happen.")
            print("Waiting for five seconds for main() restart")
            time.sleep(5)
            print("Restarting...")
    except KeyboardInterrupt:
        print("\nCTRL-C. Exiting...")
