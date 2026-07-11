import numpy as np
from .framework_core import AbstractDecisionLayer

class CorrelationSubspaceDetector(AbstractDecisionLayer):
    def __init__(self, subspace_dim=2, similarity_threshold=0.85):
        self.k = subspace_dim
        self.similarity_threshold = similarity_threshold
        self.fault_dictionary = {}
        self.fault_id_counter = 0
        self.Pn = None

    def _get_subspace(self, X):
        Xc = X - np.mean(X, axis=0)
        _, _, Vt = np.linalg.svd(Xc, full_matrices=False)
        return Vt[:self.k].T

    def _projection_matrix(self, V):
        return V @ V.T

    def _residual_signature(self, X, P):
        Xc = X - np.mean(X, axis=0)
        R = Xc @ (np.eye(X.shape[1]) - P)
        cov = (R.T @ R) / (X.shape[0] - 1)
        # Using pure numpy linalg instead of scipy
        eigvals, eigvecs = np.linalg.eigh(cov)
        return eigvecs[:, -1]

    def _cosine_similarity(self, a, b):
        return np.abs(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def calibrate(self, baseline_stream):
        baseline = baseline_stream[:50].reshape(-1, baseline_stream.shape[-1])
        Vn = self._get_subspace(baseline)
        self.Pn = self._projection_matrix(Vn)

    def update(self, window_data):
        if self.Pn is None:
            raise ValueError("Detector must be calibrated with a baseline stream first.")
            
        Vc = self._get_subspace(window_data)
        Pc = self._projection_matrix(Vc)
        sig = self._residual_signature(window_data, self.Pn)
        
        if np.linalg.norm(sig) < 1e-6:
            return {"status": "NOMINAL", "matched_fault": None, "score": 1.0}
            
        matched = None
        best_score = 0
        
        for fid, ref in self.fault_dictionary.items():
            score = self._cosine_similarity(sig, ref)
            if score > best_score:
                best_score = score
                matched = fid
                
        if best_score > self.similarity_threshold:
            return {"status": "MATCHED_FAULT", "matched_fault": matched, "score": float(best_score)}
        else:
            self.fault_id_counter += 1
            fid = f"FAULT_{self.fault_id_counter:02d}"
            self.fault_dictionary[fid] = sig
            return {"status": "NEW_FAULT_REGISTERED", "matched_fault": fid, "score": float(best_score)}
