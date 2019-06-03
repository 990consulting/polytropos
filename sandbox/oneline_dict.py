def f(x):
    return "A" * x

my_dict = {x: f(x) for x in range(10)}
print(my_dict)