#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
from OpenSSL.crypto import verify
__metaclass__ = type

# DOCUMENTATION = r'''
# ---
# module: azdo_agent_wait_for_idle

# short_description: Waits until an agent is idle (not running any pipeline)

# version_added: "1.0.0"

# description: Waits until an agent is idle (not running any pipeline)

# author:
#     - Eduardo Lucas (eduardo.lucas@sequentia.nl)
# '''

import time
from ansible.module_utils.basic import AnsibleModule
from azure.devops.v6_0.task_agent.task_agent_client import TaskAgentClient
from msrest.authentication import BasicAuthentication
from ansible_collections.community.azuredevops.plugins.module_utils.azdo_utils import get_agent

result = dict(
    changed=False,
    message='',
    elapsed=0
)

def run_module():
    module_args = dict(
        name=dict(type='str', required=True),
        sleep=dict(type='int', required=False, default=5),
        timeout=dict(type='int', required=False, default=600),
        pat=dict(type='str', required=True),
        url=dict(type='str', required=True),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json(**result)


    personal_access_token = module.params['pat']
    organization_url = module.params['url']
    credentials = BasicAuthentication('', personal_access_token)
    client = TaskAgentClient(base_url=organization_url, creds=credentials)
    client.config.connection.verify = False

    is_idle = False
    is_timeout = False
    start_time = time.time()
    while not is_idle:

        agent_and_pool = get_agent(client, module.params['name'])

        if not agent_and_pool or not agent_and_pool['agent']:
            is_idle = True
            break


        if agent_and_pool['agent'].assigned_request == None:
            is_idle = False
            break

        time.sleep(module.params['sleep'])
        elapsed_time = time.time() - start_time
        result['elapsed'] = str(elapsed_time)
        if (elapsed_time > module.params['timeout']):
            is_timeout = True
            break

    if (is_timeout):
        module.fail_json(
            msg='Timet out waiting for agent to be idle', **result)

    module.exit_json(**result)

def main():
    run_module()


if __name__ == '__main__':
    main()
