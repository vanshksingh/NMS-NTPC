import ping3

def ping_host(host, count=4):
    for i in range(count):
        result = ping3.ping(host)
        if result is not None:
            print(f"Reply from {host}: time={result} ms")
        else:
            print(f"No response from {host}")

if __name__ == "__main__":
    target_host = "172.20.10.2"  # Replace with your target IP address or hostname
    ping_count = 5  # Number of pings to send (adjust as needed)

    ping_host(target_host, ping_count)
