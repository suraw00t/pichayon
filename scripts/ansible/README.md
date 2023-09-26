How to use ansible to update hosts
`
1. add hosts to /etc/hosts
2. ssh-copy-id <user@host> (for all hosts)
3. source venv/bin/activate
4. cd pichayon/scripts/ansible
5. run command: ansible-playbook ansible_playbooks/deploy-pichayon.yml -i ansible-inventory.yml
6. wait for ansible completed all tasks
`