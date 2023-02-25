from __future__ import annotations

import asyncio, dns.asyncresolver
from logging import Logger

from chia.server.server import ChiaServer
from chia.types.peer_info import PeerInfo

def start_reconnect_task(server: ChiaServer, peer_info: PeerInfo, log: Logger) -> asyncio.Task[None]:
    """
    Start a background task that checks connection and reconnects periodically to a peer.
    """

    async def connection_check() -> None:
        nonlocal peer_info
        while True:
            peer_retry = True
            for _, connection in server.all_connections.items():
                if connection.get_peer_info() == peer_info:
                    peer_retry = False
            if peer_retry:

                ipv6_entries = []
                ipv4_entries = []
                resolver = dns.asyncresolver.Resolver()
                try:
                    try:
                        answers = await resolver.resolve(peer_info.host, 'AAAA', lifetime=3.0)
                        ipv6_entries = [str(an.to_text()) for an in answers]
                    except dns.resolver.NoAnswer as e:
                        log.info(f"!! DNS lookup for domain {peer_info.host} returned no AAAA entry {e}")
                    except dns.resolver.LifetimeTimeout as e:
                        log.info(f"!! DNS lookup for AAAA entry on domain {peer_info.host} timed out {e}")
                    try:
                        answers = await resolver.resolve(peer_info.host, 'A', lifetime=3.0)
                        ipv4_entries = [str(an.to_text()) for an in answers]
                    except dns.resolver.NoAnswer as e:
                        log.info(f"!! DNS lookup for domain {peer_info.host} returned no A entry {e}")
                    except dns.resolver.LifetimeTimeout as e:
                        log.info(f"!! DNS lookup for A entry on domain {peer_info.host} timed out {e}")
                    all_entries = ipv6_entries + ipv4_entries
                    if all_entries:
                        peer_info = PeerInfo(all_entries[0], peer_info.port)
                    else:
                        log.info(f"!! DNS lookup for domain {peer_info.host} returned empty result")
                except dns.resolver.NXDOMAIN as e:
                    log.info(f"!! DNS lookup for not existing domain {peer_info.host} failed {e}")

                log.info(f"!! Reconnecting to peer {peer_info}")
                try:
                    await server.start_client(peer_info, None)
                except Exception as e:
                    log.info(f"Failed to connect to {peer_info} {e}")
            await asyncio.sleep(3)

    return asyncio.create_task(connection_check())