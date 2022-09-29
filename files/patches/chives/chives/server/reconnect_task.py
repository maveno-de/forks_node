import asyncio, dns.asyncresolver

from typing import Optional

from chives.server.server import ChivesServer
from chives.types.peer_info import PeerInfo
from chives.util.network import get_host_addr


def start_reconnect_task(server: ChivesServer, peer_info_arg: PeerInfo, log, auth: bool, prefer_ipv6: Optional[bool]):
    """
    Start a background task that checks connection and reconnects periodically to a peer.
    """
    # If peer_info_arg is already an address, use it, otherwise resolve it here.
    if peer_info_arg.is_valid(True):
        peer_info = peer_info_arg
        peer_url = ''
    else:
        peer_info = PeerInfo(get_host_addr(peer_info_arg, prefer_ipv6), peer_info_arg.port)
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
                    ipv6_entries = []
                    ipv4_entries = []
                    resolver = dns.asyncresolver.Resolver()
                    try:
                        try:
                            answers = await resolver.resolve(peer_url, 'AAAA', lifetime=3.0)
                            ipv6_entries = [str(an.to_text()) for an in answers]
                        except dns.resolver.NoAnswer as e:
                            log.info(f"DNS lookup for domain {peer_url} returned no AAAA entry {e}")
                        except dns.resolver.LifetimeTimeout as e:
                            log.info(f"DNS lookup for AAAA entry on domain {peer_url} timed out {e}")
                        try:
                            answers = await resolver.resolve(peer_url, 'A', lifetime=3.0)
                            ipv4_entries = [str(an.to_text()) for an in answers]
                        except dns.resolver.NoAnswer as e:
                            log.info(f"DNS lookup for domain {peer_url} returned no A entry {e}")
                        except dns.resolver.LifetimeTimeout as e:
                            log.info(f"DNS lookup for A entry on domain {peer_url} timed out {e}")
                        all_entries = ipv6_entries + ipv4_entries
                        if all_entries:
                            if ipv6_entries and (False if prefer_ipv6 is None else prefer_ipv6):
                                peer_address = ipv6_entries[0]
                            elif ipv4_entries and not (False if prefer_ipv6 is None else prefer_ipv6):
                                peer_address = ipv4_entries[0]
                            else:
                                peer_address = all_entries[0]
                            peer_info = PeerInfo(peer_address, peer_info_arg.port)
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