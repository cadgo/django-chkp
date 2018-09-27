from background_task import background

@background
def counttomil():
    for i in range(1000):
        print("Tarea programanada {}".format(i))