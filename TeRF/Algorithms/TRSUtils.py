# def log_p(self, typesystem, p_rule):
#     p_n_rules = stats.geom.logpmf(len(self.clauses)+1, p=p_rule)
#     p_rules = sum(rule.log_p(typesystem, self.rule_type)
#                   for rule in self)
#     return p_n_rules + p_rules
