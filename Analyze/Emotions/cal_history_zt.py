

def 


if __name__ == '__main__':
    import os
    files = os.listdir("./Data/history")
    files.sort()
    print(files)
    #依次计算
    points = []
    points5Days = []
    pointIndex = 0
    for file in files:
        # print(file)
        pointIndex += 1
        point = cal_history_point("./Data/history/"+file)