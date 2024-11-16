d = {"a": 123}

def add(d):
    d['b'] = 456

def modify_list(input_list):
    input_list[0] = 10  # Modify the first element
    input_list.append(20)  # Add a new element

my_list = [1, 2, 3]
modify_list(my_list)
modify_list(my_list)
modify_list(my_list)
modify_list(my_list)


print(my_list)  # Output will be [10, 2, 3, 20]

print(d)
add(d)
print(d)