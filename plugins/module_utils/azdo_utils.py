from azure.devops.v6_0.pipelines.pipelines_client import PipelinesClient
from azure.devops.v6_0.pipelines.models import Pipeline, RunPipelineParameters

def get_agent_and_pool(azdo_client, agent_name, ansible_result):
    agent_and_pool_result = dict(pool=None, agent=None)
    azdo_client.config.connection.verify = False
    pools = azdo_client.get_agent_pools()
    for pool in pools:
        pool_agents = azdo_client.get_agents(pool_id=pool.id)
        for pool_agent in pool_agents:
            if pool_agent.name.lower() == agent_name.lower():
                pool_agent_details = azdo_client.get_agent(
                    pool_id=pool.id, agent_id=pool_agent.id, include_capabilities=None, include_assigned_request=True, include_last_completed_request=True, property_filters=None)
                agent_and_pool_result = dict(pool=pool, agent=pool_agent_details)
                ansible_result['message'] = ansible_result['message'] + '>>> found agent'
                break
    return agent_and_pool_result

def set_agent_enabled(azdo_client, agent, pool, enabled, ansible_result):
    agent.enabled = enabled
    azdo_client.update_agent(agent, pool.id, agent.id)
    ansible_result["message"] = ansible_result["message"] + \
        ('\r\n*** updating agent ***' + str(agent))
    return

def get_pipeline_by_name(pipeline_client: PipelinesClient, project, name):
    pipeline_list = pipeline_client.list_pipelines(project)
    pipeline: Pipeline
    for pipeline in pipeline_list:
        if (pipeline.name == name):
            return pipeline
    return None
