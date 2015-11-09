from gurobipy import *

from tandem.base_tandem import Seater



class GurobiMixin(Seater):
    
    @classmethod
    def _table_lp_variable(cls, lower_bound, upper_bound, model):
        def _lp_variable(table):
            name = cls._hash_table(table)
            var = model.addVar(name=name,
                               vtype=GRB.BINARY)
            return var
        return _lp_variable
    
    @staticmethod
    def _solve_model(model):
        model.update()
        model.optimize()
       
    @staticmethod
    def _update_model(model):
        model.update()
        
    @staticmethod
    def _create_minimize_model(name):
        model = Model(name)
        model.modelSense = GRB.MINIMIZE
        return model
    
    @staticmethod
    def _solver_sum(iterable):
        return quicksum(iterable)
        
    @staticmethod
    def _add_objective_function(objective, model):
        model.setObjective(objective)
        return model
    
    @staticmethod
    def _add_constraint(constraint, name, model):
        model.addConstr(constraint, name)
        return model

    @staticmethod
    def _chosen_tables(variables, model):
        for language_table, var in variables.items():
            try:
                if var.x == 1.0:
                    yield language_table
            except GurobiError:
                pass
