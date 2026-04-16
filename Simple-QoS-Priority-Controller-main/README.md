# QoS Priority Controller - SDN Mininet Project

## Student Details
- **Name:** Dhruvjagadeesh
- **Course:** UE24CS252B - Computer Networks
- **Project:** Simple QoS Priority Controller

## Problem Statement
Implement an SDN-based QoS controller that prioritizes traffic types using OpenFlow rules. Identifies traffic types, assigns priority levels, installs rules, and measures latency impact.

## Topology
- 1 OVS Switch (s1), 4 Hosts (h1-h4), POX Controller (127.0.0.1:6633)

| Host | IP | Traffic Type | Priority | Protocol |
|---|---|---|---|---|
| h1 | 10.0.0.1 | VoIP simulation | HIGH (30) | UDP |
| h2 | 10.0.0.2 | Web/HTTP | MEDIUM (20) | TCP port 80 |
| h3 | 10.0.0.3 | Bulk transfer | LOW (10) | TCP port 5001 |
| h4 | 10.0.0.4 | Blocked host | DROP (100) | All traffic dropped |

## Flow Rules
| Priority | Match | Action |
|---|---|---|
| 100 | IP src=10.0.0.4 | DROP |
| 30 | UDP | NORMAL - VoIP high priority |
| 20 | TCP port 80 | NORMAL - HTTP medium priority |
| 10 | TCP port 5001 | NORMAL - Bulk low priority |
| 0 | table-miss | CONTROLLER |

## Setup
```bash
sudo apt install mininet -y
git clone https://github.com/noxrepo/pox.git ~/pox
git clone https://github.com/Dhruvjagadeesh/qos-sdn-mininet.git
cp qos_controller.py ~/pox/ext/
```

## Running
**Terminal 1 - POX Controller:**
```bash
cd ~/pox
python3 pox.py log.level --DEBUG qos_controller
```
**Terminal 2 - Mininet:**
```bash
sudo python3 qos_topology.py
```

## Test Scenarios
**Scenario 1 - Allowed vs Blocked:**
```bash
mininet> h1 ping -c 3 h2    # PASS - 0% loss
mininet> h4 ping -c 3 h1    # FAIL - 100% loss (blocked)
mininet> sh ovs-ofctl dump-flows s1
```
**Scenario 2 - QoS Priority:**
```bash
mininet> h2 iperf -s -u -p 5005 &
mininet> h1 iperf -c 10.0.0.2 -u -b 5M -t 10 -p 5005
mininet> h3 iperf -s -p 5001 &
mininet> h1 iperf -c 10.0.0.3 -t 10 -p 5001
```

## Results
### Scenario 1: Blocked vs Allowed
| Test | Result |
|---|---|
| h1 ping h2 | 0% packet loss (allowed) |
| h4 ping h1 | 100% packet loss (blocked) |

### Scenario 2: QoS Performance
| Traffic | Priority | Bandwidth | Jitter | Loss |
|---|---|---|---|---|
| UDP VoIP h1 to h2 | HIGH (30) | 5.25 Mbits/sec | 0.020 ms | 0% |
| TCP Bulk h1 to h3 | LOW (10) | 9.57 Mbits/sec | N/A | 0% |

## References
1. Mininet: http://mininet.org
2. POX: https://github.com/noxrepo/pox
3. OpenFlow Spec: https://opennetworking.org
