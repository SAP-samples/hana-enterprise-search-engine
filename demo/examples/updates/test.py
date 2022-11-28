import requests
import os
import sys
from copy import deepcopy

sys.path.append(os.path.join(sys.path[0], '..', '..', '..'))
print(sys.path[-1])

from demo.shared.tools import TENANT_SUFFIX, get_base_url, get_root_path

base_url = get_base_url()
root_path = get_root_path()
example_name = 'updates'


cson = {
  'definitions': {
    'AOrganization': {
      'kind': 'entity',
      'includes': [
        'sap.esh.Identifier'
      ],
      'elements': {
        'id': {
          'key': True,
          'type': 'cds.UUID'
        },
        'source': {
          'items': {
            'elements': {
              'name': {
                'type': 'cds.String',
                'length': 4000
              },
              'type': {
                'type': 'cds.String',
                'length': 4000
              },
              'sid': {
                'type': 'cds.String',
                'length': 4000
              }
            }
          }
        },
        'name': {
          'type': 'cds.String',
          'length': 4000
        },
        'relPerson': {
          '@sap.esh.isVirtual': True,
          'type': 'cds.Association',
          'target': 'ARelOrgPerson',
          'keys': [
            {
              'ref': [
                'id'
              ]
            }
          ]
        }
      }
    },
    'APerson': {
      'kind': 'entity',
      'includes': [
        'sap.esh.Identifier'
      ],
      'elements': {
        'id': {
          'key': True,
          'type': 'cds.UUID'
        },
        'source': {
          'items': {
            'elements': {
              'name': {
                'type': 'cds.String',
                'length': 4000
              },
              'type': {
                'type': 'cds.String',
                'length': 4000
              },
              'sid': {
                'type': 'cds.String',
                'length': 4000
              }
            }
          }
        },
        'firstName': {
          'type': 'cds.String',
          'length': 4000
        },
        'lastName': {
          'type': 'cds.String',
          'length': 4000
        },
        'relOrganization': {
          '@sap.esh.isVirtual': True,
          'type': 'cds.Association',
          'target': 'ARelOrgPerson',
          'keys': [
            {
              'ref': [
                'id'
              ]
            }
          ]
        }
      }
    },
    'ARelOrgPerson': {
      'kind': 'entity',
      'includes': [
        'sap.esh.Identifier'
      ],
      'elements': {
        'id': {
          'key': True,
          'type': 'cds.UUID'
        },
        'source': {
          'items': {
            'elements': {
              'name': {
                'type': 'cds.String',
                'length': 4000
              },
              'type': {
                'type': 'cds.String',
                'length': 4000
              },
              'sid': {
                'type': 'cds.String',
                'length': 4000
              }
            }
          }
        },
        'person': {
          'type': 'cds.Association',
          'target': 'APerson',
          'keys': [
            {
              'ref': [
                'id'
              ]
            }
          ]
        },
        'organization': {
          'type': 'cds.Association',
          'target': 'AOrganization',
          'keys': [
            {
              'ref': [
                'id'
              ]
            }
          ]
        }
      }
    },
    'BOrganization': {
      'kind': 'entity',
      'elements': {
        'id': {
          'key': True,
          'type': 'cds.UUID'
        },
        'name': {
          'type': 'cds.String',
          'length': 4000
        },
        'relPerson': {
          '@sap.esh.isVirtual': True,
          'type': 'cds.Association',
          'target': 'BRelOrgPerson',
          'keys': [
            {
              'ref': [
                'id'
              ]
            }
          ]
        }
      }
    },
    'BPerson': {
      'kind': 'entity',
      'elements': {
        'id': {
          'key': True,
          'type': 'cds.UUID'
        },
        'firstName': {
          'type': 'cds.String',
          'length': 4000
        },
        'lastName': {
          'type': 'cds.String',
          'length': 4000
        },
        'relOrganization': {
          '@sap.esh.isVirtual': True,
          'type': 'cds.Association',
          'target': 'BRelOrgPerson',
          'keys': [
            {
              'ref': [
                'id'
              ]
            }
          ]
        }
      }
    },
    'BRelOrgPerson': {
      'kind': 'entity',
      'elements': {
        'id': {
          'key': True,
          'type': 'cds.UUID'
        },
        'person': {
          'type': 'cds.Association',
          'target': 'BPerson',
          'keys': [
            {
              'ref': [
                'id'
              ]
            }
          ]
        },
        'organization': {
          'type': 'cds.Association',
          'target': 'BOrganization',
          'keys': [
            {
              'ref': [
                'id'
              ]
            }
          ]
        }
      }
    },
    'COrganization': {
      'kind': 'entity',
      'includes': [
        'sap.esh.Identifier'
      ],
      'elements': {
        'id': {
          'key': True,
          'type': 'cds.UUID'
        },
        'source': {
          'items': {
            'elements': {
              'name': {
                'type': 'cds.String',
                'length': 4000
              },
              'type': {
                'type': 'cds.String',
                'length': 4000
              },
              'sid': {
                'type': 'cds.String',
                'length': 4000
              }
            }
          }
        },
        'name': {
          'type': 'cds.String',
          'length': 4000
        },
        'relPerson': {
          '@sap.esh.isVirtual': True,
          'type': 'cds.Association',
          'target': 'CRelOrgPerson',
          'keys': [
            {
              'ref': [
                'id'
              ]
            }
          ]
        }
      }
    },
    'CPerson': {
      'kind': 'entity',
      'includes': [
        'sap.esh.Identifier'
      ],
      'elements': {
        'id': {
          'key': True,
          'type': 'cds.UUID'
        },
        'source': {
          'items': {
            'elements': {
              'name': {
                'type': 'cds.String',
                'length': 4000
              },
              'type': {
                'type': 'cds.String',
                'length': 4000
              },
              'sid': {
                'type': 'cds.String',
                'length': 4000
              }
            }
          }
        },
        'firstName': {
          'type': 'cds.String',
          'length': 4000
        },
        'lastName': {
          'type': 'cds.String',
          'length': 4000
        },
        'relOrganization': {
          '@sap.esh.isVirtual': True,
          'type': 'cds.Association',
          'target': 'CRelOrgPerson',
          'keys': [
            {
              'ref': [
                'id'
              ]
            }
          ]
        }
      }
    },
    'CRelOrgPerson': {
      'kind': 'entity',
      'elements': {
        'id': {
          'key': True,
          'type': 'cds.UUID'
        },
        'person': {
          'type': 'cds.Association',
          'target': 'CPerson',
          'keys': [
            {
              'ref': [
                'id'
              ]
            }
          ]
        },
        'organization': {
          'type': 'cds.Association',
          'target': 'COrganization',
          'keys': [
            {
              'ref': [
                'id'
              ]
            }
          ]
        }
      }
    },
    'DOrganization': {
      'kind': 'entity',
      'elements': {
        'id': {
          'key': True,
          'type': 'cds.UUID'
        },
        'name': {
          'type': 'cds.String',
          'length': 4000
        },
        'relPerson': {
          '@sap.esh.isVirtual': True,
          'type': 'cds.Association',
          'target': 'DRelOrgPerson',
          'keys': [
            {
              'ref': [
                'id'
              ]
            }
          ]
        }
      }
    },
    'DPerson': {
      'kind': 'entity',
      'elements': {
        'id': {
          'key': True,
          'type': 'cds.UUID'
        },
        'firstName': {
          'type': 'cds.String',
          'length': 4000
        },
        'lastName': {
          'type': 'cds.String',
          'length': 4000
        },
        'relOrganization': {
          '@sap.esh.isVirtual': True,
          'type': 'cds.Association',
          'target': 'DRelOrgPerson',
          'keys': [
            {
              'ref': [
                'id'
              ]
            }
          ]
        }
      }
    },
    'DRelOrgPerson': {
      'kind': 'entity',
      'includes': [
        'sap.esh.Identifier'
      ],
      'elements': {
        'id': {
          'key': True,
          'type': 'cds.UUID'
        },
        'source': {
          'items': {
            'elements': {
              'name': {
                'type': 'cds.String',
                'length': 4000
              },
              'type': {
                'type': 'cds.String',
                'length': 4000
              },
              'sid': {
                'type': 'cds.String',
                'length': 4000
              }
            }
          }
        },
        'person': {
          'type': 'cds.Association',
          'target': 'DPerson',
          'keys': [
            {
              'ref': [
                'id'
              ]
            }
          ]
        },
        'organization': {
          'type': 'cds.Association',
          'target': 'DOrganization',
          'keys': [
            {
              'ref': [
                'id'
              ]
            }
          ]
        }
      }
    },
    'sap.esh.Identifier': {
      'kind': 'aspect',
      'elements': {
        'id': {
          'key': True,
          'type': 'cds.UUID'
        },
        'source': {
          'items': {
            'elements': {
              'name': {
                'type': 'cds.String',
                'length': 4000
              },
              'type': {
                'type': 'cds.String',
                'length': 4000
              },
              'sid': {
                'type': 'cds.String',
                'length': 4000
              }
            }
          }
        }
      }
    }
  },
  'meta': {
    'creator': 'CDS Compiler v2.15.2',
    'flavor': 'inferred'
  },
  '$version': '2.0'
}


person = {
    'firstName': 'John',
    'lastName': 'Doe'
}
person_src = deepcopy(person) | {
    'source': [
        {
            'name': 'systemA',
            'type': 'Person',
            'sid': 'objectid123456'
        }
    ]
}

organization = {
    'name': 'ACME inc.'
}
organization_src = deepcopy(organization) | {
    'source': [
        {
            'name': 'systemA',
            'type': 'Organization',
            'sid': 'objectid098765'
        }
    ]
}

rel_org_person_src = {
    'source': [
        {
            'name': 'systemA',
            'type': 'RelOrgPerson',
            'sid': 'objectid2222444555'
        }
    ],
    'person': {
        'source': [
            {
                'name': 'systemA',
                'type': 'Person',
                'sid': 'objectid123456'
            }
        ]
    },
    'organization': {
        'source': [
            {
                'name': 'systemA',
                'type': 'Organization',
                'sid': 'objectid098765'
            }
        ]
    }
}


#### Test 1: A-Objects with source key
object_prefix = 'A'

data = {
    f'{object_prefix}Person': [person_src],
    f'{object_prefix}Organization': [organization_src]
}

r = requests.delete(f'{base_url}/v1/tenant/{example_name}{TENANT_SUFFIX}')
print(f'Delete tenanat status code: {r.status_code}')
r = requests.post(f'{base_url}/v1/tenant/{example_name}{TENANT_SUFFIX}')
print(f'Create tenanat status code: {r.status_code}')
r = requests.post(f'{base_url}/v1/deploy/{example_name}{TENANT_SUFFIX}', json=cson)
print(f'Deploy status code: {r.status_code}')
r = requests.post(f'{base_url}/v1/data/{example_name}{TENANT_SUFFIX}', json=data)
print(f'Post data status code: {r.status_code}')
person_id = r.json()[f'{object_prefix}Person'][0]['id']
organization_id = r.json()[f'{object_prefix}Organization'][0]['id']

r = requests.post(f'{base_url}/v1/data/{example_name}{TENANT_SUFFIX}', json=data)
print(f'Post data again status code: {r.status_code}. Shoud be 400')

data = {
    f'{object_prefix}RelOrgPerson': [rel_org_person_src]
}
r = requests.post(f'{base_url}/v1/data/{example_name}{TENANT_SUFFIX}', json=data)
print(r.status_code)
rel_org_person_id = r.json()[f'{object_prefix}RelOrgPerson'][0]['id']
data = {
    f'{object_prefix}Person': [{'id': person_id}],
    f'{object_prefix}Organization': [{'id': organization_id}],
    f'{object_prefix}RelOrgPerson': [{'id': rel_org_person_id}]
}
r = requests.delete(f'{base_url}/v1/data/{example_name}{TENANT_SUFFIX}', json=data)
print(r.status_code)


#### Test 2: A-Objects without source key
object_prefix = 'A'
data = {
    f'{object_prefix}Person': [person],
    f'{object_prefix}Organization': [organization]
}

r = requests.delete(f'{base_url}/v1/tenant/{example_name}{TENANT_SUFFIX}')
print(f'Delete tenanat status code: {r.status_code}')
r = requests.post(f'{base_url}/v1/tenant/{example_name}{TENANT_SUFFIX}')
print(f'Create tenanat status code: {r.status_code}')
r = requests.post(f'{base_url}/v1/deploy/{example_name}{TENANT_SUFFIX}', json=cson)
print(f'Deploy status code: {r.status_code}')
r = requests.post(f'{base_url}/v1/data/{example_name}{TENANT_SUFFIX}', json=data)
print(r.status_code)
person_id = r.json()[f'{object_prefix}Person'][0]['id']
organization_id = r.json()[f'{object_prefix}Organization'][0]['id']

data = {
    f'{object_prefix}RelOrgPerson': [{'person':{'id':person_id}, 'organization':{'id':organization_id}}]
}
r = requests.post(f'{base_url}/v1/data/{example_name}{TENANT_SUFFIX}', json=data)
print(r.status_code)
rel_org_person_id = r.json()[f'{object_prefix}RelOrgPerson'][0]['id']
data = {
    f'{object_prefix}Person': [{'id': person_id}],
    f'{object_prefix}Organization': [{'id': organization_id}],
    f'{object_prefix}RelOrgPerson': [{'id': rel_org_person_id}]
}
r = requests.delete(f'{base_url}/v1/data/{example_name}{TENANT_SUFFIX}', json=data)
print(r.status_code)


#### Test 3: B-Objects (they do not have source keys at all)
object_prefix = 'B'
data = {
    f'{object_prefix}Person': [person],
    f'{object_prefix}Organization': [organization]
}

r = requests.delete(f'{base_url}/v1/tenant/{example_name}{TENANT_SUFFIX}')
print(f'Delete tenanat status code: {r.status_code}')
r = requests.post(f'{base_url}/v1/tenant/{example_name}{TENANT_SUFFIX}')
print(f'Create tenanat status code: {r.status_code}')
r = requests.post(f'{base_url}/v1/deploy/{example_name}{TENANT_SUFFIX}', json=cson)
print(f'Deploy status code: {r.status_code}')
r = requests.post(f'{base_url}/v1/data/{example_name}{TENANT_SUFFIX}', json=data)
print(r.status_code)
person_id = r.json()[f'{object_prefix}Person'][0]['id']
organization_id = r.json()[f'{object_prefix}Organization'][0]['id']

data = {
    f'{object_prefix}RelOrgPerson': [{'person':{'id':person_id}, 'organization':{'id':organization_id}}]
}
r = requests.post(f'{base_url}/v1/data/{example_name}{TENANT_SUFFIX}', json=data)
print(r.status_code)
rel_org_person_id = r.json()[f'{object_prefix}RelOrgPerson'][0]['id']
data = {
    f'{object_prefix}Person': [{'id': person_id}],
    f'{object_prefix}Organization': [{'id': organization_id}],
    f'{object_prefix}RelOrgPerson': [{'id': rel_org_person_id}]
}
r = requests.post(f'{base_url}/v1/data/{example_name}{TENANT_SUFFIX}', json=data)
print(f'Post data again status code: {r.status_code}. Shoud be 400')
r = requests.delete(f'{base_url}/v1/data/{example_name}{TENANT_SUFFIX}', json=data)

