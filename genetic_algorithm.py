import random
import copy

# Define the problem parameters
activities = ["SLA100A", "SLA100B", "SLA191A", "SLA191B", "SLA201", "SLA291", "SLA303", "SLA304", "SLA394", "SLA449", "SLA451"]
rooms = ["Slater 003", "Roman 216", "Loft 206", "Roman 201", "Loft 310", "Beach 201", "Beach 301", "Logos 325", "Frank 119"]
facilitators = ["Lock", "Glen", "Banks", "Richards", "Shaw", "Singer", "Uther", "Tyler", "Numen", "Zeldin"]
times = ["10 AM", "11 AM", "12 PM", "1 PM", "2 PM", "3 PM"]

activity_enrollments = {
    "SLA100A": 50,
    "SLA100B": 50,
    "SLA191A": 50,
    "SLA191B": 50,
    "SLA201": 50,
    "SLA291": 50,
    "SLA303": 60,
    "SLA304": 25,
    "SLA394": 20,
    "SLA449": 60,
    "SLA451": 100
}

room_capacities = {
    "Slater 003": 45,
    "Roman 216": 30,
    "Loft 206": 75,
    "Roman 201": 50,
    "Loft 310": 108,
    "Beach 201": 60,
    "Beach 301": 75,
    "Logos 325": 450,
    "Frank 119": 60
}

preferred_facilitators = {}
other_facilitators = {}

activities_needing_preferred_facilitators = ["SLA100A", "SLA100B", "SLA191A", "SLA191B", "SLA201", "SLA291", "SLA303", "SLA304", "SLA394", "SLA449", "SLA451"]
activities_needing_other_facilitators = ["SLA100A", "SLA100B", "SLA191A", "SLA191B", "SLA201", "SLA291", "SLA303", "SLA304", "SLA394", "SLA449", "SLA451"]


for activity in activities_needing_preferred_facilitators:
    num_preferred_facilitators = random.randint(1, len(facilitators))
    preferred_facilitators[activity] = random.sample(facilitators, num_preferred_facilitators)


for activity in activities_needing_other_facilitators:
    num_other_facilitators = random.randint(1, len(facilitators))
    other_facilitators[activity] = random.sample(facilitators, num_other_facilitators)


facilitator_load = {
    "Glen": 3,
    "Lock": 2,
    "Banks": 4,
    "Richards": 1,
    "Shaw": 3,
    "Singer": 2,
    "Uther": 1,
    "Tyler": 5,
    "Numen": 3,
    "Zeldin": 2
}

room_building = {
    "Slater 003": "Slater",
    "Roman 216": "Roman",
    "Loft 206": "Loft",
    "Roman 201": "Roman",
    "Loft 310": "Loft",
    "Beach 201": "Beach",
    "Beach 301": "Beach",
    "Logos 325": "Logos",
    "Frank 119": "Frank"
}


population_size = 500

# Define the mutation rate (initially 0.01)
mutation_rate = 0.01

# Define the number of generations
num_generations = 100

# Define the termination condition threshold (1% improvement)
improvement_threshold = 0.01

# Function to initialize a random schedule
def initialize_schedule():
    schedule = {}
    for activity in activities:
        room = random.choice(rooms)
        time = random.choice(times)
        facilitator = random.choice(facilitators)
        schedule[activity] = {"room": room, "time": time, "facilitator": facilitator}
    return schedule

# Function to calculate the fitness of a schedule
def calculate_fitness(schedule):
    fitness = 0
    for activity, details in schedule.items():
        room = details["room"]
        time = details["time"]
        facilitator = details["facilitator"]

        # Start with a base fitness score
        activity_fitness = 0.0

        # Check if the activity is scheduled at the same time in the same room as another activity
        same_time_same_room_activities = [act for act, det in schedule.items() if det["room"] == room and det["time"] == time]
        if len(same_time_same_room_activities) > 1:
            activity_fitness -= 0.5

        # Calculate room size penalties
        expected_enrollment = activity_enrollments[activity]
        room_capacity = room_capacities[room]

        if room_capacity < expected_enrollment:
            activity_fitness -= 0.5
        elif room_capacity > 3 * expected_enrollment:
            activity_fitness -= 0.2
        elif room_capacity > 6 * expected_enrollment:
            activity_fitness -= 0.4
        else:
            activity_fitness += 0.3

        # Check if the activity is overseen by a preferred facilitator
        if facilitator in preferred_facilitators[activity]:
            activity_fitness += 0.5
        elif facilitator in other_facilitators[activity]:
            activity_fitness += 0.2
        else:
            activity_fitness -= 0.1

        # Facilitator load penalties
        time_slot_facilitators = [det["facilitator"] for act, det in schedule.items() if det["time"] == time]
        if time_slot_facilitators.count(facilitator) == 1:
            activity_fitness += 0.2
        elif time_slot_facilitators.count(facilitator) > 1:
            activity_fitness -= 0.2

        if facilitator_load[facilitator] > 4:
            activity_fitness -= 0.5
        elif facilitator_load[facilitator] in [1, 2] and facilitator != "Dr. Tyler":
            activity_fitness -= 0.4

        # Activity-specific adjustments
        if activity == "SLA101":
            sections_same_time = [act for act, det in schedule.items() if act == "SLA101" and det["time"] == time]
            if len(sections_same_time) == 2 and abs(sections_same_time.index(activity) - 1) == 1:
                activity_fitness += 0.5
            if len(sections_same_time) == 2 and abs(sections_same_time.index(activity) - 1) != 1:
                activity_fitness -= 0.5

        if activity == "SLA191":
            sections_same_time = [act for act, det in schedule.items() if act == "SLA191" and det["time"] == time]
            if len(sections_same_time) == 2 and abs(sections_same_time.index(activity) - 1) == 1:
                activity_fitness += 0.5
            if len(sections_same_time) == 2 and abs(sections_same_time.index(activity) - 1) != 1:
                activity_fitness -= 0.5

        if activity == "SLA191" and "SLA101" in sections_same_time:
            activities_at_consecutive_times = [act for act, det in schedule.items() if det["time"] == time or det["time"] == time - 1]
            if any(room_building[det["room"]] in ["Roman", "Beach"] for det in activities_at_consecutive_times):
                activity_fitness -= 0.4

        if activity == "SLA191" and "SLA101" in sections_same_time:
            activities_separated_by_1_hour = [act for act, det in schedule.items() if det["time"] == time - 2]
            if "SLA101" in activities_separated_by_1_hour:
                activity_fitness += 0.25

        if activity == "SLA191" and "SLA101" in sections_same_time:
            if "SLA101" in sections_same_time:
                activity_fitness -= 0.25

        # Add the activity's fitness to the total fitness
        fitness += activity_fitness

    return fitness


def selection(population, fitness_scores):
    selected_parents = []
    total_fitness = sum(fitness_scores)

    while len(selected_parents) < 2:  
        # Spin the roulette wheel
        spin = random.uniform(0, total_fitness)
        partial_sum = 0

        for i, fitness in enumerate(fitness_scores):
            partial_sum += fitness
            if partial_sum >= spin:
                selected_parents.append(copy.deepcopy(population[i]))
                break

    return selected_parents

# Function to perform crossover 
def crossover(parent1, parent2):
    child1 = {}
    child2 = {}
    crossover_point = random.randint(1, len(activities) - 1)  

    for i, activity in enumerate(activities):
        if i < crossover_point:
            child1[activity] = copy.deepcopy(parent1[activity])
            child2[activity] = copy.deepcopy(parent2[activity])
        else:
            child1[activity] = copy.deepcopy(parent2[activity])
            child2[activity] = copy.deepcopy(parent1[activity])

    return child1, child2

# Function to perform mutation
def mutate(schedule):
    if random.random() < mutation_rate:
        
        activity_to_mutate = random.choice(activities)
        mutation_type = random.choice(["room", "time", "facilitator"])

        
        if mutation_type == "room":
            new_room = random.choice(rooms)
            schedule[activity_to_mutate]["room"] = new_room
        elif mutation_type == "time":
            new_time = random.choice(times)
            schedule[activity_to_mutate]["time"] = new_time
        elif mutation_type == "facilitator":
            new_facilitator = random.choice(facilitators)
            schedule[activity_to_mutate]["facilitator"] = new_facilitator

    return schedule

def genetic_algorithm():
    print("Running the genetic algorithm...")
    # Initialize the population with random schedules
    population = [initialize_schedule() for _ in range(population_size)]

    # Main loop for the specified number of generations
    for generation in range(num_generations):
        # Calculate the fitness of each schedule in the population
        fitness_scores = [calculate_fitness(schedule) for schedule in population]

        # Selection (Roulette Wheel Selection)
        new_population = []

        while len(new_population) < population_size:
            parents = selection(population, fitness_scores)

            # Crossover
            child1, child2 = crossover(parents[0], parents[1])

            # Mutation
            child1 = mutate(child1)
            child2 = mutate(child2)

            new_population.extend([child1, child2])

        # Update the population with the new generation
        population = copy.deepcopy(new_population)

        # Termination condition check
        if generation > 0:
            avg_fitness = sum(fitness_scores) / population_size
            prev_avg_fitness = sum(prev_fitness_scores) / population_size
            improvement = (prev_avg_fitness - avg_fitness) / prev_avg_fitness

            if improvement < improvement_threshold:
                break

        # Store the fitness scores for the next generation
        prev_fitness_scores = fitness_scores

    # Find the best schedule in the final population
    best_schedule_index = fitness_scores.index(max(fitness_scores))
    best_schedule = population[best_schedule_index]

    # Output the best schedule
    print("Best Schedule (Fitness Score: {})".format(fitness_scores[best_schedule_index]))
    for activity, details in best_schedule.items():
        print(f"Activity: {activity}, Room: {details['room']}, Time: {details['time']}, Facilitator: {details['facilitator']}")

    # Implement code to save the best schedule to a file

if __name__ == "__main__":
    genetic_algorithm()
