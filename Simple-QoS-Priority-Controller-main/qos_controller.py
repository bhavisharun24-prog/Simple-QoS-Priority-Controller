from pox.core import core
from pox.lib.util import dpidToStr
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr

log = core.getLogger()
mac_table = {}

def install_flow(connection, priority, match, actions=None, idle_timeout=0, hard_timeout=0):
    msg = of.ofp_flow_mod()
    msg.priority     = priority
    msg.match        = match
    msg.idle_timeout = idle_timeout
    msg.hard_timeout = hard_timeout
    msg.actions      = actions if actions is not None else []
    connection.send(msg)

def handle_connection_up(event):
    conn = event.connection
    log.info("Switch connected: %s - installing QoS rules", dpidToStr(event.dpid))

    match_block = of.ofp_match()
    match_block.dl_type = 0x0800
    match_block.nw_src  = IPAddr("10.0.0.4")
    install_flow(conn, priority=100, match=match_block, actions=[])
    log.info("INSTALLED: DROP - all traffic from h4")

    match_udp = of.ofp_match()
    match_udp.dl_type  = 0x0800
    match_udp.nw_proto = 17
    install_flow(conn, priority=30, match=match_udp,
                 actions=[of.ofp_action_output(port=of.OFPP_NORMAL)])
    log.info("INSTALLED: HIGH - UDP VoIP")

    match_http = of.ofp_match()
    match_http.dl_type  = 0x0800
    match_http.nw_proto = 6
    match_http.tp_dst   = 80
    install_flow(conn, priority=20, match=match_http,
                 actions=[of.ofp_action_output(port=of.OFPP_NORMAL)])
    log.info("INSTALLED: MEDIUM - TCP port 80 HTTP")

    match_bulk = of.ofp_match()
    match_bulk.dl_type  = 0x0800
    match_bulk.nw_proto = 6
    match_bulk.tp_dst   = 5001
    install_flow(conn, priority=10, match=match_bulk,
                 actions=[of.ofp_action_output(port=of.OFPP_NORMAL)])
    log.info("INSTALLED: LOW - TCP port 5001 bulk")

def handle_packet_in(event):
    conn   = event.connection
    dpid   = event.dpid
    inport = event.port
    packet = event.parsed
    if not packet.parsed:
        return
    mac_table.setdefault(dpid, {})
    mac_table[dpid][packet.src] = inport
    dst = packet.dst
    if dst in mac_table[dpid]:
        out_port = mac_table[dpid][dst]
        match = of.ofp_match.from_packet(packet, inport)
        install_flow(conn, priority=1, match=match,
                     actions=[of.ofp_action_output(port=out_port)],
                     idle_timeout=30, hard_timeout=60)
        msg = of.ofp_packet_out()
        msg.data    = event.ofp
        msg.in_port = inport
        msg.actions = [of.ofp_action_output(port=out_port)]
        conn.send(msg)
    else:
        msg = of.ofp_packet_out()
        msg.data    = event.ofp
        msg.in_port = inport
        msg.actions = [of.ofp_action_output(port=of.OFPP_FLOOD)]
        conn.send(msg)

def launch():
    core.openflow.addListenerByName("ConnectionUp", handle_connection_up)
    core.openflow.addListenerByName("PacketIn",     handle_packet_in)
    log.info("QoS Controller ready - waiting for switches...")
