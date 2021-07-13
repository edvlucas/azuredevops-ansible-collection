#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
from OpenSSL.crypto import verify
__metaclass__ = type

# DOCUMENTATION = r'''
# ---
# module: azdo_agent

# short_description: Triggers an Azure DevOps pipeline and wait for its completion

# version_added: "1.0.0"

# description: Triggers an Azure DevOps pipeline and wait for its completion

# author:
#     - Eduardo Lucas (eduardo.lucas@sequentia.nl)
# '''

import time
from ansible.module_utils.basic import AnsibleModule
from azure.devops.v6_0.pipelines.pipelines_client import PipelinesClient
from azure.devops.v6_0.pipelines.models import Pipeline, RunPipelineParameters
from ansible_collections.community.azuredevops.plugins.module_utils.azdo_utils import get_pipeline_by_name

from msrest.authentication import BasicAuthentication

result = dict(
    changed=False,
    build_id=None,
    build_status=None,
    pipeline_state=None,
    pipeline_result=None,
    timeout=None
)

def run_module():

    result['message'] = "Loading arguments;"

    module_args = dict(
        project=dict(type='str', required=True),
        pipeline_name=dict(type='str', required=True),
        pat=dict(type='str', required=True),
        url=dict(type='str', required=True),
        parameters=dict(type='dict', default={}, required=False),
        wait_for_completion=dict(type='bool', required=False, default=False),
        wait_for_completion_timeout=dict(type='int', required=False, default=300),
        wait_for_completion_poll_interval=dict(type='int', required=False, default=5),
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
    client = PipelinesClient(base_url=organization_url, creds=credentials)
    client.config.connection.verify = False

    project_name = module.params['project']
    pipeline = get_pipeline_by_name(
        client, project_name, module.params['pipeline_name'])

    if not pipeline:
      module.fail_json(msg='Could not find a pipeline named ' + module.params['pipeline_name'], **result)

    pipeline_variables = None
    pipeline_parameters = module.params.get('parameters')
    parameters = RunPipelineParameters(
        preview_run=False,
        resources=None,
        stages_to_skip=None,
        template_parameters=pipeline_parameters,
        variables=pipeline_variables,
        yaml_override=None
    )

    run = client.run_pipeline(
        run_parameters=parameters,
        project=project_name,
        pipeline_id=pipeline.id,
        pipeline_version=None)

    result['message'] = str(run)
    result['build_id'] = run.id

    runstatus = None
    start_time = time.time()
    result['timeout'] = False
    runstatus = None
    timeout_in_seconds = module.params['wait_for_completion_timeout']
    if (module.params['wait_for_completion']):
      while True:
        runstatus = client.get_run(project_name, pipeline.id, run.id)
        result['pipeline_state'] = runstatus.state
        result['pipeline_result'] = str(runstatus.result)
        if runstatus.finished_date:
          result['message'] += "Runstatus: " + str(runstatus)
          break

        time.sleep(module.params['wait_for_completion_poll_interval'])
        elapsed_time = time.time() - start_time
        if (elapsed_time > timeout_in_seconds):
            result['timeout'] = True
            break

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
