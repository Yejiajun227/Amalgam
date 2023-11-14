import inspect


class DecoratedAllMethod:
    """_summary_
    """
    def __init__(self, func):
        self.func = func

    def __get__(self, obj, cls=None):
        def wrapper(*args, **kwargs):
            print("decorate: before".center(50, '-'))
            try:
                # 实例方法
                ret = self.func(obj, *args, **kwargs)
            except TypeError:
                # 类方法或者静态方法
                ret = self.func(*args, **kwargs)
            print("decorate: after".center(50, '*'))
            return ret
        for attr in "__module__", "__name__", "__doc__":
            setattr(wrapper, attr, getattr(self.func, attr))
        return wrapper


class DecoratedInstanceMethod:

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, cls=None):
        def wrapper(*args, **kwargs):
            print("decorate instance method: before".center(50, '-'))

            ret = self.func(obj, *args, **kwargs)

            print("decorate instance method: after".center(50, '*'))
            return ret
        for attr in "__module__", "__name__", "__doc__":
            setattr(wrapper, attr, getattr(self.func, attr))
        return wrapper


class DecoratedClassMethod:

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, cls=None):
        def wrapper(*args, **kwargs):
            print("decorate class method: before")
            ret = self.func(*args, **kwargs)
            print("decorate class method: after")
            return ret
        for attr in "__module__", "__name__", "__doc__":
            setattr(wrapper, attr, getattr(self.func, attr))
        return wrapper


def decorate_class(cls, party=None):
    """decorate all functions and methods in class

    Returns:
        _type_: _description_
    """
    for name, meth in inspect.getmembers(cls):
        if inspect.ismethod(meth) or inspect.isfunction(meth):
            setattr(cls, name, DecoratedAllMethod(meth))

    return cls



# @decorate_class
class Person:

    def __init__(self, name):
        self.name = name
        print("__init__")

    def call(self):
        print(self.name)

    @staticmethod
    def speak(text):
        print(f"speak: {text}")

    @classmethod
    def eat(cls):
        print("eat...")


if __name__ == '__main__':
    # p = Person(name='张三')
    # p.call()
    # p.speak('hello world')
    # Person.speak('你好')
    # p.eat()
    # Person.eat()

    for name, meth in inspect.getmembers(Person):
        if inspect.ismethod(meth):
            print('method', name)
        elif inspect.isfunction(meth):
            print('function ', name)