from urllib.request import urlretrieve
from diagrams import Cluster, Diagram
from diagrams.custom import Custom
from diagrams.k8s.infra import Master, Node
from diagrams.onprem.iac import Ansible

dnsmasq_url = "https://thekelleys.org.uk/dnsmasq/images/icon.png"
dnsmasq_icon = "dnsmasq.png"
urlretrieve(dnsmasq_url,dnsmasq_icon)

with Diagram(name="OCP4 Lab Helper", show=False):
    
    ansible = Ansible("Helper")
    
    dnsmasq = Custom("dnsmasq", dnsmasq_icon)
    
    master = Master("1")
    node = Node("2")
    
    