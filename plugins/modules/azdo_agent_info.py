#!/usr/bin/python
# -*- coding: utf-8 -*- 

# Copyright: (c) 2021, Eduardo Lucas <eduardo.lucas@sequentia.nl>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
from OpenSSL.crypto import verify
__metaclass__ = type

DOCUMENTATION = '''
module: azdo_agent_info
version_added: "2.11.0"
short_description: Get the information of an azure devops agent
description:
    - Get the information of an azure devops agent
options:
    name:
        description:
            - The agent name
        type: str
        required: True
    pat:
        description:
            - The Azure DevOps Personal Access Token for accessing the Azure DevOps API
        type: str
        required: True
    url:
        description:
            - An url pointing to an Azure DevOps collection
        type: str
extends_documentation_fragment:
    - TODO: azure-devops
author:
    - Eduardo Lucas (@sequentia.nl)
'''

EXAMPLES = '''
    - name: Get the status of an agent
      azdo_agent_info:
        name: 'build-agent-01'
        pat: <your PAT>
        url: https://azuredevops.local/tfs/DefaultCollection
'''

RETURN = '''
agent_enabled:
    description:
        - The object_id for the group.
    type: bool
    returned: always
    sample: True
agent_pool_name:
    description:
        - The pool where the agent is located
    returned: always
    type: str
    sample: buildpool
'''

import traceback
from ansible.module_utils.basic import missing_required_lib
from ansible.module_utils.basic import AnsibleModule
from msrest.authentication import BasicAuthentication

result = dict(
    changed=False,
    agent=None,
    pool=None,
    message='',
    agent_enabled=None,
    agent_pool_name=None
)

def run_module():

  try:
    module_args = dict(
        name=dict(type='str', required=True),
        pat=dict(type='str', required=True),
        url=dict(type='str', required=True),
        verifyTls=dict(type='bool', required=False, default=True),
    )
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
    if module.check_mode: module.exit_json(**result)

    # The shared library imports should only be imported after module is defined, so the proper missing dependency errors can be properly reported via module.fail_json
    from ansible_collections.community.azuredevops.plugins.module_utils.azdo_utils import get_agent_and_pool
    from azure.devops.v6_0.task_agent.task_agent_client import TaskAgentClient

    client = TaskAgentClient(base_url = module.params.get('url'), creds = BasicAuthentication('', module.params.get('pat')))
    client.config.connection.verify = module.params.get('verifyTls')

    agent_and_pool = get_agent_and_pool(client, module.params['name'], result)

    result['message'] = result['message'] + " >>> result = " + str(agent_and_pool)

    if (agent_and_pool.get('pool') and agent_and_pool.get('agent')):
      result['agent_pool_name'] = agent_and_pool['pool'].name
      result['agent_enabled'] = agent_and_pool['agent'].enabled
      result['agent'] = str(agent_and_pool.get('agent'))
      result['pool'] = str(agent_and_pool['pool'])
    else:
      raise Exception('Agent not found')

    module.exit_json(**result)

  except ModuleNotFoundError:
    import traceback
    from ansible.module_utils.basic import missing_required_lib
    module.fail_json(msg=missing_required_lib("azure-devops"), exception="Missing azure-devops>=6.0.0b4")

def main():
    run_module()

if __name__ == '__main__':
    main()
