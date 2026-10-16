"""
VeloC Distributed Cluster Simulation & Raft Consensus Engine
Implements MPI-style collectives (bcast, reduce, allreduce, scatter, gather)
and Deterministic Simulation Testing (DST) with Raft consensus.
"""

import time
import random
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class Packet:
    sender: int
    receiver: int
    msg_type: str
    term: int
    payload: Any
    deliver_time: float

class ClusterNode:
    def __init__(self, node_id: int, total_nodes: int):
        self.node_id = node_id
        self.total_nodes = total_nodes
        self.state = "FOLLOWER" # FOLLOWER, CANDIDATE, LEADER
        self.current_term = 0
        self.voted_for: Optional[int] = None
        self.log: List[Any] = []
        self.commit_index = 0
        self.peers = [i for i in range(total_nodes) if i != node_id]

    def handle_request_vote(self, candidate_id: int, term: int) -> bool:
        if term > self.current_term:
            self.current_term = term
            self.state = "FOLLOWER"
            self.voted_for = None
        
        if (self.voted_for is None or self.voted_for == candidate_id) and term >= self.current_term:
            self.voted_for = candidate_id
            return True
        return False

    def handle_append_entries(self, leader_id: int, term: int, entries: List[Any]) -> bool:
        if term >= self.current_term:
            self.current_term = term
            self.state = "FOLLOWER"
            self.log.extend(entries)
            return True
        return False

class DeterministicClusterSimulator:
    def __init__(self, num_nodes: int = 5):
        self.num_nodes = num_nodes
        self.nodes = [ClusterNode(i, num_nodes) for i in range(num_nodes)]
        self.network_queue: List[Packet] = []
        self.virtual_clock = 0.0
        self.partitioned_nodes: set = set()

    def partition(self, isolated_nodes: List[int]):
        self.partitioned_nodes = set(isolated_nodes)

    def heal_partition(self):
        self.partitioned_nodes.clear()

    def send_packet(self, sender: int, receiver: int, msg_type: str, term: int, payload: Any, delay: float = 0.01):
        if sender in self.partitioned_nodes or receiver in self.partitioned_nodes:
            # Dropped due to network partition!
            return
        pkt = Packet(sender, receiver, msg_type, term, payload, self.virtual_clock + delay)
        self.network_queue.append(pkt)
        self.network_queue.sort(key=lambda p: p.deliver_time)

    def step(self) -> bool:
        if not self.network_queue:
            return False
        pkt = self.network_queue.pop(0)
        self.virtual_clock = pkt.deliver_time
        receiver_node = self.nodes[pkt.receiver]

        if pkt.msg_type == "VOTE_REQ":
            granted = receiver_node.handle_request_vote(pkt.sender, pkt.term)
            self.send_packet(pkt.receiver, pkt.sender, "VOTE_RESP", pkt.term, granted)
        elif pkt.msg_type == "APPEND_REQ":
            ok = receiver_node.handle_append_entries(pkt.sender, pkt.term, pkt.payload)
            self.send_packet(pkt.receiver, pkt.sender, "APPEND_RESP", pkt.term, ok)
        return True

    def run_election(self, candidate_id: int) -> bool:
        candidate = self.nodes[candidate_id]
        candidate.state = "CANDIDATE"
        candidate.current_term += 1
        candidate.voted_for = candidate_id
        votes = 1

        for peer in candidate.peers:
            self.send_packet(candidate_id, peer, "VOTE_REQ", candidate.current_term, None)

        while self.network_queue:
            pkt = self.network_queue.pop(0)
            self.virtual_clock = pkt.deliver_time
            if pkt.msg_type == "VOTE_REQ":
                granted = self.nodes[pkt.receiver].handle_request_vote(pkt.sender, pkt.term)
                self.send_packet(pkt.receiver, pkt.sender, "VOTE_RESP", pkt.term, granted)
            elif pkt.msg_type == "VOTE_RESP" and pkt.receiver == candidate_id and pkt.payload is True:
                votes += 1

        if votes > self.num_nodes // 2:
            candidate.state = "LEADER"
            return True
        return False

    # MPI Collective Operations Emulation
    def mpi_bcast(self, root: int, data: Any) -> List[Any]:
        return [data for _ in range(self.num_nodes)]

    def mpi_allreduce_sum(self, local_vals: List[float]) -> float:
        assert len(local_vals) == self.num_nodes
        return sum(local_vals)

    def mpi_scatter(self, root: int, full_list: List[Any]) -> List[Any]:
        chunk_size = len(full_list) // self.num_nodes
        return [full_list[i * chunk_size : (i + 1) * chunk_size] for i in range(self.num_nodes)]

    def mpi_gather(self, chunks: List[List[Any]]) -> List[Any]:
        res = []
        for c in chunks:
            res.extend(c)
        return res
