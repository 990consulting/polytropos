def coro(input_arg):
    print("Starting coroutine with input argument of %i" % input_arg)
    value: int = (yield)  # Apparently, you have to use these parentheses -- why?
    print("The value is %i" % value)
    return value * input_arg


def middleman(input_arg, factor):
    print("Delegating to the coroutine")
    result = yield from coro(input_arg)
    print("The return value of the coroutine is %i" % result)
    return factor * result

print("Initializing the middleman")
the_middleman = middleman(7, 5)
next(the_middleman)

# If you call a coroutine from the outermost scope, you're going to have to handle StopIteration because you can't
# use "yield from" outside of a function
try:
    the_middleman.send(6)
except StopIteration as e:
    print("The return value of middleman is %i" % e.value)
