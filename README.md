# OpenShift Container Platform 4 Lab
This set of ansible plays provides the necessary automation to deploy a OCP4 lab environment with the help of libvirt. 

Notes: 
0. this assume that you have some understanding about OCP4 and how its deployment workflow.
1. as it uses PXE to provision the OCP4 machines, this should also work with any hypervisor or bare metal. 
2. it requires valid RHEL subscriptions and access to Red Hat Infrastucture Provider for OpenShift Cluster Manager website.

## Environment
The automation will require a first RHEL7 VM that will act as a:
- dhcp server
- dns server
- pxe server
- http server
- haproxy server

The above will help in the provisioning of the OCP4 environment along wiht being the required loadbalancer for OCP4. Remember, this is a lab ;)

Then you will have to create:
- 1 VM for the OCP4 bootstrap, this one will be decommissioned at the end of the deployment
- 3 VMs for the master nodes acting also as workers (this is a lab!). 
These VMs will have:
- either the RHEL Unknown or Fedora CoreOS Operating System definition in your hypervisor.
- the boot from network as first option to allow the PXE boot and don't forget the let the hard drive a secondary chose so that it can boot automatically

## Create the OCP4 lab
### Parameters
Before using the lab_setup play, the following parameters need to be set within the file called "parameters_setup.yml":

The following parameters are required to register the "infra" virtual machine to RHN or Satelitte and fetch a valid subscription. 
rhn_user: "johndoe"
rhn_pass: "mysupersecret"
rhn_pool: "1234567890ABC"

The following can be retrieve on the OpenShift Cluster Manager website and is required for the installation.
mypullsecret: '{"auths": ...}'
Note: mypullsecret needs to be enclosed between single quotes. If not, the play will fail. 

The following parameters are used to customized the OCP4 cluster. The
clustername: "cluster"
labdomain: "my.lab"

The following parameters are used to customized the DHCP servers and fit your network. 
dhciprange: "192.168.100"
ptriprange: "100.168.192"
dhcprange: "{{ dhcpiprange }}.20,{{ dhcpiprange }}.30,24h"
dhcproute: "{{ dhcpiprange }}.1"
Note: don't change/remove {{ dhcpiprange }} from dhcprange or dhcproute unless you know what you're doing.

### The play
Edit the inventory file to target your infra virtual machine.
Then, run the play after customizing "parameters_setup.yml" with the following command:

```
$ ansible-playbook -i inventory -e @parameters_lab_setup.yml lab_setup.yml
```

The following output is expected:

```
$ ansible-playbook -i inventory -e @../parameters_lab_setup.yml lab_setup.yml 

PLAY [DNSDHCP] ******************************************************************************

TASK [sysprep : Verify if host is already registered] ***************************************
changed: [192.168.100.10]

TASK [sysprep : debug] **********************************************************************
skipping: [192.168.100.10]

TASK [sysprep : Subscribe to RHN] ***********************************************************
skipping: [192.168.100.10]

TASK [sysprep : Disable Repositories] *******************************************************
changed: [192.168.100.10]

TASK [sysprep : Enable Repositories] ********************************************************
changed: [192.168.100.10]

TASK [sysprep : Update system] **************************************************************
ok: [192.168.100.10]

TASK [sysprep : Install all required packages for Infra Services VM] ************************
ok: [192.168.100.10]

TASK [sysprep : Configure firewall for httpd] ***********************************************
ok: [192.168.100.10] => (item=dns)
ok: [192.168.100.10] => (item=dhcp)
ok: [192.168.100.10] => (item=http)
ok: [192.168.100.10] => (item=tftp)

TASK [httpd : Inject configuration file] ****************************************************
ok: [192.168.100.10]

TASK [Enabling httpd service] ***************************************************************
ok: [192.168.100.10]

TASK [ocp : Create OCP temp directory] ******************************************************
ok: [192.168.100.10]

TASK [ocp : Unarchive latest openshift installer] *******************************************
ok: [192.168.100.10]

TASK [ocp : Unarchive latest openshift cli command] *****************************************
ok: [192.168.100.10]

TASK [ocp : Create installation directory] **************************************************
ok: [192.168.100.10]

TASK [ocp : Inject installation template] ***************************************************
changed: [192.168.100.10]

TASK [ocp : Call openshift-installer to create manifest] ************************************
changed: [192.168.100.10]

TASK [ocp : Call openshift-installer to create ignition config files] ***********************
changed: [192.168.100.10]

TASK [ocp : Create RHCOS directory] *********************************************************
ok: [192.168.100.10]

TASK [ocp : Create RHCOS directory] *********************************************************
ok: [192.168.100.10]

TASK [ocp : Create RHCOS directory] *********************************************************
ok: [192.168.100.10]

TASK [ocp : Download latest RHCOS iso] ******************************************************
ok: [192.168.100.10]

TASK [ocp : Download latest RHCOS raw] ******************************************************
ok: [192.168.100.10]

TASK [ocp : Download latest RHCOS kernel] ***************************************************
ok: [192.168.100.10]

TASK [ocp : Download latest RHCOS initramfs] ************************************************
ok: [192.168.100.10]

TASK [dnsmasq : fixing permissions] *********************************************************
[WARNING]: Consider using the file module with mode rather than running 'chmod'.  If you
need to use command because file is insufficient you can add 'warn: false' to this command
task or set 'command_warnings=False' in ansible.cfg to get rid of this message.
changed: [192.168.100.10]

TASK [dnsmasq : fixing permissions] *********************************************************
changed: [192.168.100.10]

TASK [Inject dnsmasq configuration file] ****************************************************
changed: [192.168.100.10]

TASK [dnsmasq : Inject hosts configuration file] ********************************************
ok: [192.168.100.10]

TASK [dnsmasq : Copy syslinux file for tftp server usage] ***********************************
changed: [192.168.100.10]

TASK [dnsmasq : Inject default pxelinux configuration file] *********************************
changed: [192.168.100.10]

TASK [Enabling dnsmasq service] *************************************************************
changed: [192.168.100.10]

TASK [Inject haproxy configuration file] ****************************************************
changed: [192.168.100.10]

TASK [Enabling haproxy service] *************************************************************
changed: [192.168.100.10]

PLAY RECAP **********************************************************************************
192.168.100.10             : ok=31   changed=14   unreachable=0    failed=0    skipped=2    rescued=0    ignored=0   
``` 

When the play is successful within your setup, you modify your local resolv.conf and target the infra vm and then do the following tests:

```
$ curl 192.168.100.10:8080/ocp-installer
```
The above should return the html output for listing the content of the directory which should be the following if you do a browser check:

```
Index of /ocp-installer
Parent Directory
README.md
cluster/
openshift-install
``` 

Then do a DNS check as follow:
```
$ for i in {apps,myshiny.apps,api,api-int}; do nslookup $i.cluster.my.lab;done
Server:		192.168.100.10
Address:	192.168.100.10#53

Name:	apps.cluster.my.lab
Address: 192.168.100.10

Server:		192.168.100.10
Address:	192.168.100.10#53

Name:	myshiny.apps.cluster.my.lab
Address: 192.168.100.10

Server:		192.168.100.10
Address:	192.168.100.10#53

Name:	api.cluster.my.lab
Address: 192.168.100.10

Server:		192.168.100.10
Address:	192.168.100.10#53

Name:	api-int.cluster.my.lab
Address: 192.168.100.10

```
Note: none can fail otherwise OCP4 deployment fail and/or not usable

At this stage, do you a HAproxy check is almost useless as there is not application behin however the following should be expected:

```
$ curl api.cluster.my.lab
curl: (52) Empty reply from server
``` 
If there is any other responses, then the play log output needs to be analyzed.


### Lab creation
Now that the infra virtual machine is running with all the appropriate services, the bootstrap virtual machine can be started with as boot sequence network then disk to allow PXE boot.

When the PXE boot menu appears select "1) OCP4 bootstrap", the virtual machine will boot, then deploy RHCOS with the bootstrap ignition configuration file generated with the play and then reboot itself. 
When the machine reboot itself, do not touch any key on the keyboard, when the timeout will occur on the PXE boot menu, the bootstrap virtual machine will boot on its local disk with the freshly install RHCOS.

Repeat the process for the 3 master/worker nodes by selecting "2) OCP4 master" entry.

At this stage, the 3 master/worker nodes will connect with the bootstrap VM and start their deployment as such to form the OCP4 cluster. This process can take between 5 to 40 minutes depending on the allocated resoources to the respective virtual machines.

To monitor the "progress", you can ssh to your infra virtual machine, and do the followings:

```
$ cd /var/www/html/ocp-installer
$ sudo ./openshift-install --dir=cluster wait-for bootstrap-complete
INFO Waiting up to 20m0s for the Kubernetes API at https://api.cluster.my.lab:6443... 
INFO API v1.18.3+47c0e71 up                       
INFO Waiting up to 40m0s for bootstrapping to complete... 
INFO It is now safe to remove the bootstrap resources 
INFO Time elapsed: 8m2s                           

```
When the above message appears, the bootstrap machine can be stopped and remove from the loadbalancer.

Then, while still being in the same directory, do the followings to verify connectivity to the cluster:

```
$ export KUBECONFIG=auth/kubeconfig
$ oc whoami
system:admin
$ oc get nodes
NAME                        STATUS   ROLES           AGE   VERSION
ocp-mst-01.cluster.my.lab   Ready    master,worker   36m   v1.18.3+47c0e71
ocp-mst-02.cluster.my.lab   Ready    master,worker   33m   v1.18.3+47c0e71
ocp-mst-03.cluster.my.lab   Ready    master,worker   38m   v1.18.3+47c0e71

``` 

At this stage, follow the remaining of the documentation: https://docs.openshift.com/container-platform/4.5/installing/installing_bare_metal/installing-bare-metal.html#installation-approve-csrs_installing-bare-metal which should not take more than 10-15 minutes.

Once you're done with the last steps, you can start create a project or connect to the console via the url https://console-openshift-console.apps.cluster.my.lab based on the above parameters example, so change clustername (here cluster) and the labdomain (here my.lab) to match yours.
 
## TODO
1. allow a setup with an external DHCP server
2. allow a setup with an external DNS server
3. allow a setup with an external PXE server
4. allow a setup with an external LoadBalancer
5. change the fix permission with a more elegant solution
6. automatic VM creation on libvirt
7. modify the dnsmasq_conf.j2 MAC address entry with a variable to be set in the parameters_setup.yml file
8. create a play for the post boostrap steps
