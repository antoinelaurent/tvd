#!/usr/bin/env python
# encoding: utf-8

#
# The MIT License (MIT)
#
# Copyright (c) 2013-2014 CNRS (Hervé BREDIN -- http://herve.niderb.fr/)
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
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


from collections import namedtuple


class Episode(namedtuple('Episode', ['series', 'season', 'episode'])):
    """
    Parameters
    ----------
    series : str
    season : int
    episode : int
    """

    def __new__(cls, series, season, episode):
        return super(Episode, cls).__new__(cls, series, season, episode)

    def __str__(self):
        return '%s.Season%02d.Episode%02d' % (
            self.series, self.season, self.episode)

    def for_json(self):
        """
        Usage
        -----
        >>> import simplejson as json
        >>> episode = Episode('GameOfThrones', 1, 1)
        >>> json.dumps(episode, for_json=True)
        """
        return {
            '__E__': self.episode,
            'series': self.series,
            'season': self.season,
        }

    @classmethod
    def _from_json(cls, d):
        """
        Usage
        -----
        >>> import simplejson as json
        >>> from tvd.core.io import object_hook
        >>> with open('episodegraph.json', 'r') as f:
        ...   episode = json.load(f, object_hook=object_hook)
        """
        return cls(series=d['series'], season=d['season'], episode=d['__E__'])
