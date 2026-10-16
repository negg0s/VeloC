"""
Unit tests for VeloC Stage 6 Block E: Distributed & Cluster Simulation
"""

import unittest
import sys
from pathlib import Path

ROOT_DIR = Path("D:/VeloC")
sys.path.insert(0, str(ROOT_DIR / "src"))

from cluster import DeterministicClusterSimulator

class TestBlockECluster(unittest.TestCase):
    def test_mpi_collectives(self):
        sim = DeterministicClusterSimulator(num_nodes=4)
        
        # 1. Bcast
        bcast_res = sim.mpi_bcast(root=0, data="model_weights_tensor")
        self.assertEqual(len(bcast_res), 4)
        self.assertTrue(all(x == "model_weights_tensor" for x in bcast_res))

        # 2. Allreduce Sum
        local_gradients = [1.5, 2.5, 3.0, 4.0]
        total_grad = sim.mpi_allreduce_sum(local_gradients)
        self.assertEqual(total_grad, 11.0)

        # 3. Scatter & Gather
        data = [10, 20, 30, 40, 50, 60, 70, 80]
        chunks = sim.mpi_scatter(root=0, full_list=data)
        self.assertEqual(len(chunks), 4)
        self.assertEqual(chunks[0], [10, 20])
        gathered = sim.mpi_gather(chunks)
        self.assertEqual(gathered, data)

    def test_raft_consensus_and_election(self):
        sim = DeterministicClusterSimulator(num_nodes=5)
        # Node 0 starts election
        elected = sim.run_election(candidate_id=0)
        self.assertTrue(elected)
        self.assertEqual(sim.nodes[0].state, "LEADER")

    def test_raft_network_partition_resilience(self):
        sim = DeterministicClusterSimulator(num_nodes=5)
        # Partition minority nodes (3 and 4)
        sim.partition([3, 4])
        # Node 0 in majority partition (0, 1, 2) can still win election (3 votes > 2.5)
        elected = sim.run_election(candidate_id=0)
        self.assertTrue(elected)
        self.assertEqual(sim.nodes[0].state, "LEADER")

        # Isolated minority candidate cannot win election
        sim.network_queue.clear()
        minority_elected = sim.run_election(candidate_id=3)
        self.assertFalse(minority_elected)

        # Heal partition
        sim.heal_partition()
        sim.network_queue.clear()
        self.assertEqual(len(sim.partitioned_nodes), 0)

if __name__ == "__main__":
    unittest.main()
