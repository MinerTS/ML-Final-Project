import math

with open('glass.txt', 'r') as file:
    lines = file.readlines()
# 自定義column name
column_names = ['Id number', 'RI', 'Na', 'Mg', 'Al', 'Si', 'K', 'Ca', 'Ba', 'Fe','Type of glass']
Attributes = [0,1,2,3,4,5,6,7,8]
# 初始化字典
raw_data = []
Ground_tru = []

for line in lines:
    row = line.strip().split(',')
    Ground_tru.append(row.pop(10))
    if len(row) == len(Attributes)+1:
            instance = dict(zip(Attributes, row[1:]))
            raw_data.append(instance)

def probability(data) -> float:   #計算類別資料發生率公式
    total_samples = len(data)
    class_counts = {}
   
    for value in data:
        if value[1] in class_counts:
            class_counts[str(value[1])] += 1
        else:
            class_counts[str(value[1])] = 1

    prob = {key: counts / total_samples for key, counts in class_counts.items()}

    return prob

def H_entropy(data):   # 計算Entropye公式_H(X),H(Y)
    probs = probability(data)
    probs_values = [prob[1] for prob in probs.items()] # 抽出字典value到list中，[0]是key [1]是value


    entropy_value = -sum(p * math.log2(p) for p in probs_values)
    return entropy_value

def EntropyBased(Sorted_value, Splitting_point: list , min_value = 0, max_value = 0):
    currentBestGain = 0
    currentBestPoint = 0
    criterion = 0
    values_P = []

    if len(Splitting_point) == 0:
        values_P = sorted(Sorted_value)
        max_value = values_P[-1][0] + 1  # max
        min_value = values_P[0][0]  # min
    else:
        for sub_idx in Sorted_value:
            if min_value <= sub_idx[0] < max_value:
                values_P.append(sub_idx)
  
    Entropy_P = H_entropy(values_P)

    candidates_list = set()
    for i in range(len(values_P) - 1):  # construct the candidate list
        candidates_list.add(round((values_P[i][0] + values_P[i + 1][0]) / 2, 8))
    candidates_list = sorted(candidates_list)

    currentS1 = []
    currentS2 = []

    for point in candidates_list:
        S1 = []
        S2 = []
        for i in range(len(values_P)):
            if values_P[i][0] < point:
                S1.append(values_P[i])
            else:
                S2.append(values_P[i])
        X = (len(S1)/len(values_P)) * H_entropy(S1)
        Y = (len(S2)/len(values_P)) * H_entropy(S2)
        currentGain = Entropy_P - (X + Y)
        if currentGain > currentBestGain:
            currentBestGain = currentGain
            currentBestGain_idx = len(S1)
            currentBestPoint = point
            currentS1 = S1
            currentS2 = S2
    S = len(values_P)   # 計算criterion是否符合MPL priciple，符合再下切
    currentX = H_entropy(currentS1)
    currentY = H_entropy(currentS2)
    k = len(set(values_P[j][1] for j in range(len(values_P))))
    k1 = len(set(currentS1[m][1] for m in range(len(currentS1))))
    k2 = len(set(currentS2[n][1] for n in range(len(currentS2))))
    criterion = math.log2(S - 1) / S + (math.log2(3 ** k - 2) - (k * Entropy_P - k1 * currentX - k2 * currentY)) / S
    if currentBestGain - criterion > 0:
        Splitting_value = currentBestPoint
        Splitting_point.append(Splitting_value)
        EntropyBased(Sorted_value, Splitting_point = Splitting_point, min_value = min_value, max_value = Splitting_value)
        EntropyBased(Sorted_value, Splitting_point = Splitting_point, min_value = Splitting_value, max_value = max_value)


discretized_row = []
discr_ent_data = []  #Ent_B後的資料，List包含Dict裡面的value為str

# 循环处理每个属性
for class_selected in Attributes:  # 跳过第一个和最后一个列名
    attrTodis = [float(row[class_selected]) for row in raw_data]
    valuesTodis = list(zip(attrTodis, Ground_tru))

    Splitting_list = []
    EntropyBased(valuesTodis, Splitting_point = Splitting_list)
    Splitting_list.append(min(attrTodis))
    Splitting_list.append(max(attrTodis))
    Splitting_list.sort()

    discr_ent_str = []  # 開使做value mapping
    if len(Splitting_list) > 2:
        for value in attrTodis:
            for internvl in range(len(Splitting_list) - 1):
                if Splitting_list[internvl] <= value < Splitting_list[internvl + 1]:
                    discr_ent_str.append(str(internvl + 1))
            if value == max(attrTodis):
                discr_ent_str.append(str(len(Splitting_list) - 1))

    else:
        for i in range(len(attrTodis)):
            discr_ent_str.append(str(1))
    discretized_row.append(discr_ent_str)



    class_name = column_names[Attributes[class_selected] + 1]  # 获取类别名称
    print(f"Splitting Points(include Max. and Min.) for {class_name}:{Splitting_list}")

for values in zip(*discretized_row):
    discretized_dict = {key: value for key, value in zip(Attributes, values)}
    discr_ent_data.append(discretized_dict)
