import os
import networkx as nx
from prettytable import PrettyTable
from time import time
import random as r

datasets={
        "car-f-92":32,
        "car-s-91":35,
        "ear-f-83":24,
        "hec-s-92":18,
        "kfu-s-93":20,
        "lse-f-91":18,
        "pur-s-93":42,
        "rye-s-93":23,
        "sta-f-83":13,
        "tre-s-92":23,
        "uta-s-92":35,
        "ute-s-92":10,
        "yor-f-83":21
    }

class Problem:
    def __init__(self):
        self.G=None
        self.periods_solutions=dict()
        self.existed_solutions=dict()
        self.problem_name=''
        self.P=-1
        self.temporary_period_view=dict()
        self.adj_matrix=list()

    def common_students(self,s1,s2):
        return len(s1.intersection(s2))
    
    def flush_all(self):
        self.G=None
        self.periods_solutions.clear()
        self.existed_solutions.clear()
        self.problem_name=''
        self.P=-1
        self.adj_matrix.clear()

    def load_problem(self,datasetname):
        self.flush_all()
        self.students=0
        self.problem_name=datasetname
        exams=dict()
        examid=-1
        datasetfile=os.path.join("","Datasets",datasetname+".stu")
        with open(datasetfile,"r") as RF:
            for line in RF:
                data=line.split()
                for exam in data:
                    examid=int(exam)
                    if examid in exams:
                        exams[examid].add(self.students)
                    else:
                        exams[examid]=set()
                        exams[examid].add(self.students)
                self.students+=1
        self.adj_matrix.append(list())
        for exam in exams:
            self.adj_matrix.append(list())
        for i in range(1,len(self.adj_matrix)):
            for j in range(0,len(self.adj_matrix)):
                self.adj_matrix[i].append(0)
        for i in range(1,len(self.adj_matrix)):
            for j in range(1,len(self.adj_matrix)):
                if i==j: continue
                self.adj_matrix[i][j]=self.common_students(exams[i],exams[j])
        self.exams=len(self.adj_matrix)-1
        self.create_graph()

    def conflict_density(self):
        cd=0
        for i in range(1,len(self.adj_matrix)):
            for j in range(1,len(self.adj_matrix)):
                if self.adj_matrix[i][j]!=0:
                    cd+=1
        return cd/self.exams**2
    
    def print_problem(self):
        print('Problem:{}'.format(self.problem_name))
        print('Students:{}'.format(self.students))
        print('Exams:{}'.format(self.exams))
        print('Conflict Density:{}'.format(self.conflict_density()))

    def create_graph(self):
        self.G=nx.Graph()
        self.G.add_nodes_from([examid for examid in range(1,self.exams)])
        for i in range(1,len(self.adj_matrix)):
            for j in range(1,len(self.adj_matrix)):
                if self.adj_matrix[i][j]>0:
                    self.G.add_edge(i,j,weight=self.adj_matrix[i][j])

    def load_solution(self):
        datasetspath=os.path.join('','Solutions',self.problem_name+".sol")
        with open(datasetspath,'r') as RF:
            for line in RF:
                data=line.split('\t')
                if len(data)!=2: continue
                self.existed_solutions[int(data[0])]=int(data[1])

    def preview_solution(self):
        self.load_solution()
        table=PrettyTable()
        table.field_names=['Exam','Period']
        table.add_rows([[exam,period] for exam,period in self.existed_solutions.items()])
        print(table)
        print('Feasibility:'+str(self.is_best_known_feasible()))

         
    def solve_problem(self):
        if self.G==None:
            print('Import a problem!!!!!')
            return
        self.periods_solutions=nx.greedy_color(self.G,strategy='DSATUR')
        table=PrettyTable()
        table.field_names=['Exam','Period']
        table.add_rows([[exam,period] for exam,period in self.periods_solutions.items()])
        print(table)
        self.P=max(self.periods_solutions.values())+1
        print('Dsatur:Periods Used:{}'.format(self.P))
        print('Period Number:{}-Invalid'.format(self.P)) if self.P<datasets[self.problem_name] else print('Period Number:{}-Valid'.format(self.P))

    def is_feasible_move(self,exam,period):
        for exam2 in self.G.neighbors(exam):
            if self.temporary_period_view[exam2]==period:
                return False
        return True

    def is_feasible(self):
        for exam in list(self.G.nodes):
            for neighbor in self.G.neighbors(exam):
                if self.periods_solutions[exam]==self.periods_solutions[neighbor]:
                    return False
        return True
    
    def is_best_known_feasible(self):
        if self.existed_solutions==dict(): return False
        for exam in list(self.G.nodes):
            for neighbor in list(self.G.neighbors(exam)):
                if self.existed_solutions[exam]==self.existed_solutions[neighbor]:
                    return False
        return True

    def execute_move(self):
        choice=['move_exam','swap_exams']
        randomly_selected_move=r.choice(choice)
        if randomly_selected_move=='move_exam':
            exam=r.choice([exam for exam in self.temporary_period_view])
            period=r.randint(0,self.P-1)
            if self.is_feasible_move(exam,period):
                return dict({exam:period})
        else:
            exam1=r.choice([exam for exam in self.temporary_period_view])
            exam2=r.choice([exam for exam in self.temporary_period_view])
            while exam1==exam2:
                exam2=r.choice([exam for exam in self.temporary_period_view])
            period1=self.temporary_period_view[exam2]
            period2=self.temporary_period_view[exam1]
            if period1==period2:
                return dict()
            if self.is_feasible_move(exam1,period1) and self.is_feasible_move(exam2,period2):
                return dict({exam1:period1,exam2:period2})
        return dict()
    
    def sol_file(self):
        with open(os.path.join('','Solutions',self.problem_name+'.sol'),'w') as F:
            F.write('Problem:{}\n'.format(self.problem_name))
            F.write('Periods used:{}\n'.format(self.P))
            F.write('=='*8+'\n')
            for exam,period in self.periods_solutions.items():
                F.write('{}:{}\n'.format(exam,period))

    def simulated_annealing(self):
        if self.G==None:
            print('First select 1.Import a problem!!')
            return
        temperature=1000.0
        start_temp=1000.0
        alpha=0.9999
        freeze=0.1
        best_sol=self.periods_solutions
        extime=int(input('Give simulated annealing execution time:'))
        start_timer=time()
        periods_dsatur_made=self.P
        print(periods_dsatur_made)
        self.temporary_period_view=self.periods_solutions.copy()
        while True:
            moves=self.execute_move()
            rollback=dict()
            for exam,period in moves.items():
                self.temporary_period_view[exam]=period
            periods_made=max(self.temporary_period_view.values())+1
            if periods_made<periods_dsatur_made:
                print('Solution improved|Periods used:{}|Temperature:{}'.format(periods_made,temperature))
                periods_dsatur_made=periods_made
                best_sol=self.temporary_period_view
            else:
                for exam,period in rollback.items():
                    self.temporary_period_view[exam]=period
            temperature*=alpha
            if temperature<freeze:
                temperature=start_temp*(r.randint(1,20)*0.1)
            if time()-start_timer>extime:
                break
        self.periods_solutions=best_sol
        table=PrettyTable()
        table.field_names=['Exam','Period']
        for exam,period in self.periods_solutions.items():
            table.add_row([exam,period])
        print(table)
        print('Periods used:{}\n'.format(self.P))

def menu():
    problem=Problem()
    ds=[dataset for dataset in datasets]
    while True:
        print("-"*10+" Uett "+"-"*10)
        print('1.Load Problem')
        print('2.Load Solutions')
        print('3.Solve the problem')
        print('4.Optimize the problem solution')
        print('5.Massive Solution')
        print('6.Exit')
        choice=int(input('Select:'))
        print('\n')
        if choice==1:
            counter=1
            for dataset in ds:
                print('{}.{}'.format(counter,dataset))
                counter+=1
            ch=int(input('select a dataset:'))
            problem.load_problem(ds[ch-1])
            print('\n')
            problem.print_problem()
        elif choice==2:
            problem.preview_solution()
        elif choice==3:
            problem.solve_problem()
        elif choice==4:
            problem.simulated_annealing()
        elif choice==5:
            for dataset in datasets:
                print('#Dataset:{}'.format(dataset))
                problem.load_problem(dataset)
                problem.solve_problem()
                problem.simulated_annealing()
        elif choice==6:
            break

if __name__=='__main__':
    menu()            

    
