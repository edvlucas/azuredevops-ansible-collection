#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
from OpenSSL.crypto import verify
__metaclass__ = type

# DOCUMENTATION = r'''
# ---
# module: azdo_agent

# short_description: Manages Azure DevOps agents

# version_added: "1.0.0"

# description: Manages Azure DevOps agents

# author:
#     - Eduardo Lucas (eduardo.lucas@sequentia.nl)
# '''

from ansible.module_utils.basic import AnsibleModule
from azure.devops.v6_0.task_agent.task_agent_client import TaskAgentClient
from msrest.authentication import BasicAuthentication
from ansible_collections.community.azuredevops.plugins.module_utils.azdo_utils import get_agent_and_pool, set_agent_enabled

result = dict(
    changed=False,
    agent=None,
    pool=None,
    message='',
    agent_enabled=None,
    agent_pool_name=None
)


def run_module():

    module_args = dict(
        name=dict(type='str', required=True),
        state=dict(type='str', required=True),
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

    agent_and_pool = get_agent(client, module.params['name'], result)

    result['message'] = result['message'] + " >>> result = " + str(agent_and_pool)
    
    if (agent_and_pool and agent_and_pool['pool']):
      result['agent_pool_name'] = agent_and_pool['pool'].name

    if agent_and_pool and agent_and_pool['agent'] and agent_and_pool['pool']:
        result['message'] = "Agent enabled is " + \
            str(agent_and_pool['agent'].enabled) + \
            " and desired state is " + str(module.params['state'])
        
        # Disable the agent when enabled and desired state = disabled
        if agent_and_pool['agent'].enabled and module.params['state'] == 'disabled':
            result['agent_enabled'] = 'disabled'
            set_agent_enabled(client, agent_and_pool['agent'], agent_and_pool['pool'], False, result)
        else:

          # Disable the agent when disabled and desired state = enabled
          if not agent_and_pool['agent'].enabled and module.params['state'] == 'enabled':
              result['agent_enabled'] = 'enabled'
              set_agent_enabled(client, agent_and_pool['agent'], agent_and_pool['pool'], True, result)
          
          else:
            
            result['agent_enabled'] = agent_and_pool['agent'].enabled
        
        result['agent'] = str(agent_and_pool['agent'])
        result['pool'] = str(agent_and_pool['pool'])

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
