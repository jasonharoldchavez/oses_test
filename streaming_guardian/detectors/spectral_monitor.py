import numpy as np
from .framework_core import AbstractDecisionLayer

class SpectralMonitorDetector(AbstractDecisionLayer):
    def __init__(self, num_nodes):
        self.n = num_nodes
        self.W = np.zeros((num_nodes, num_nodes))

    def update_edge(self, i, j, weight):
        """Updates the internal adjacency matrix for graph topology."""
        if 0 <= i < self.n and 0 <= j < self.n:
            self.W[i, j] = weight

    def update(self, raw_signal=None):
        """
        Computes the spectral gap of the transition matrix Laplacian.
        Fills the framework interface requirement.
        """
        out_deg = np.sum(self.W, axis=1)
        # Avoid division by zero for unlinked nodes
        out_deg[out_deg == 0] = 1e-9
        
        P = self.W / out_deg[:, None]
        L = np.eye(self.n) - P
        
        # Pure NumPy eigenvalues evaluation
        vals = np.linalg.eigvals(L)
        vals = np.sort(np.real(vals))
        
        spectral_gap = vals[1] if len(vals) > 1 else 0.0
        
        return {
            "spectral_gap": float(round(spectral_gap, 4)),
            "max_load": float(np.max(self.W)),
            "total_flow": float(np.sum(self.W))
        }
