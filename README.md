# Ansible Collection - community.azuredevops

## Installing the collection

  ```bash
  pip install azure-devops
  pip install PyOpenSSL
  ansible-galaxy collection install git@github.com:edvlucas/ansible-azuredevops-collection.git#/community/azuredevops --force --no-cache
  ```
## Using the collection roles

At the beginning of a play, add:

  ```yaml
  collections:
    -  community.azuredevops
  ```

And then, use the collection modules in your tasks. Example:

  ```yaml
  tasks:
    - azdo_agent:
        name: "{{ inventory_hostname }}"
        state: status
        pat: "{{ azdo_pat }}"
        url: "{{ azdo_org_url }}"
      register: agentstatus
  ```

# Modules

## azdo_agent
## azdo_pipeline
