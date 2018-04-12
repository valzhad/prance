# -*- coding: utf-8 -*-
"""Test suite for prance.util.url ."""

__author__ = 'Jens Finkhaeuser'
__copyright__ = 'Copyright (c) 2016-2017 Jens Finkhaeuser'
__license__ = 'MIT +no-false-attribs'
__all__ = ()

import sys

import pytest

from prance.util import url


def test_absurl_http():
  test = 'http://foo.bar/asdf/#lala/quux'
  res = url.absurl(test)
  assert res.geturl() == test


def test_absurl_http_fragment():
  base = 'http://foo.bar/asdf/#lala/quux'
  test = '#another'
  res = url.absurl(test, base)
  assert res.scheme == 'http'
  assert res.netloc == 'foo.bar'
  assert res.path == '/asdf/'
  assert res.fragment == 'another'


def test_absurl_file():
  if sys.platform == "win32":
    base = 'file:///c:/windows/notepad.exe'
    test = "regedit.exe"
    expect = 'file:///c:/windows/regedit.exe'
  else:
    base = 'file:///etc/passwd'
    test = 'group'
    expect = 'file:///etc/group'
  res = url.absurl(test, base)
  assert res.geturl() == expect


def test_absurl_absfile():
  if sys.platform == "win32":
    test = 'file:///c:/windows/notepad.exe'
  else:
    test = 'file:///etc/passwd'
  res = url.absurl(test)
  assert res.geturl() == test


def test_absurl_fragment():
  base = 'file:///etc/passwd'
  test = '#frag'
  with pytest.raises(url.ResolutionError):
    url.absurl(test)

  res = url.absurl(test, base)
  assert res.geturl() == 'file:///etc/passwd#frag'


def test_absurl_relfile():
  base = 'http://foo.bar'
  test = 'relative.file'
  with pytest.raises(url.ResolutionError):
    url.absurl(test)
  with pytest.raises(url.ResolutionError):
    url.absurl(test, base)


def test_urlresource():
  parsed = url.absurl('http://foo.bar/asdf?some=query#myfrag')
  res = url.urlresource(parsed)
  assert res == 'http://foo.bar/asdf'


def test_split_url_reference():
  base = url.absurl('http://foo.bar/')

  # Relative reference
  parsed, path = url.split_url_reference(base, '#foo/bar')
  assert parsed.netloc == 'foo.bar'
  assert len(path) == 2
  assert path[0] == 'foo'
  assert path[1] == 'bar'

  # Leading slashes are stripped
  parsed, path = url.split_url_reference(base, '#///foo/bar')
  assert parsed.netloc == 'foo.bar'
  assert len(path) == 2
  assert path[0] == 'foo'
  assert path[1] == 'bar'

  # Absolute reference
  parsed, path = url.split_url_reference(base, 'http://somewhere/#foo/bar')
  assert parsed.netloc == 'somewhere'
  assert len(path) == 2
  assert path[0] == 'foo'
  assert path[1] == 'bar'


def test_fetch_url_file():
  from prance.util import fs
  content = url.fetch_url(url.absurl(fs.abspath('tests/with_externals.yaml')))
  assert content['swagger'] == '2.0'


def test_fetch_url_cached():
  from prance.util import fs
  cache = {}

  content1 = url.fetch_url(url.absurl(fs.abspath('tests/with_externals.yaml')), cache)
  assert content1['swagger'] == '2.0'

  content2 = url.fetch_url(url.absurl(fs.abspath('tests/with_externals.yaml')), cache)
  assert content2['swagger'] == '2.0'

  assert id(content1) == id(content2)


def test_fetch_url_http():
  exturl = 'http://finkhaeuser.de/projects/prance/petstore.yaml'\
    '#/definitions/Pet'
  content = url.fetch_url(url.absurl(exturl))
  assert content['swagger'] == '2.0'


def test_fetch_url_python():
  exturl = 'python://tests/petstore.yaml'
  content = url.fetch_url(url.absurl(exturl))
  assert content['swagger'] == '2.0'
