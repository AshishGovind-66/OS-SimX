import unittest
from src.scheduler import simulate_cpu
from src.memory import simulate_page_replacement
from src.deadlock import detect_deadlock, bankers_safe_sequence

class SimulatorTests(unittest.TestCase):
    def test_fcfs_metrics(self):
        result = simulate_cpu([
            {"pid":"P1","arrival":0,"burst":5},
            {"pid":"P2","arrival":1,"burst":3}
        ], "FCFS")
        by_pid = {p["pid"]: p for p in result["metrics"]}
        self.assertEqual(by_pid["P1"]["completion"], 5)
        self.assertEqual(by_pid["P2"]["waiting"], 4)

    def test_round_robin(self):
        result = simulate_cpu([
            {"pid":"P1","arrival":0,"burst":5},
            {"pid":"P2","arrival":1,"burst":3}
        ], "RR", 2)
        self.assertEqual(len(result["metrics"]), 2)
        self.assertEqual(result["total_time"], 8)

    def test_page_replacement(self):
        result = simulate_page_replacement([7,0,1,2,0,3,0,4,2,3], 3, "FIFO")
        self.assertEqual(result["faults"] + result["hits"], 10)

    def test_deadlock_no_deadlock(self):
        result = detect_deadlock([[1,0],[0,1]], [[0,1],[1,0]], [1,1])
        self.assertFalse(result["deadlock"])

    def test_bankers(self):
        result = bankers_safe_sequence([[0,1,0],[2,0,0],[3,0,2]],
                                       [[7,5,3],[3,2,2],[9,0,2]], [7,5,3])
        self.assertTrue(result["safe"])

if __name__ == "__main__":
    unittest.main()
