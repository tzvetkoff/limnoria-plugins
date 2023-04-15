#!/usr/bin/env python3

import json

payload1 = {
  0: {
    'id': '05f091479701a15841275f5d8e79245b3f54f40e',
    'message': 'Commit message first line\n\nSecond line\nThird line\n',
    'url': 'https://try.gitea.io/tzvetkoff/blah/commit/05f091479701a15841275f5d8e79245b3f54f40e',
    'author': {
      'name': 'Latchezar Tzvetkoff',
      'email': 'latchezar@tzvetkoff.net',
      'username': ''
    },
    'committer': {
      'name': 'Latchezar Tzvetkoff',
      'email': 'latchezar@tzvetkoff.net',
      'username': ''
    },
    'verification': None,
    'timestamp': '2022-09-19T05:43:36+03:00',
    'added': ['README.md'],
    'removed': [],
    'modified': []
  }
}

payload2 = {
  0: {
    'id': '7af01e4181947e5e261386964f297839e7b3dbe3',
    'message': 'Remove a line\n',
    'url': 'https://try.gitea.io/tzvetkoff/blah/commit/7af01e4181947e5e261386964f297839e7b3dbe3',
    'author': {
      'name': 'Latchezar Tzvetkoff',
      'email': 'latchezar@tzvetkoff.net',
      'username': ''
    },
    'committer': {
      'name': 'Latchezar Tzvetkoff',
      'email': 'latchezar@tzvetkoff.net',
      'username': ''
    },
    'verification': None,
    'timestamp': '2022-09-19T05:45:43+03:00',
    'added': [],
    'removed': [],
    'modified': ['README.md']
  },
  1: {
    'id': '52b50846b91b8385cf69de8387bf18adc6ca2d8b',
    'message': 'Add a line\n',
    'url': 'https://try.gitea.io/tzvetkoff/blah/commit/52b50846b91b8385cf69de8387bf18adc6ca2d8b',
    'author': {
      'name': 'Latchezar Tzvetkoff',
      'email': 'latchezar@tzvetkoff.net',
      'username': ''
    },
    'committer': {
      'name': 'Latchezar Tzvetkoff',
      'email': 'latchezar@tzvetkoff.net',
      'username': ''
    },
    'verification': None,
    'timestamp': '2022-09-19T05:45:33+03:00',
    'added': [],
    'removed': [],
    'modified': ['README.md']
  }
}


print(json.dumps(payload1))
print()
print(json.dumps(payload2))

# vim:ft=python:ts=4:sts=4:sw=4:et:tw=119
