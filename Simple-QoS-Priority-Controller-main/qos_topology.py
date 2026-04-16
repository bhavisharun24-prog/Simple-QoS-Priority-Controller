from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.topo import Topo
from mininet.log import setLogLevel, info
from mininet.link import TCLink
from mininet.cli import CLI

class QoSTopo(Topo):
    def build(self):
        s1 = self.addSwitch("s1", cls=OVSKernelSwitch)
        h1 = self.addHost("h1", ip="10.0.0.1/24")
        h2 = self.addHost("h2", ip="10.0.0.2/24")
        h3 = self.addHost("h3", ip="10.0.0.3/24")
        h4 = self.addHost("h4", ip="10.0.0.4/24")
        self.addLink(h1, s1, cls=TCLink, bw=10)
        self.addLink(h2, s1, cls=TCLink, bw=10)
        self.addLink(h3, s1, cls=TCLink, bw=10)
        self.addLink(h4, s1, cls=TCLink, bw=10)

def run():
    setLogLevel("info")
    net = Mininet(
        topo=QoSTopo(),
        controller=RemoteController("c0", ip="127.0.0.1", port=6633),
        switch=OVSKernelSwitch,
        link=TCLink,
        autoSetMacs=True
    )
    net.start()
    info("Topology ready: h1=VoIP h2=HTTP h3=Bulk h4=Blocked\n")
    CLI(net)
    net.stop()

if __name__ == "__main__":
    run()
