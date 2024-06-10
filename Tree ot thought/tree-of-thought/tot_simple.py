from langchain.llms import OpenAI
import openai
from typing import Tuple
from langchain_experimental.tot.checker import ToTChecker
from langchain_experimental.tot.thought import ThoughtValidity
import re
from langchain_experimental.tot.base import ToTChain
import os
from environs import Env
env = Env()
env.read_env()

os.getenv("OPENAI_API_KEY")

llm = OpenAI(temperature=1, max_tokens=512, model="text-davinci-003")

sudoku_puzzle =   "3,*,*,2|1,*,3,*|*,1,*,3|4,*,*,1"
sudoku_solution = "3,4,1,2|1,2,3,4|2,1,4,3|4,3,2,1"
problem_description = f"""
{sudoku_puzzle}

- This is a 4x4 Sudoku puzzle.
- The * represents a cell to be filled.
- The | character separates rows.
- At each step, replace one or more * with digits 1-4.
- There must be no duplicate digits in any row, column or 2x2 subgrid.
- Keep the known digits from previous valid thoughts in place.
- Each thought can be a partial or the final solution.
""".strip()
print(problem_description)

class MyChecker(ToTChecker):
    def evaluate(self, problem_description: str, thoughts: Tuple[str, ...] = ()) -> ThoughtValidity:
        last_thought = thoughts[-1]
        clean_solution = last_thought.replace(" ", "").replace('"', "")
        regex_solution = clean_solution.replace("*", ".").replace("|", "\\|")
        if sudoku_solution in clean_solution:
            return ThoughtValidity.VALID_FINAL
        elif re.search(regex_solution, sudoku_solution):
            return ThoughtValidity.VALID_INTERMEDIATE
        else:
            return ThoughtValidity.INVALID
        

tot_chain = ToTChain(llm=llm, checker=MyChecker(), k=30, c=5, verbose=True, verbose_llm=False)
tot_chain.run(problem_description=problem_description)    
