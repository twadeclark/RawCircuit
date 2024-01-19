import random

class IntegerArray:
    def __init__(self):
        self.thread_array = []

    def add(self, item1, item2):
        if isinstance(item1, int) and isinstance(item2, int):
            self.thread_array.append([item1, item2])
        else:
            print("Both items must be integers.")

TOTAL_COMMENTS = 20
MULTIPLER = 3

array = IntegerArray()
array.add(0, 0)

for i in range(1, TOTAL_COMMENTS):
    d = (len(array.thread_array) - 1) * MULTIPLER
    r = random.randint(0, int(d))
    if r > len(array.thread_array) - 1:
        r = len(array.thread_array) - 1
    # print("i:", i, "d:", d, "r:", r)
    array.add(i, r)

indent = 0
last = 0
# subtractor = 0

for item in array.thread_array:
    # for i in range(0, item[1]):
    #     print(" ", end="")
    # print(item)


    if item[0] == item[1] + 1:
        indent += 1
    else:
        indent = max(0, indent - 1)


    for i in range(0, indent):
        print(" ", end="")
    print(item)
    last = item[1]

    # if item[1] + 1 == last:
    #     indent += 1
    # else:
    #     indent = item[1]
    # for i in range(0, indent):
    #     print(" ", end="")
    # print(item)
    # last = item[1]

    # if item[1] > 0:
    #     if item[1] != array.array[item[0] - 1][0]:
    #         subtractor += (item[1] - subtractor)
    # for i in range(0, item[1] - subtractor):
    #     print(" ", end="")
    # print(item, subtractor, item[1], array.array[item[0] - 1][0])



# print the number of times each integer appears in the second item of each array item
# for i in range(0, len(array.array)):
#     count = 0
#     for item in array.array:
#         if item[1] == i:
#             count += 1
#     if count > 0:
#         print(i, ":", count)
