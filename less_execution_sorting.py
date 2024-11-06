import datetime
import random

# Generate a list of 10,000 random numbers
random_list = [random.randint(1, 10000) for _ in range(10000)]

# Record start time
start_time = datetime.datetime.now()
print("start_time", start_time)

# Print the original list (optional, as it can be very large)
# print(random_list)

# Sort the list in descending order using Python's built-in sorted() function
sorted_list = sorted(random_list, reverse=True)

# Record end time
end_time = datetime.datetime.now()
print("end_time", end_time)

# Print execution time
print("execution time", end_time - start_time)

# Print the sorted list (optional, as it can be very large)
print(sorted_list)
