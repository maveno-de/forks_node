import asyncio, dns.asyncresolver
import socket

from hddcoin.server.server import HDDcoinServer
from hddcoin.types.peer_info import PeerInfo


def start_reconnect_task(server: HDDcoinServer, peer_info_arg: PeerInfo, log, auth: bool):
    """
    Start a background task that checks connection and reconnects periodically to a peer.
    """
    # If peer_info_arg is already an address, use it, otherwise resolve it here.
    if peer_info_arg.is_valid(True):
        peer_info = peer_info_arg
        peer_url = ''
    else:
        peer_info = PeerInfo(socket.gethostbyname(peer_info_arg.host), peer_info_arg.port)
        peer_url = peer_info_arg.host

    async def connection_check():
        nonlocal peer_info
        while True:
            peer_retry = True
            for _, connection in server.all_connections.items():
                if connection.get_peer_info() == peer_info or connection.get_peer_info() == peer_info_arg:
                    peer_retry = False
            if peer_retry:
                if peer_url:
                    ipv4_entries = []
                    resolver = dns.asyncresolver.Resolver()
                    try:
                        try:
                            answers = await resolver.resolve(peer_url, 'A', lifetime=3.0)
                            ipv4_entries = [str(an.to_text()) for an in answers]
                        except dns.resolver.NoAnswer as e:
                            log.info(f"DNS lookup for domain {peer_url} returned no A entry {e}")
                        except dns.resolver.LifetimeTimeout as e:
                            log.info(f"DNS lookup for A entry on domain {peer_url} timed out {e}")
                        if ipv4_entries:
                            peer_info = PeerInfo(ipv4_entries[0], peer_info_arg.port)
                        else:
                            log.info(f"DNS lookup for domain {peer_url} returned empty result")
                    except dns.resolver.NXDOMAIN as e:
                        log.info(f"DNS lookup for not existing domain {peer_url} failed {e}")
                log.info(f"Reconnecting to peer {peer_info}")
                try:
                    await server.start_client(peer_info, None, auth=auth)
                except Exception as e:
                    log.info(f"Failed to connect to {peer_info} {e}")
            await asyncio.sleep(3)

    return asyncio.create_task(connection_check())