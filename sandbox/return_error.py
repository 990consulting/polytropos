def get_error() -> BaseException:
    return ValueError("Hi there, I'm a ValueError")

x = get_error()
print("I've retrieved the exception, but right now. I'm fine. Here is its __repr__:")
print(x)
input("Press return to raise an exception")
raise x
