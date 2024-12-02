from ortools.sat.python import cp_model
import pandas as pd
import time
import csv


# Função para resolver o problema com uma estratégia específica
def read_project_file(file_path):
    project_info = {}
    precedence_df = pd.DataFrame(columns=["jobnr", "modes", "successors"])
    duration_resources_df = pd.DataFrame(columns=["jobnr", "mode", "duration", "R1", "R2", "R3", "R4"])
    resources = {}

    with open(file_path, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        line = line.strip()

        if line.startswith("#General Information"):
            project_info['projects'] = int(lines[i + 1].split(":")[1].strip())
            project_info['jobs'] = int(lines[i + 2].split(":")[1].strip().split()[0])
            project_info['horizon'] = int(lines[i + 3].split(":")[1].strip())

        elif line.startswith("#Precedence relations"):
            i += 2
            while lines[i].strip() != "************************************************************************":
                parts = list(map(int, lines[i].strip().split()))
                jobnr = parts[0]
                modes = parts[1]
                num_successors = parts[2]
                successors = parts[3:3 + num_successors]
                new_row = pd.DataFrame([{"jobnr": jobnr, "modes": modes, "successors": successors}])
                precedence_df = pd.concat([precedence_df, new_row], ignore_index=True)
                i += 1

        elif line.startswith("#Duration and resources"):
            i += 2
            while lines[i].strip() != "************************************************************************":
                parts = list(map(int, lines[i].strip().split()))
                jobnr, mode, duration = parts[:3]
                resources_values = parts[3:]
                while len(resources_values) < 4:
                    resources_values.append(0)
                new_row = pd.DataFrame([{
                    "jobnr": jobnr,
                    "mode": mode,
                    "duration": duration,
                    "R1": resources_values[0],
                    "R2": resources_values[1],
                    "R3": resources_values[2],
                    "R4": resources_values[3]
                }])
                duration_resources_df = pd.concat([duration_resources_df, new_row], ignore_index=True)
                i += 1

        elif line.startswith("#Resource availability"):
            i += 2
            while lines[i].strip() != "************************************************************************":
                resource, qty = lines[i].strip().split()
                resources[resource] = int(qty)
                i += 1

    return project_info, precedence_df, duration_resources_df, resources

# Função para gerar a tabela de cronograma
def generate_schedule_table(jobs, job_start_times, job_end_times, duration_resources_df, solver, horizon):
    table = []
    header = ["Job/Day"] + [str(day) for day in range(1, horizon + 1)]
    table.append(header)

    for job in jobs:
        row = [f"{job}"] + [" " for _ in range(horizon)]
        start = solver.Value(job_start_times[job]) + 1
        end = solver.Value(job_end_times[job]) + 1

        r1 = duration_resources_df.loc[duration_resources_df['jobnr'] == job, 'R1'].values[0]
        r2 = duration_resources_df.loc[duration_resources_df['jobnr'] == job, 'R2'].values[0]
        r3 = duration_resources_df.loc[duration_resources_df['jobnr'] == job, 'R3'].values[0]
        r4 = duration_resources_df.loc[duration_resources_df['jobnr'] == job, 'R4'].values[0]

        for time in range(start, end):
            resources_used = []
            if r1 > 0:
                resources_used.append("R1")
            if r2 > 0:
                resources_used.append("R2")
            if r3 > 0:
                resources_used.append("R3")
            if r4 > 0:
                resources_used.append("R4")

            if not resources_used:
                row[time] = "R0"
            else:
                row[time] = "+".join(resources_used)

        table.append(row)

    print(f"Schedule: Horizon = {horizon}, Makespan = {solver.ObjectiveValue()}\n")
    row_width = max(len(" | ".join(header)), len("| ".join(["---"] * len(header))))
    print("-" * row_width)
    for row in table:
        print("| " + " | ".join(f"{cell:^5}" for cell in row) + " |")
        print("-" * row_width)

# Função para resolver o problema com uma estratégia específica
def solve_project_scheduling(file_path, strategy):
    project_info, precedence_df, duration_resources_df, resources = read_project_file(file_path)
    model = cp_model.CpModel()
    jobs = duration_resources_df['jobnr'].tolist()
    job_start_times = {}
    job_end_times = {}
    horizon = project_info['horizon']

    for job in jobs:
        job_start_times[job] = model.NewIntVar(0, horizon, f"start_{job}")
        duration = duration_resources_df.loc[duration_resources_df['jobnr'] == job, 'duration'].values[0]
        job_end_times[job] = model.NewIntVar(0, horizon, f"end_{job}")
        model.Add(job_end_times[job] == job_start_times[job] + duration)

    for _, row in precedence_df.iterrows():
        job = row['jobnr']
        successors = row['successors']
        for successor in successors:
            model.Add(job_start_times[successor] >= job_end_times[job])

    interval_vars = []
    demands = {"R1": [], "R2": [], "R3": [], "R4": []}
    for job in jobs:
        start_var = job_start_times[job]
        duration = duration_resources_df.loc[duration_resources_df['jobnr'] == job, 'duration'].values[0]
        end_var = job_end_times[job]
        interval_var = model.NewIntervalVar(start_var, duration, end_var, f"interval_{job}")
        interval_vars.append(interval_var)

        for r in ["R1", "R2", "R3", "R4"]:
            r_needed = duration_resources_df.loc[duration_resources_df['jobnr'] == job, r].values[0]
            demands[r].append(r_needed)

    for r in ["R1", "R2", "R3", "R4"]:
        if r in resources:
            model.AddCumulative(interval_vars, demands[r], resources[r])

    makespan = model.NewIntVar(0, horizon, 'makespan')
    model.AddMaxEquality(makespan, [job_end_times[job] for job in jobs])
    model.Minimize(makespan)

    solver = cp_model.CpSolver()
    solver.parameters.search_branching = strategy

    start_time = time.time()
    status = solver.Solve(model)
    end_time = time.time()

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        result = {
            "Strategy": strategy,
            "WallTime": solver.WallTime(),
            "Conflicts": solver.NumConflicts(),
            "Branches": solver.NumBranches(),
            "Makespan": solver.ObjectiveValue(),
            "ProcessTime": end_time - start_time
        }

        job_start_times_values = {job: solver.Value(job_start_times[job]) for job in jobs}
        job_end_times_values = {job: solver.Value(job_end_times[job]) for job in jobs}
        return result, job_start_times_values, job_end_times_values, solver, project_info, duration_resources_df  # Retorna project_info também
    else:
        return None, None, None, None, None, None


# Função principal para executar e comparar estratégias
def main():
    file_path = input("Digite o caminho do arquivo: ").strip()
    output_csv = "performance_results.csv"

    strategies = {
        cp_model.AUTOMATIC_SEARCH: "AUTOMATIC_SEARCH",
        cp_model.FIXED_SEARCH: "FIXED_SEARCH",
        cp_model.PORTFOLIO_SEARCH: "PORTFOLIO_SEARCH"
    }

    all_results = []
    best_result = None
    best_solver = None
    best_job_start_times = None
    best_job_end_times = None
    best_project_info = None
    best_duration_resources_df = None

    # Armazenar os tempos de processamento para calcular a eficiência posteriormente
    min_process_time = float('inf')

    for strategy, strategy_name in strategies.items():
        print(f"Resolving using {strategy_name}...")
        result, job_start_times_values, job_end_times_values, solver, project_info, duration_resources_df = solve_project_scheduling(
            file_path, strategy)

        if result:
            result["Strategy"] = strategy_name
            all_results.append(result)

            # Atualiza o tempo de processamento mínimo
            min_process_time = min(min_process_time, result["ProcessTime"])

            # Calculando a eficiência para a estratégia atual
            if result["ProcessTime"] > 0:
                result["Efficiency"] = 100 * (min_process_time / result["ProcessTime"])
            else:
                result["Efficiency"] = 0  # Para evitar divisão por zero

            # Atualiza o melhor resultado com base no makespan, eficiência e tempo de processamento
            if best_result is None or (
                result["Makespan"] < best_result["Makespan"] or
                (result["Makespan"] == best_result["Makespan"] and result["Efficiency"] > best_result["Efficiency"]) or
                (result["Makespan"] == best_result["Makespan"] and result["Efficiency"] == best_result["Efficiency"] and result["ProcessTime"] < best_result["ProcessTime"])
            ):
                best_result = result
                best_solver = solver
                best_job_start_times = job_start_times_values
                best_job_end_times = job_end_times_values
                best_project_info = project_info
                best_duration_resources_df = duration_resources_df

    # Salva os resultados em um arquivo CSV
    with open(output_csv, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Strategy", "WallTime", "Conflicts", "Branches", "Makespan", "ProcessTime", "Efficiency"])
        for res in all_results:
            writer.writerow([
                res["Strategy"],
                round(res["WallTime"], 3),
                res["Conflicts"],
                res["Branches"],
                res["Makespan"],
                round(res["ProcessTime"], 3),
                round(res["Efficiency"], 1)
            ])

    if best_result and best_solver:
        print(f"\nMelhor Estratégia: {best_result['Strategy']}")
        print(
            f"Makespan: {best_result['Makespan']}, Tempo de Processamento: {best_result['ProcessTime']}s, Eficiência: {best_result['Efficiency']:.1f}%")
        print(f"Resultados completos salvos em: {output_csv}")
        generate_schedule_table(best_job_start_times.keys(), best_job_start_times, best_job_end_times,
                                best_duration_resources_df, best_solver, best_project_info['horizon'])



# Executando o programa principal
main()