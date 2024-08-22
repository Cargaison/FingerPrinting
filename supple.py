from scapy.all import get_if_list

interfaces = get_if_list()
print("Available interfaces:", interfaces)
