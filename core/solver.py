import numpy as np
import random
import operator

from . import config
from .individual import Candidate, Fixed
from .population import Population
from .genetic_operators import Tournament, CXCrossover, mutate


class Sudoku(object):

    def __init__(self):
        self.given = None
        return

    def load(self, p_values):
        self.given = Fixed(p_values)
        return

    def solve(self, progress_callback=None):
        population_size_used = config.POPULATION_SIZE
        quant_elite_used = int(config.ELITE_PERCENTAGE * population_size_used)
        if quant_elite_used % 2 != 0 and (population_size_used - quant_elite_used) > 0:
            quant_elite_used = max(0, quant_elite_used - 1)

        num_generations_to_run = config.MAX_GENERATIONS
        mutation_rate = config.INITIAL_MUTATION_RATE

        reseed_count = 0

        default_return_metrics = {
            'generation': -1,
            'solution_candidate': None,
        }

        no_given = self.given is None or self.given.values is None
        if no_given or not self.given.no_duplicates():
            return default_return_metrics

        self.population = Population()
        seed_success = self.population.seed(population_size_used, self.given)
        if seed_success != 1:
            return default_return_metrics

        for generation_num in range(0, num_generations_to_run):
            self.population.update_fitness()
            all_fitness_values = [
                c.fitness for c in self.population.candidates
                if c.fitness is not None
            ]

            solution_found_candidate = None
            max_fitness = 0.0

            if all_fitness_values:
                max_fitness = np.max(all_fitness_values)
                if abs(max_fitness - 1.0) < 1e-9:
                    for idx, c_sol in enumerate(self.population.candidates):
                        has_fitness = c_sol.fitness is not None
                        fitness_is_one = (abs(c_sol.fitness - 1.0) < 1e-9
                                          if has_fitness else False)
                        fitness_ok = has_fitness and fitness_is_one
                        if fitness_ok:
                            no_zeros = not np.any(c_sol.values == 0)
                            valid = Fixed(c_sol.values).no_duplicates()
                            if no_zeros and valid:
                                solution_found_candidate = c_sol
                                solution_index = idx
                                break

            if progress_callback:
                self.population.sort()
                best_candidate_current_gen = (
                    self.population.candidates[0]
                    if self.population.candidates else None
                )
                total_individuals_current = (
                    (generation_num + 1) * population_size_used
                )
                should_continue = progress_callback(
                    generation_num,
                    best_candidate_current_gen,
                    total_individuals_current,
                    max_fitness
                )

                # Se o callback retornar False, cancelar a execução
                if should_continue is False:
                    return {
                        'generation': -3,
                        'solution_candidate': best_candidate_current_gen
                    }

            if solution_found_candidate:
                return {
                    'generation': generation_num,
                    'solution_candidate': solution_found_candidate
                }

            self.population.sort()

            tourney_selector = Tournament()

            pmx_crossover_op = CXCrossover()
            offspring_population = []

            parent_pool = self.population.candidates

            while len(offspring_population) < population_size_used:
                parent1 = tourney_selector.compete(parent_pool)
                parent2 = tourney_selector.compete(parent_pool)

                if parent1 is None or parent2 is None:
                    continue

                child1, child2 = pmx_crossover_op.crossover(parent1, parent2)

                if child1 is not None and child1.values is not None:
                    child1.update_fitness()
                    old_fitness_c1 = child1.fitness if child1.fitness is not None else -1.0
                    mutation_performed_c1 = mutate(child1, mutation_rate, self.given)
                    if mutation_performed_c1:
                        child1.update_fitness()
                    offspring_population.append(child1)

                if len(offspring_population) >= population_size_used:
                    break

                if child2 is not None and child2.values is not None:
                    child2.update_fitness()
                    old_fitness_c2 = child2.fitness if child2.fitness is not None else -1.0
                    mutation_performed_c2 = mutate(child2, mutation_rate, self.given)
                    if mutation_performed_c2:
                        child2.update_fitness()
                    offspring_population.append(child2)

            combined_population = self.population.candidates + offspring_population
            combined_population = sorted(
                [c for c in combined_population if c.fitness is not None],
                key=operator.attrgetter('fitness'),
                reverse=True
            )

            next_population_candidates = []

            num_elites = min(quant_elite_used, len(combined_population))
            next_population_candidates.extend(combined_population[:num_elites])

            tournament_pool = combined_population[num_elites:]

            num_to_select_from_tournament = (
                population_size_used - len(next_population_candidates)
            )

            for _ in range(num_to_select_from_tournament):
                if len(tournament_pool) < 2:
                    if tournament_pool:
                        next_population_candidates.append(tournament_pool.pop())
                    break

                participant1, participant2 = random.sample(tournament_pool, 2)

                winner = (
                    participant1
                    if participant1.fitness >= participant2.fitness
                    else participant2
                )

                next_population_candidates.append(winner)
                tournament_pool.remove(winner)

            idx_filler = 0
            while len(next_population_candidates) < population_size_used:
                if not combined_population:
                    break
                filler_candidate = Candidate()
                source_candidate = combined_population[idx_filler % len(combined_population)]
                if source_candidate.values is not None:
                    filler_candidate.values = np.copy(source_candidate.values)
                    filler_candidate.update_fitness()
                    next_population_candidates.append(filler_candidate)
                idx_filler += 1
                if idx_filler > 2 * population_size_used:
                    break

            if not next_population_candidates:
                if self.population.seed(population_size_used, self.given) != 1:
                    default_return_metrics.update({
                        'generation': -2,
                        'final_mutation_rate': mutation_rate,
                        'solution_index': -1
                    })
                    return default_return_metrics
            else:
                self.population.candidates = next_population_candidates

            if 'max_fitness' in locals() and max_fitness > 0:

                if all_fitness_values:
                    median_fitness = np.median(all_fitness_values)

                else:
                    median_fitness = 0

                amplitude_reduction = 1.0 - max_fitness

                upper_term = (1.0 - config.MEDIAN_FITNESS_UPPER_BOUND_RATIO)
                upper_factor = 1.0 - upper_term * amplitude_reduction
                upper_bound = max_fitness * upper_factor
                lower_term = (1.0 - config.MEDIAN_FITNESS_LOWER_BOUND_RATIO)
                lower_factor = 1.0 - lower_term * amplitude_reduction
                lower_bound = max_fitness * lower_factor

                if median_fitness > upper_bound:
                    mutation_rate += config.MUTATION_RATE_ADJUSTMENT_STEP
                elif median_fitness < lower_bound:
                    mutation_rate -= config.MUTATION_RATE_ADJUSTMENT_STEP

                mutation_rate = max(
                    config.MIN_MUTATION_RATE,
                    min(mutation_rate, config.MAX_MUTATION_RATE)
                )

        best_candidate_at_end = None

        if self.population.candidates:
            self.population.sort()
            best_candidate_at_end = self.population.candidates[0]
            has_candidate = best_candidate_at_end is not None
            has_values_attr = hasattr(best_candidate_at_end, 'values')
            values_not_none = (
                best_candidate_at_end.values is not None
                if has_candidate else False
            )
            if has_candidate and has_values_attr and values_not_none:
                fitness_one = abs(best_candidate_at_end.fitness - 1.0) < 1e-9
                no_zeros = not np.any(best_candidate_at_end.values == 0)
                valid = Fixed(best_candidate_at_end.values).no_duplicates()
                if not (fitness_one and no_zeros and valid):
                    pass
            else:
                best_candidate_at_end = None

        default_return_metrics.update({
            'generation': -2,
            'solution_candidate': best_candidate_at_end,
        })
        return default_return_metrics
