import pulp

from tandem.base_tandem import Seater



class PulpMixin(Seater):
    
    @classmethod
    def _table_lp_variable(cls, lower_bound, upper_bound, model):
        def _lp_variable(table):
            name = cls._hash_table(table)
            return pulp.LpVariable(name,
                                   lowBound=lower_bound,
                                   upBound=upper_bound,
                                   cat=pulp.LpInteger)
        return _lp_variable 
    
    @staticmethod
    def _solve_model(model):
        model.solve()
        
    @staticmethod
    def _update_model(model):
        pass
        
    @staticmethod
    def _create_minimize_model(name):
        return pulp.LpProblem(name, pulp.LpMinimize)
    
    @staticmethod
    def _solver_sum(iterable):
        return pulp.lpSum(iterable)
        
    @staticmethod
    def _add_objective_function(objective, model):
        model += objective
        return model
    
    @staticmethod
    def _add_constraint(constraint, name, model):
        model += (constraint, name)
        return model
    
    @staticmethod
    def _chosen_tables(variables, model):
        for language_table, var in variables.items():
            if var.value() == 1.0:
                yield language_table