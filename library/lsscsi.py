#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: my_test
short_description: This is my test module
# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"
description: This is my longer description explaining my test module.
options:
    name:
        description: the iqdn name for search.
        required: true
        type: str
    cmd:
        description:
            - gives the gt for approprient search.
        required: false
        type: string
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
extends_documentation_fragment:
    - my_namespace.my_collection.my_doc_fragment_name
author:
    - Nitin Namdev (@vortexdude)
'''

EXAMPLES = r'''
# Pass in a message
- name: Test with a message
  lsscsi:
    name: iqn.2006-06.com.quadstor.vtl.windows.drive2
# pass in a message and have changed true
- name: Test with a message and changed output
  lsscsi:
    name: hello world
    new: true
# fail the module
- name: Test failure of the module
  lsscsi:
    name: fail me
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
original_message:
    description: The original name param that was passed in.
    type: str
    returned: always
    sample: 'hello world'
message:
    description: The output message that the test module generates.
    type: str
    returned: always
    sample: 'goodbye'
'''

from ansible.module_utils.basic import AnsibleModule
import re

lsscsibin = ''

def mapped_data(cmd):
    data = run_lsscsi([cmd])
    drives = {}
    for row in data.split('\n'):
        new_row = re.sub(' +', ' ', row)
        line = new_row.split(" ")
        device = ''
        iqdn = ''
        for meta_data in line:
            if '/dev' in meta_data:
                device = meta_data
            if '2006-06' in meta_data:
                iqdn, t, meta = meta_data.split(",")
        drives[iqdn] = dict({'iqdn': iqdn, 'device': device})
    return drives


def run_lsscsi(gargs, **kwargs):
    global lsscsibin
    args = [lsscsibin]
    args.extend(gargs)
    try:
        rc, out, error = module.run_command(args, **kwargs)
        if rc != 0:
            module.fail_json(msg="error while runnig the lsscsi command rc != 0")
    except Exception as e:
        module.fail_json(msg="error while runnig the lsscsi command rc = 0")
        
    return out

def run_module():
    global module

    module_args = dict(
        name=dict(type='str', required=True),
        state=dict(type='str', required=False)
    )

    result = dict(
        changed=False,
        debug="",
        stat={},
        parameter={}
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    global lsscsibin

    lsscsibin = module.get_bin_path('lsscsi', True)
    iscsiadmbin = module.get_bin_path('iscsiadm', True)


    if module.check_mode:
        module.exit_json(**result)

    name =  module.params['name']
    state =  module.params['state']
    full_cmd = "-gt" 

    data = mapped_data(full_cmd)
    if name in data:
        result['changed'] = True
        result['stat']['exist'] = True
        result['stat']['path'] = data[name]['device']
    else:
        result['changed'] = False
        result['stat']['exist'] = False
        result['stat']['path'] = ""

    result['parameter']['name'] = name
    result['parameter']['state'] = state
    result['stat']['bin_path'] = lsscsibin

    if state == 'absent':
        module.fail_json(msg='You requested this to fail', **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
