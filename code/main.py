import argparse
import time
import eternity_puzzle
import solver_random
import solver_heuristic
import solver_local_search
import solver_advanced

def parse_arguments():
    parser = argparse.ArgumentParser()

    # Instances parameters
    parser.add_argument('--agent', type=str, default='random')
    parser.add_argument('--infile', type=str, default='input')
    parser.add_argument('--outfile', type=str, default='solution.txt')
    parser.add_argument('--visufile', type=str, default='visualization.png')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()


    e = eternity_puzzle.EternityPuzzle(args.infile)

    print("***********************************************************")
    print("[INFO] Start the solving Eternity II")
    print("[INFO] input file: %s" % args.infile)
    print("[INFO] output file: %s" % args.outfile)
    print("[INFO] visualization file: %s" % args.visufile)
    print("[INFO] board size: %s x %s" % (e.board_size,e.board_size))
    print("[INFO] solver selected: %s" % args.agent)
    print("***********************************************************")

    start_time = time.time()


    if args.agent == "random":
        # Take the best of 1,000,000 random trials
        solution, n_conflict = solver_random.solve_best_random(e, 100000)
    elif args.agent == "heuristic":
        # Agent based on a constructive heuristic (Phase 1)
        solution, n_conflict = solver_heuristic.solve_heuristic(e)
    elif args.agent == "local_search":
        # Agent based on a local search (Phase 2)
        solution, n_conflict = solver_local_search.solve_local_search(e)
    elif args.agent == "advanced":
        # Your nice agent (Phase 3 - main part of the project)
        solution, n_conflict = solver_advanced.solve_advanced(e)
    else:
        raise Exception("This agent does not exist")
    solving_time = round((time.time() - start_time) / 60,2)

    e.display_solution(solution,args.visufile)
    e.print_solution(solution, args.outfile)


    print("***********************************************************")
    print("[INFO] Solution obtained")
    print("[INFO] Execution time: %s minutes" % solving_time)
    print("[INFO] Number of conflicts: %s" % n_conflict)
    print("[INFO] Feasible solution: %s" % (n_conflict == 0))
    print("[INFO] Sanity check passed: %s" % e.verify_solution(solution))
    print("***********************************************************")
