## FuzzingTool
# 
# Authors:
#    Vitor Oriel C N Borges <https://github.com/VitorOriel>
# License: MIT (LICENSE.md)
#    Copyright (c) 2021 Vitor Oriel
#    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#    The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
## https://github.com/NESCAU-UFLA/FuzzingTool

from .Payloader import Payloader
from .scanners import *
from ..conn.Request import Request
from ..IO.OutputHandler import outputHandler as oh
from ..IO.FileHandler import fileHandler as fh
from ..exceptions.RequestExceptions import RequestException, InvalidHostname

from threading import Thread, Event, Semaphore
import time

class Fuzzer:
    """Fuzzer class, the core of the software
    
    Attributes:
        requester: The requester object to deal with the requests
        delay: The delay between each test
        verboseMode: The verbose mode flag
        numberOfThreads: The number of threads used in the application
        output: The output content to be send to the file
        dictSizeof: The number of payloads in the payload file
        scanner: A scanner object, used to validate the results
        payloader: The payloader object to handle with the payloads
    """
    def __init__(self,
        requester: Request,
        payloader: Payloader,
        scanner: BaseScanner,
        delay: float,
        numberOfThreads: int,
        resultCallback,
        errorCallbacks: list
    ):
        """Class constructor

        @type requester: requester
        @param requester: The requester object to deal with the requests
        @type payloader: Payloader
        @param payloader: The payloader object to deal with the payload dictionary
        """
        self.__requester = requester
        self.__delay = delay
        self.__numberOfThreads = numberOfThreads
        self.__scanner = scanner
        self.__payloader = payloader
        self.resultCallback = resultCallback
        self.errorCallbacks = errorCallbacks

    def isRunning(self):
        """The running flag getter

        @returns bool: The running flag
        """
        return self.__running

    def threadHandle(self, action: str):
        """Function that handle with all of the threads functions and atributes

        @type action: str
        @param action: The action taken by the thread handler
        @returns func: A thread function
        """
        def run():
            """Run the threads"""
            while self.__running and not self.__payloader.isEmpty():
                payload = self.__payloader.get()
                try:
                    for p in payload:
                        try:
                            result = self.__scanner.getResult(
                                response=self.__requester.request(p)
                            )
                            self.resultCallback(result, self.__scanner.scan(result))
                            time.sleep(self.__delay)
                        except InvalidHostname as e:
                            self.errorCallbacks[0](e)
                        except RequestException as e:
                            self.errorCallbacks[1](e)
                finally:
                    if not self.__playerHandler.isSet():
                        self.__numberOfThreads -= 1
                        self.__semaphoreHandler.release()

        def start():
            """Handle with threads start"""
            self.__playerHandler.set() # Awake threads
            for thread in self.__threads:
                thread.start()
            for thread in self.__threads:
                thread.join()

        def stop():
            """Handle with threads stop"""
            self.__running = False
            self.__playerHandler.clear()

        def setup():
            """Handle with threads setup
            
            New Fuzzer Attributes:
                threads: The list with the threads used in the application
                running: A flag to say if the application is running or not
                playerHandler: The Event object handler - an internal flag manager for the threads
                semaphoreHandler: The Semaphore object handler - an internal counter manager for the threads
            """
            self.__threads = []
            self.__running = True
            for i in range(self.__numberOfThreads):
                self.__threads.append(Thread(target=run, daemon=True))
            self.__playerHandler = Event()
            self.__semaphoreHandler = Semaphore(0)
            self.__playerHandler.clear() # Not necessary, but force the blocking of the threads
        
        if action == 'setup': return setup()
        elif action == 'start': return start()
        elif action == 'stop': return stop()

    def start(self):
        """Starts the fuzzer application"""
        self.threadHandle('setup')
        self.threadHandle('start')

    def stop(self):
        """Stop the fuzzer application"""
        self.threadHandle('stop')
        while self.__numberOfThreads > 1:
            pass
        time.sleep(0.1)