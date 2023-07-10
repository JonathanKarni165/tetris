mat1 = [[0,1,0,0],[0,1,1,1],[0,0,0,0],[0,0,0,0]]
mat2 = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
k = 0
for i in range(4):
    for j in range(4):
        print(k, ': ', mat2, '\n\n')
        k+=1
        mat2[j][i] = mat1[3-i][j]

input()
