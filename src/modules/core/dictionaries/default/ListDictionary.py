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

from ..BaseDictionary import BaseDictionary
from ....utils.utils import checkRangeList
from ....exceptions.MainExceptions import MissingParameter

class ListDictionary(BaseDictionary):
    __name__ = "ListDictionary"
    __author__ = ("Vitor Oriel C N Borges")

    def __init__(self):
        super().__init__()

    def setWordlist(self, sourceParam: str):
        sourceParam = sourceParam[1:len(sourceParam)-1]
        if not sourceParam:
            raise MissingParameter("list of elements")
        if ',' in sourceParam:
            buildedList = []
            for param in sourceParam.split(','):
                buildedList.extend(checkRangeList(param))
        else:
            buildedList = checkRangeList(sourceParam)
        self._wordlist = buildedList