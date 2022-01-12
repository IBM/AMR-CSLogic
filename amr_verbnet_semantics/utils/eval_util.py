"""
Utility functions for evaluation
"""
from collections import Counter, defaultdict


class Metric(object):
    def __init__(self):
        self.cnt_samples = 0
        self.cnt_samples_wo_true_triples = 0
        self.cnt_samples_wo_pred_triples = 0
        self.sum_prec = 0
        self.sum_recall = 0
        self.sum_f1 = 0
        self.rel_counter = Counter()
        self.true_triples_by_rel = defaultdict(set)
        self.pred_triples_by_rel = defaultdict(set)

    def compute_relationwise_metric(self):
        """
        compute relation-wise precision, recall and F1 scores
        :param true_triples_by_rel:
        :param pred_triples_by_rel:
        :return:
        """
        rel2metric = dict()
        for rel in self.true_triples_by_rel:
            true_triples = self.true_triples_by_rel[rel]
            if rel in self.pred_triples_by_rel:
                pred_triples = self.pred_triples_by_rel[rel]
            else:
                pred_triples = set()
            true_pred_triples = pred_triples.intersection(true_triples)
            if len(pred_triples) == 0:
                prec = 0
            else:
                prec = len(true_pred_triples) / len(pred_triples)
            if len(true_triples) == 0:
                recall = 0
            else:
                recall = len(true_pred_triples) / len(true_triples)
            if prec + recall > 0:
                f1 = 2 * prec * recall / (prec + recall)
            else:
                f1 = 0

            # use percentage points
            rel2metric[rel] = {
                "prec": prec * 100,
                "recall": recall * 100,
                "f1": f1 * 100
            }
        return rel2metric

