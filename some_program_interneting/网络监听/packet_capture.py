from scapy.all import sniff, Ether, IP, TCP, UDP, ARP, ICMP, DNS
from scapy.layers.http import HTTP

def capture_packets(count=10):
    packets = sniff(count=count)  # 捕获指定数量的数据包
    return packets

def save_packet(packet, filename="packets.log"):
    with open(filename, "ab") as f:
        f.write(bytes(packet))

def filter_packets(packets, protocol):
    filtered_packets = []
    for packet in packets:
        if protocol in packet:
            filtered_packets.append(packet)
    return filtered_packets

def decode_packet(packet):
    decoded = {
        "以太网头": packet[Ether].summary(),
        "协议": packet[Ether].type
    }

    if IP in packet:
        decoded.update({
            "IP头": packet[IP].summary(),
            "源IP": packet[IP].src,
            "目标IP": packet[IP].dst
        })
    if TCP in packet:
        decoded["TCP头"] = packet[TCP].summary()
    elif UDP in packet:
        decoded["UDP头"] = packet[UDP].summary()
    elif ARP in packet:
        decoded["ARP头"] = packet[ARP].summary()
    elif ICMP in packet:
        decoded["ICMP头"] = packet[ICMP].summary()
    elif DNS in packet:
        decoded["DNS头"] = packet[DNS].summary()
    elif HTTP in packet:
        decoded["HTTP头"] = packet[HTTP].summary()
    return decoded

def classify_packets(packets):
    stats = {
        'total': len(packets),
        'ipv4': 0,
        'tcp': 0,
        'udp': 0,
        'arp': 0,
        'icmpv4': 0,
        'dns': 0,
        'http': 0
    }
    for packet in packets:
        if IP in packet:
            stats['ipv4'] += 1
            if TCP in packet:
                stats['tcp'] += 1
            elif UDP in packet:
                stats['udp'] += 1
            elif ICMP in packet:
                stats['icmpv4'] += 1
        elif ARP in packet:
            stats['arp'] += 1
        elif DNS in packet:
            stats['dns'] += 1
        elif HTTP in packet:
            stats['http'] += 1
    return stats