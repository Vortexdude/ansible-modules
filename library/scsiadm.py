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
    - Your Name (@yourGitHubHandle)
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

iscsiadmbin = ''

result = {}

def run_iscsiadm(gargs, **kwargs):
    global iscsiadmbin
    changer = False
    data = ""
    args = [iscsiadmbin]
    args.extend(gargs)

    rc, out, error = module.run_command(args, **kwargs)
    if rc == 15:
        data =  "The %s is already login" % (name)
        changer = False
    if rc == 21:
        data =  "The %s is already logout" % (name)
        changer = False
    elif rc == 0:
        data = "target %s : is %s succesfully!" %(name, state)
        changer = True
    return data, changer

def run_module():
    global module
    global iscsiadmbin
    global name
    global state
    
    module_args = dict(
        name=dict(type='str', required=True),
        state=dict(type='str', required=True, choises=['login', 'logout'])
    )

    result = dict(
        changed=False,
        debug="",
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    iscsiadmbin = module.get_bin_path('iscsiadm', True)

    if module.check_mode:
        module.exit_json(**result)
    name =  module.params['name']
    state =  module.params['state']
    state_cmd = "--" + state

    result['changed'] = False
    debug, changer = run_iscsiadm(["-m", "node", "--targetname", name, state_cmd])
    result['debug'] = debug
    result['changed'] = changer

    if state == 'absent':
        module.fail_json(msg='You requested this to fail', **result)

    module.exit_json(**result)


def main():
    run_module()

if __name__ == '__main__':
    main()
